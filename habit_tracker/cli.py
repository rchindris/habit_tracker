"""Command line interface for the habit tracker."""
import click
from datetime import date

from rich.console import Console
from rich.table import Table

from habit_tracker.models import Habit, Periodicity, HabitStatus
from habit_tracker.tracker import HabitTracker
from habit_tracker.repositories import SqlHabitRepository
from habit_tracker.exceptions import HabitStoreException
from habit_tracker import analytics

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
@click.option('--force', is_flag=True, help='Force deletion without confirmation.')
def delete(name, db, force):
    """Delete an existing habit."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    if not tracker.habit_exists(name):
        console.print(f"[bold red]Habit '{name}' not found[/bold red]")
        return

    if not force:
        confirm = click.confirm(f"Are you sure you want to delete habit '{name}'?")
        if not confirm:
            console.print(f"[bold red]Aborted deletion of habit '{name}'[/bold red]")
            return

    if tracker.delete(name):
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

    # Get habits using analytics module
    all_habits = tracker.get_habits(None)
    if periodicity != "all":
        habits = analytics.get_habits_by_periodicity(all_habits, Periodicity(periodicity))
    else:
        habits = analytics.get_all_habits(all_habits)

    if not habits:
        console.print("[yellow]No habits found[/yellow]")
        return

    table = Table(title="Habits")
    table.add_column("Name", style="bold")
    table.add_column("Description", style="italic")
    table.add_column("Periodicity")
    table.add_column("Start Date")
    table.add_column("Last Check-off")
    table.add_column("Status", justify="center")

    for habit in habits:
        last_check_off = habit.check_off_log[-1].date if habit.check_off_log else "Never"
        status, _ = analytics.get_habit_status(habit)
        status_display = {
            HabitStatus.STREAK: "[green]Streak[/green]",
            HabitStatus.PENDING: "[yellow]Pending[/yellow]",
            HabitStatus.BROKEN: "[red]Broken[/red]"
        }[status]

        table.add_row(
            habit.name,
            habit.description,
            str(habit.periodicity),
            str(habit.start_date),
            str(last_check_off),
            status_display
        )

    console.print(table)


@cli.command('check-off')
@click.argument("name", required=True)
@click.option('--db', default='habits.sqlite', help='Database to use.')
@click.option('--date',
              prompt='Date (YYYY-MM-DD)',
              type=click.DateTime(formats=["%Y-%m-%d"]),
              default=date.strftime(date.today(), "%Y-%m-%d"))
def check_off(name, db, date):
    """Check off a habit."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    if tracker.check_off(name, date.date()):
        console.print(f"[bold green]Checked off habit {name}[/bold green]")
    else:
        console.print(f"[bold red]Failed to check off habit {name}[/bold red]")


@cli.command()
@click.option('--db', default='habits.sqlite', help='Database to use.')
@click.option("--periodicity",
              type=click.Choice(["daily", "weekly", "monthly", "all"]),
              help="Filter habits by periodicity.",
              default="all")
