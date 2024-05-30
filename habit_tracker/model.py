from enum import Enum
from typing import List
from datetime import date

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class Periodicity(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class Habit:
    """A habit model element."""
    id: int
    name: str
    description: str
    start_date: date
    periodicity: Periodicity
    check_off_log: List[date] = field(default_factory=list)


class HabitRepository(ABC):
    """Define a habit repository."""

    @abstractmethod
    def create(self, habit: Habit):
        """Store a new habit."""
        ...

    @abstractmethod
    def update(self, habit: Habit):
        """Update an existing habit."""
        ...

    @abstractmethod
    def read(self, periodicity: Periodicity|str):
        """Return the habits with the given periodicity."""
        ...

    @abstractmethod
    def delete(self, habit: Habit):
        """Remove an existing habit."""
        ...
