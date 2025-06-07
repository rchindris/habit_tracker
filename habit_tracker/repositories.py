import logging
from typing import List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from habit_tracker.models import (
    Habit,
    HabitRepository,
    Periodicity,
)


class SqlHabitRepository(HabitRepository):
    """SQLite-based implementation of the habit repository."""

    def __init__(self, db_file: str):
        """Initialize the repository with a database file."""
        if not db_file:
            raise ValueError("db_file is None")

        self._logger = logging.getLogger(SqlHabitRepository.__name__)

        self.engine = create_engine(f"sqlite:///{db_file}")
        Habit.metadata.create_all(self.engine)

    def save(self, habit: Habit):
        """Store a new habit.

        Args:
            habit (Habit): The habit to store.
        Raises:
            ValueError: If the habit already exists.
        """
        with Session(self.engine) as session:
            session.add(habit)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Habit with name '{habit.name}' already exists")

    def get_all(self, periodicity: Periodicity | str) -> List[Habit]:
        """Return the habits with the given periodicity.

        Args:
            periodicity (Periodicity | str): The periodicity to filter by.
        Returns:
            List[Habit]: The filtered habits.
        """
        with Session(self.engine) as session:
            query = session.query(Habit)
            if periodicity:
                query = query.filter(Habit.periodicity == periodicity)
            return list(query.all())

    def get_by_name(self, name: str) -> Optional[Habit]:
        """Return the habit with the given name.

        Args:
            name (str): The name of the habit to get.
        Returns:
            Optional[Habit]: The habit if found, None otherwise.
        """
        with Session(self.engine) as session:
            return session.query(Habit).filter(Habit.name == name).first()

    def delete(self, habit: Habit):
        """Remove an existing habit.

        Args:
            habit (Habit): The habit to delete.
        """
        with Session(self.engine) as session:
            session.delete(habit)
            session.commit()