def streaks(db, periodicity):
    """Show streak information for all habits."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    # Get habits using analytics module
    all_habits = tracker.get_habits(None)
    if periodicity != "all":
        habits = analytics.get_habits_by_periodicity(all_habits, Periodicity(periodicity))
    else:
        habits = analytics.get_all_habits(all_habits)

    if not habits:
        console.print("[yellow]No habits found[/yellow]")
        return

    # Create streak table
    table = Table(title="Habit Streaks")
    table.add_column("Habit", style="bold")
    table.add_column("Longest Streak")
    table.add_column("Completion Rate")
    table.add_column("Periodicity")

    # Add habit streaks
    for habit in habits:
        longest_streak = analytics.get_longest_streak_for_habit(habit)
        completion_rate = analytics.get_habit_completion_rate(habit)

        table.add_row(
            habit.name,
            str(longest_streak),
            f"{completion_rate:.1f}%",
            str(habit.periodicity)
        )

    console.print(table)

    # Show overall longest streak
    longest_habit, longest_streak = analytics.get_longest_streak_all_habits(habits)
    if longest_streak > 0:
        console.print(
            f"\n[bold green]Longest streak: {longest_streak} by '{longest_habit}'[/bold green]"
        )


@cli.command()
@click.option("--periodicity",
              type=click.Choice(["daily", "weekly", "monthly", "all"]),
              help="Filter habits by periodicity.",
              default="all")
@click.option('--db', default='habits.sqlite', help='Database to use.')
def show_broken(periodicity, db):
    """Show broken habits (not checked off in their last period)."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    # Get habits using analytics module
    all_habits = tracker.get_habits(None)
    if periodicity != "all":
        habits = analytics.get_habits_by_periodicity(all_habits, Periodicity(periodicity))
    else:
        habits = analytics.get_all_habits(all_habits)

    if not habits:
        console.print("[yellow]No habits found[/yellow]")
        return

    # Filter habits that need attention (broken or pending)
    attention_habits = []
    for habit in habits:
        status, last_check_off = analytics.get_habit_status(habit)
        if status in (HabitStatus.BROKEN, HabitStatus.PENDING):
            attention_habits.append((habit, status, last_check_off))

    if not attention_habits:
        console.print("[green]No habits need attention! Keep up the good work![/green]")
        return

    # Create table for habits needing attention
    table = Table(title="Habits Needing Attention")
    table.add_column("Habit", style="bold")
    table.add_column("Periodicity")
    table.add_column("Last Check-off")
    table.add_column("Days Since", justify="right")
    table.add_column("Status", justify="center")

    today = date.today()
    for habit, status, last_check_off in attention_habits:
        days_since = (today - last_check_off).days if last_check_off else "Never"
        status_display = {
            HabitStatus.PENDING: "[yellow]Pending[/yellow]",
            HabitStatus.BROKEN: "[red]Broken[/red]"
        }[status]

        table.add_row(
            habit.name,
            str(habit.periodicity),
            str(last_check_off) if last_check_off else "Never",
            str(days_since),
            status_display
        )

    console.print(table)
    console.print(f"\n[yellow]Found {len(attention_habits)} habit(s) needing attention[/yellow]")


@cli.command()
@click.argument('habit_name')
@click.option('--db', default='habits.sqlite', help='Database to use.')
def show(habit_name, db):
    """Show detailed information for a specific habit."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    habit = tracker.get_habit(habit_name)
    if not habit:
        console.print(f"[bold red]Habit '{habit_name}' not found[/bold red]")
        return

    # Create analytics table
    table = Table(title=f"Statistics for '{habit.name}'")
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    # Add metrics
    longest_streak = analytics.get_longest_streak_for_habit(habit)
    status, last_check_off = analytics.get_habit_status(habit)

    status_display = {
        HabitStatus.STREAK: "[green]Streak[/green]",
        HabitStatus.PENDING: "[yellow]Pending[/yellow]",
        HabitStatus.BROKEN: "[red]Broken[/red]"
    }[status]

    table.add_row("Periodicity", str(habit.periodicity))
    table.add_row("Start Date", str(habit.start_date))
    table.add_row("Days Tracked", str((date.today() - habit.start_date).days))
    table.add_row("Times Completed", str(len(habit.check_off_log)))
    table.add_row("Longest Streak", str(longest_streak))
    table.add_row("Status", status_display)
    if last_check_off:
        table.add_row("Last Check-off", str(last_check_off))

    console.print(table)
    console.print(
        "\n[blue]Tip:[/blue] Use [italic]poetry run habit history",
        f'"{habit_name}"[/italic] to see check-off history.'
    )


@cli.command()
@click.argument('habit_name')
@click.option('--db', default='habits.sqlite', help='Database to use.')
def history(habit_name, db):
    """Show check-off history for a specific habit."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    habit = tracker.get_habit(habit_name)
    if not habit:
        console.print(f"[bold red]Habit '{habit_name}' not found[/bold red]")
        return

    if habit.check_off_log:
        # Create check-off log table
        table = Table(title=f"Check-off History for '{habit.name}'")
        table.add_column("Date", style="cyan")
        table.add_column("Days Ago", justify="right")

        # Sort check-offs by date, most recent first
        sorted_check_offs = sorted(
            habit.check_off_log,
            key=lambda co: co.date,
            reverse=True
        )

        today = date.today()
        for check_off in sorted_check_offs:
            days_ago = (today - check_off.date).days
            days_text = "Today" if days_ago == 0 else (
                "Yesterday" if days_ago == 1 else f"{days_ago} days ago"
            )
            table.add_row(
                str(check_off.date),
                days_text
            )

        console.print(table)
        console.print(f"\n[green]Total check-offs: {len(habit.check_off_log)}[/green]")
    else:
        console.print("\n[yellow]No check-offs recorded yet.[/yellow]")


if __name__ == "__main__":
    cli()
