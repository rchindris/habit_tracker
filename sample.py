#!/usr/bin/env python3
"""Sample data initialization script for the Habit Tracker.

This script creates a set of sample habits in the database for testing
and demonstration purposes.
"""
import click
from datetime import date, timedelta
from random import randint

from habit_tracker.models import Habit, Periodicity
from habit_tracker.tracker import HabitTracker
from habit_tracker.repositories import SqlHabitRepository


SAMPLE_HABITS = [
    # Daily habits
    {
        "name": "Morning Exercise",
        "description": "30 minutes of morning workout",
        "periodicity": Periodicity.DAILY,
        "start_date": date.today() - timedelta(days=30)
    },
    {
        "name": "Read Book",
        "description": "Read at least 30 minutes",
        "periodicity": Periodicity.DAILY,
        "start_date": date.today() - timedelta(days=20)
    },
    # Weekly habit
    {
        "name": "Weekly Review",
        "description": "Review goals and plan next week",
        "periodicity": Periodicity.WEEKLY,
        "start_date": date.today() - timedelta(weeks=8)
    },
    # Monthly habits
    {
        "name": "Deep Clean",
        "description": "Deep clean the apartment",
        "periodicity": Periodicity.MONTHLY,
        "start_date": date.today() - timedelta(days=90)
    },
    {
        "name": "Budget Review",
        "description": "Review and adjust monthly budget",
        "periodicity": Periodicity.MONTHLY,
        "start_date": date.today() - timedelta(days=60)
    }
]


def create_sample_check_offs(tracker, habit_name, start_date):
    """Create random check-offs for a habit."""
    current_date = start_date
    today = date.today()
    habit = tracker.get_habit(habit_name)
    if not habit:
        return

    while current_date <= today:
        # Randomly check off with 70% probability
        if randint(1, 10) <= 7:
            tracker.check_off(habit_name, current_date)

        # Move to next period based on periodicity
        if habit.periodicity == Periodicity.DAILY:
            current_date += timedelta(days=1)
        elif habit.periodicity == Periodicity.WEEKLY:
            current_date += timedelta(weeks=1)
        else:  # Monthly
            current_date += timedelta(days=30)


@click.command()
@click.option('--db', default='habits.sqlite',
              help='Database file to initialize with sample data.')
@click.option('--force', is_flag=True,
              help='Force recreation of database if it exists.')
def init_sample_data(db, force):
    """Initialize the database with sample habits."""
    repo = SqlHabitRepository(db)
    tracker = HabitTracker(repo)

    # Check if database already has habits
    existing_habits = tracker.get_habits(None)
    if existing_habits and not force:
        click.echo("Database already contains habits. Use --force to override.")
        return

    # Create sample habits
    click.echo(f"Initializing database '{db}' with sample habits...")

    for habit_data in SAMPLE_HABITS:
        # Create habit
        habit = Habit(**habit_data)
        tracker.create(habit)
        click.echo(f"Created habit: {habit_data['name']} ({habit_data['periodicity']})")

        # Create some random check-offs
        create_sample_check_offs(tracker, habit_data['name'], habit_data['start_date'])
        click.echo(f"Added sample check-offs for: {habit_data['name']}")

    click.echo("\nSample data initialization complete!")
    click.echo("Use 'poetry run habit list' to see the created habits.")


if __name__ == "__main__":
    init_sample_data()
