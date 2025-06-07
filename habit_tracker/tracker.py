import logging
from typing import List
from datetime import date

from habit_tracker.models import (
    Habit, HabitRepository, Periodicity, CheckOff
)
from habit_tracker.exceptions import HabitStoreException


class HabitTracker:
    """"Implementation of the HabitTracker application logic."""

    def __init__(self, repository: HabitRepository):
        """Initialize for the given repository.

        Args:
        repostiory (HabitRepository): The repository for storing habits.
        """
        if repository is None:
            raise ValueError("repository is None")

        self._repository = repository

    def habit_exists(self, habit_name: str) -> bool:
        """Check if a habit exists.
        
        Args:
          habit_name (str): The name of the habit to check.
        """
        return self._repository.get_by_name(habit_name) is not None
    
    def get_habit(self, habit_name: str) -> Habit:
        """Get a habit by name.
        
        Args:
          habit_name (str): The name of the habit to get.
        """
        return self._repository.get_by_name(habit_name)

    def get_habits(self, periodicity: Periodicity|str) -> List[Habit]:
        """Get all habits with the given periodicity.

        Args:
          periodicity (Periodicity|str): The periodicity of the habits to get.

        Returns:
          A list of habits with the given periodicity.
        """
        if isinstance(periodicity, str):
            periodicity = Periodicity(periodicity)

        return self._repository.get_all(periodicity)

    def create(self, habit: Habit) -> bool:
        """Create a new habit and store it in the repository.

        Args:
          habit (Habit): The habit to create.

        Returns:
          The new habit object if it was created successfully, None otherwise.

        Raises:
          ValueError: If the habit is None.
        """
        if habit is None:
            raise ValueError("habit is None")

        existing_habit = self._repository.get_by_name(habit.name)
        if existing_habit:
            logging.error("A habit with the same name already exists")
            return False

        try:
            return self._repository.save(habit)
        except Exception as e:
            logging.error(e)
            return False

    def delete(self, habit_name: str) -> bool:
        """Delete a habit.

        Args:
          habit_name (str): The name of the habit to delete.

        Returns:
          True if the habit was deleted successfully, False otherwise.

        Raises:
          ValueError: If the habit name is None.
          HabitStoreException: If the habit is not found.
        """
        if habit_name is None:
            raise ValueError("habit_name is None")

        habit = self._repository.get_by_name(habit_name)
        if not habit:
            raise HabitStoreException("Habit not found")

        deleted = False
        try:
            self._repository.delete(habit)
            deleted = True
        except HabitStoreException as e:
            logging.error(e)

        return deleted
    
    def check_off(self, habit_name: str, when: date) -> bool:
        """Check off a habit.

        Args:
          habit_name (str): The name of the habit to check off.
          date (date): The date to check off the habit. If not provided, the current date is used.

        Returns:
          True if the habit was checked off successfully, False otherwise.

        Raises:
          ValueError: If the habit name is None.
        """
        if habit_name is None:
            raise ValueError("habit_name is None")
        if when is None:
            when = date.today()

        # Check if the date is in the future
        if when > date.today():
            logging.error("Date is in the future")
            return False
        
        habit = self._repository.get_by_name(habit_name)
        if not habit:
            logging.error("Habit not found")
            return False

        try:
            habit.check_off_log.append(CheckOff(date=when))
            self._repository.save(habit)
            return True
        except HabitStoreException as e:
            logging.error(e)
        
        return False
            
        
            
            
        
        
