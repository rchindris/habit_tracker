import os
import pytest
from datetime import datetime, date

from habit_tracker.models import Habit
from habit_tracker.repositories import SqlHabitRepository
from habit_tracker.exceptions import HabitStoreException

TEST_DB = "test_habits.sqlite"

@pytest.fixture
def repo():
    """Create a test repository."""
    repository = SqlHabitRepository(TEST_DB)
    yield repository
    
    repository._session.close()
    try:
        os.remove(TEST_DB)
    except OSError:
        pass

def test_create_habit(repo):
    """Test creating a new habit."""
    # Create a test habit
    habit = Habit(
        name="Test Habit",
        description="A test habit",
        periodicity="daily",
        start_date=date.today()
    )
    
    # Save it to the repository
    saved_habit = repo.save(habit)
    
    # Verify the habit was saved
    assert saved_habit is not None
    assert saved_habit.name == "Test Habit"
    assert saved_habit.description == "A test habit"
    assert saved_habit.periodicity == "daily"

def test_create_duplicate_habit(repo):
    """Test that creating a duplicate habit raises an exception."""
    # Create initial habit
    habit1 = Habit(
        name="Test Habit",
        description="A test habit",
        periodicity="daily",
        start_date=date.today()
    )
    repo.save(habit1)
    
    # Try to create another habit with the same name
    habit2 = Habit(
        name="Test Habit",
        description="Another test habit",
        periodicity="weekly",
        start_date=date.today()
    )
    
    # Verify that saving raises an exception
    with pytest.raises(ValueError):
        repo.save(habit2)

def test_get_by_name(repo):
    """Test retrieving a habit by name."""
    # Create and save a habit
    habit = Habit(
        name="Test Habit",
        description="A test habit",
        periodicity="daily",
        start_date=date.today()
    )
    repo.save(habit)
    
    # Retrieve the habit
    retrieved_habit = repo.get_by_name("Test Habit")
    
    # Verify the habit was retrieved correctly
    assert retrieved_habit is not None
    assert retrieved_habit.name == "Test Habit"
    assert retrieved_habit.description == "A test habit"

def test_get_all_habits(repo):
    """Test retrieving all habits."""
    # Create and save multiple habits
    habits = [
        Habit(name="Daily Habit", description="A daily habit", periodicity="daily", start_date=date.today()),
        Habit(name="Weekly Habit", description="A weekly habit", periodicity="weekly", start_date=date.today()),
        Habit(name="Monthly Habit", description="A monthly habit", periodicity="monthly", start_date=date.today())
    ]
    
    for habit in habits:
        repo.save(habit)
    
    # Get all habits
    all_habits = repo.get_all(None)
    assert len(all_habits) == 3
    
    # Get daily habits
    daily_habits = repo.get_all("daily")
    assert len(daily_habits) == 1
    assert daily_habits[0].name == "Daily Habit"

def test_delete_habit(repo):
    """Test deleting a habit."""
    # Create and save a habit
    habit = Habit(
        name="Test Habit",
        description="A test habit",
        periodicity="daily",
        start_date=date.today()
    )
    repo.save(habit)
    
    # Delete the habit
    repo.delete(habit)
    
    # Verify the habit was deleted
    retrieved_habit = repo.get_by_name("Test Habit")
    assert retrieved_habit is None

def test_delete_nonexistent_habit(repo):
    """Test deleting a habit that doesn't exist."""
    habit = Habit(
        name="Nonexistent Habit",
        description="This habit doesn't exist",
        periodicity="daily",
        start_date=date.today()
    )
    
    # Verify that deleting raises an exception
    with pytest.raises(ValueError):
        repo.delete(habit) 