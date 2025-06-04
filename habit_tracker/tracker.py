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

    def get_habits(self, periodicity: Periodicity|str) -> List[Habit]:
        """Get all habits with the given periodicity."""
        return self._repository.get_all(periodicity)

    def create(self, habit: Habit) -> bool:
        """Create a new habit and store it in the repository.

        Args:
        habit (Habit): The habit to be created.

        Returns:
        The new habit object if it was created successfully, None otherwise.
        
        """
        if habit is None:
            raise ValueError("habit is None")

        existing_habit = self._repository.get_all(habit.name)
        if existing_habit:
            raise HabitStoreException("A habit with the same name already exists")

        try:
            return self._repository.save(habit)
        except Exception as e:
            print(e)
            raise HabitStoreException(str(e))

    def delete(self, habit_name: str) -> bool:
        """Delete a habit."""
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
    
    def check_off(self, habit_name: str) -> None:
        """Check off a habit."""
        habit = self._repository.get_by_name(habit_name)
        if not habit:
            raise HabitStoreException("Habit not found")

        if habit:
            self._repository.save(habit)
            
            
            
        
            
            
        
        
