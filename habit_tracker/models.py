from enum import StrEnum
from datetime import date
from typing import List, Optional
from abc import ABC, abstractmethod

from sqlalchemy import (
    Column, Integer, String, Date, Enum as SQLEnum, ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base, Mapped

Base = declarative_base()


class Periodicity(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class HabitStatus(StrEnum):
    """Status of a habit's completion in current and previous periods."""
    STREAK = "streak"   # Checked off in current period
    PENDING = "pending" # Not checked off in current period, but checked off in previous
    BROKEN = "broken"   # Not checked off in both current and previous periods


class CheckOff(Base):
    """A check off model element."""
    __tablename__ = 'check_offs'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    date = Column(Date, nullable=False, default=date.today)
    habit: Mapped["Habit"] = relationship(back_populates="check_off_log")



class Habit(Base):
    """A habit model element."""
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(Date, nullable=False, default=date.today)
    periodicity = Column(SQLEnum(Periodicity), nullable=False, default=Periodicity.DAILY)
    check_off_log: Mapped[List[CheckOff]] = relationship(back_populates="habit")


class HabitRepository(ABC):
    """Define a habit repository."""

    @abstractmethod
    def save(self, habit: Habit):
        """Store a new habit."""
        ...

    @abstractmethod
    def get_all(self, periodicity: Periodicity|str) -> List[Habit]:
        """Return the habits with the given periodicity."""
        ...

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Habit]:
        """Return the habit with the given name."""
        ...

    @abstractmethod
    def delete(self, habit: Habit):
        """Remove an existing habit."""
        ...
