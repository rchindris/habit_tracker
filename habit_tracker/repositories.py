import logging
from typing import Union, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from habit_tracker.exceptions import HabitStoreException
from habit_tracker.models import (
    Base,
    Habit, 
    HabitRepository, 
    Periodicity
)


class SqlHabitRepository(HabitRepository):
    """A habit repository implementation using SQLAlchemy"""

    def __init__(self, db_file: str):
        """Initialize the repository.

        Args:
            db_file (str): the path to the SQLite database file.
        """
        if not db_file:
            raise ValueError("db_file is None")
            
        self._logger = logging.getLogger(SqlHabitRepository.__name__)

        # Create SQLAlchemy engine and session
        self.engine = create_engine(f'sqlite:///{db_file}')
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = self.session_factory()
        
        # Ensure the tables exist
        Base.metadata.create_all(self.engine)

    def save(self, habit: Habit) -> Optional[Habit]:
        """Create a new habit in the database.

        Args:
          habit (Habit): the habit object to save.

        Returns:
          the saved Habit instance.
        """
        try:
            self.session.add(habit)
            self.session.commit()
            
            return habit  # The habit now has an ID after commit
        except IntegrityError as ie:
            self.session.rollback()
            raise HabitStoreException("A habit with the same name already exists")

    def get_all(self, periodicity: Periodicity|str) -> List[Habit]:
        """Return the habits for a given periodicity.

        Args:
          periodicity (Periodicity|str): the habit periodicity.
        """
        try:
            if periodicity:
                habits = self.session.query(Habit).filter(Habit.periodicity == periodicity).all()            
            else:
                habits = self.session.query(Habit).all()
            return habits
        except Exception as e:
            raise HabitStoreException(str(e))
    
    def get_by_name(self, name: str) -> Optional[Habit]:
        """Return the habit with the given name."""
        try:
            return self.session.query(Habit).filter(Habit.name == name).first()
        except Exception as e:
            raise HabitStoreException(str(e))

    def delete(self, habit: Habit):
        """Remove an existing habit from the database."""
        if not habit:
            raise ValueError("habit is None")

        try:
            self.session.delete(habit)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise HabitStoreException(str(e))
