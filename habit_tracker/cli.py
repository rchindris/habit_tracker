import click
from datetime import date

from rich.console import Console
from rich.table import Table

from habit_tracker.models import Habit, Periodicity
from habit_tracker.tracker import HabitTracker
from habit_tracker.repositories import SqlHabitRepository
from habit_tracker.exceptions import HabitStoreException
console = Console()

# Create a group for all commands
@click.group()
def cli():
    """Habit Tracker CLI"""
    pass


@cli.command()
@click.argument("name")
@click.option("--description", prompt="Description",
              help="The description of the habit.")
@click.option("--periodicity", prompt="Periodicity",
              type=click.Choice(["daily", "weekly", "monthly"]),
              default="daily",
              help="The periodicity of the habit.")
@click.option('--start-date',
              prompt='Start date (YYYY-MM-DD)',
              type=click.DateTime(formats=["%Y-%m-%d"]),
              default=date.strftime(date.today(), "%Y-%m-%d"),
              help='The start date of the habit.')
@click.option('--db', default='habits.sqlite', help='Database file to use.')
def create(name, description, periodicity, start_date, db):
    """Create a new habit."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    habit = Habit(
        name=name, description=description, 
        periodicity=periodicity, start_date=start_date
    )

    try:
        created_habit = tracker.create(habit)
        console.print(f"[bold green]Created habit '{created_habit.name}'[/bold green]")
    except HabitStoreException as e:
        console.print(f"[bold red]Failed to create habit: {e}[/bold red]")

@cli.command()
@click.argument("name", required=True)
@click.option('--db', default='habits.sqlite', help='Database file to use.')
def delete(name, db):
    """Delete an existing habit."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    if tracker.delete(Habit(id=id, name=name)):
        console.print(f"[bold green]Habit '{name}' deleted.[/bold green]")
    else:
        console.print(f"[bold red]Failed to delete habit '{name}'[/bold red]")

@cli.command()
@click.option("--periodicity", 
              type=click.Choice(["daily", "weekly", "monthly", "all"]), 
              help="Filter habits by periodicity.",
              default="all")
@click.option('--db', default='habits.sqlite', help='Database to use.')
def list(periodicity, db):
    """List all habits, optionally filtered by periodicity."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    habits = tracker.get_habits(periodicity=periodicity if periodicity != "all" else None)
    table = Table(title="Habits")
    table.add_column("Name", style="bold")
    table.add_column("Periodicity")
    table.add_column("Start Date")
    table.add_column("Last Checked Off")
    
    for habit in habits:
        last_check_off = habit.check_off_log[-1].date if habit.check_off_log else "Never"
        table.add_row(
            habit.name, str(habit.periodicity), 
            str(habit.start_date), str(last_check_off)
        )
        
    console.print(table)


@cli.command()
@click.argument("name", required=True)
@click.option('--db', default='habits.sqlite', help='Database to use.')
def check_off(name, db):
    """Check off a habit."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    try:
        tracker.check_off(name)
        console.print(f"[bold green]Checked off habit {name}[/bold green]")
    except HabitStoreException as e:
        console.print(f"[bold red]Failed to check off habit: {e}[/bold red]")

if __name__ == "__main__":
    cli()
