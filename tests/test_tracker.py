import pytest
from datetime import date
from unittest.mock import Mock, MagicMock

from habit_tracker.models import Habit, HabitRepository, Periodicity
from habit_tracker.tracker import HabitTracker
from habit_tracker.exceptions import HabitStoreException

@pytest.fixture
def mock_repo():
    """Create a mock repository."""
    return Mock(spec=HabitRepository)

@pytest.fixture
def tracker(mock_repo):
    """Create a tracker with a mock repository."""
    return HabitTracker(mock_repo)

def test_create_habit(tracker, mock_repo):
    """Test creating a new habit."""
    # Setup
    habit = Habit(
        name="Test Habit",
        description="A test habit",
        periodicity="daily",
        start_date=date.today()
    )
    mock_repo.get_by_name.return_value = None
    mock_repo.save.return_value = habit
    
    # Execute
    result = tracker.create(habit)
    
    # Verify
    assert result == habit
    mock_repo.get_by_name.assert_called_once_with(habit.name)
    mock_repo.save.assert_called_once_with(habit)

def test_create_duplicate_habit(tracker, mock_repo):
    """Test that creating a duplicate habit raises an exception."""
    # Setup
    habit = Habit(
        name="Test Habit",
        description="A test habit",
        periodicity="daily",
        start_date=date.today()
    )
    mock_repo.get_by_name.return_value = habit
    
    # Execute and verify
    with pytest.raises(HabitStoreException) as exc_info:
        tracker.create(habit)
    assert "already exists" in str(exc_info.value)
    mock_repo.save.assert_not_called()

def test_create_habit_none(tracker):
    """Test that creating None as habit raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        tracker.create(None)
    assert "habit is None" in str(exc_info.value)

def test_get_habits_by_periodicity(tracker, mock_repo):
    """Test getting habits filtered by periodicity."""
    # Setup
    habits = [
        Habit(name="Daily Habit", description="A daily habit", periodicity="daily"),
        Habit(name="Weekly Habit", description="A weekly habit", periodicity="weekly")
    ]
    mock_repo.get_all.return_value = habits
    
    # Execute
    result = tracker.get_habits("daily")
    
    # Verify
    assert result == habits
    mock_repo.get_all.assert_called_once_with(Periodicity.DAILY)

def test_get_habits_none_periodicity(tracker):
    """Test that getting habits with None periodicity raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        tracker.get_habits(None)
    assert "periodicity is None" in str(exc_info.value)

def test_delete_habit(tracker, mock_repo):
    """Test deleting an existing habit."""
    # Setup
    habit = Habit(
        name="Test Habit",
        description="A test habit",
        periodicity="daily",
        start_date=date.today()
    )
    mock_repo.get_by_name.return_value = habit
    
    # Execute
    result = tracker.delete("Test Habit")
    
    # Verify
    assert result is True
    mock_repo.get_by_name.assert_called_once_with("Test Habit")
    mock_repo.delete.assert_called_once_with(habit)

def test_delete_nonexistent_habit(tracker, mock_repo):
    """Test deleting a non-existent habit."""
    # Setup
    mock_repo.get_by_name.return_value = None
    
    # Execute and verify
    with pytest.raises(HabitStoreException) as exc_info:
        tracker.delete("Nonexistent Habit")
    assert "not found" in str(exc_info.value)
    mock_repo.delete.assert_not_called()

def test_delete_none_habit_name(tracker):
    """Test that deleting with None as habit name raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        tracker.delete(None)
    assert "habit_name is None" in str(exc_info.value)

def test_check_off_habit(tracker, mock_repo):
    """Test checking off an existing habit."""
    # Setup
    habit = Habit(
        name="Test Habit",
        description="A test habit",
        periodicity="daily",
        start_date=date.today()
    )
    mock_repo.get_by_name.return_value = habit
    
    # Execute
    tracker.check_off("Test Habit")
    
    # Verify
    mock_repo.get_by_name.assert_called_once_with("Test Habit")
    mock_repo.save.assert_called_once_with(habit)

def test_check_off_nonexistent_habit(tracker, mock_repo):
    """Test checking off a non-existent habit."""
    # Setup
    mock_repo.get_by_name.return_value = None
    
    # Execute and verify
    with pytest.raises(HabitStoreException) as exc_info:
        tracker.check_off("Nonexistent Habit")
    assert "not found" in str(exc_info.value)
    mock_repo.save.assert_not_called()

def test_check_off_none_habit_name(tracker):
    """Test that checking off with None as habit name raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        tracker.check_off(None)
    assert "habit_name is None" in str(exc_info.value) 