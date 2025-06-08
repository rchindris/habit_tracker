from typing import List, Optional
from datetime import date

from habit_tracker.models import (
    Habit, HabitRepository, Periodicity, CheckOff
)


class HabitTracker:
    """Core habit tracking functionality."""

    def __init__(self, repository: HabitRepository):
        """Initialize the tracker with a repository."""
        self.repository = repository

    def create(self, habit: Habit) -> Habit:
        """Create a new habit.

        Args:
            habit (Habit): The habit to create.
        Returns:
            Habit: The created habit.
        Raises:
            ValueError: If the habit name, description, or periodicity is not provided.
        """
        if not habit:
            raise ValueError("Habit is required")

        if not habit.name:
            raise ValueError("Habit name is required")
        if not habit.periodicity:
            raise ValueError("Habit periodicity is required")
        if not habit.start_date:
            habit.start_date = date.today()

        existing = self.get_habit(habit.name)
        if existing:
            raise ValueError(f"Habit with name '{habit.name}' already exists")

        self.repository.save(habit)
        return habit

    def get_habits(self, periodicity: Optional[Periodicity | str] = None) -> List[Habit]:
        """Return habits filtered by periodicity.

        Args:
            periodicity (Optional[Periodicity | str]): The periodicity to filter by.
        Returns:
            List[Habit]: The filtered habits.
        """
        return self.repository.get_all(periodicity)

    def get_habit(self, name: str) -> Optional[Habit]:
        """Return a habit by name.

        Args:
            name (str): The name of the habit to get.
        Returns:
            Optional[Habit]: The habit if found, None otherwise.
        """
        return self.repository.get_by_name(name)

    def habit_exists(self, name: str) -> bool:
        """Check if a habit exists.

        Args:
            name (str): The name of the habit to check.
        Returns:
            bool: True if the habit exists, False otherwise.
        """
        return self.get_habit(name) is not None

    def check_off(self, name: str, check_date: date = None) -> bool:
        """Check off a habit for a given date.

        Args:
            name (str): The name of the habit to check off.
            check_date (date): The date to check off the habit.
        Returns:
            bool: True if the habit was checked off, False otherwise.
        """
        if not name:
            raise ValueError("Habit name is required")

        habit = self.get_habit(name)
        if not habit:
            return False

        if not check_date:
            check_date = date.today()

        if check_date > date.today():
            raise ValueError("Check date cannot be in the future")

        # Create a new check-off
        check_off = CheckOff(date=check_date)
        habit.check_off_log.append(check_off)

        try:
            self.repository.save(habit)
            return True
        except Exception:
            return False

    def delete(self, name: str) -> bool:
        """Delete a habit by name.

        Args:
            name (str): The name of the habit to delete.
        Returns:
            bool: True if the habit was deleted, False otherwise.
        """
        if not name:
            raise ValueError("Habit name is required")

        if not self.habit_exists(name):
            raise ValueError(f"Habit with name '{name}' does not exist")

        habit = self.get_habit(name)
        if not habit:
            return False

        try:
            self.repository.delete(habit)
            return True
        except Exception:
            return False
