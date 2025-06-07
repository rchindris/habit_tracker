"""Analytics module for habit tracking analysis.

This module implements analytics functionality using functional programming principles.
It provides functions to analyze habits and their completion patterns.
"""
from typing import List, Optional, Tuple
from datetime import date, timedelta
from itertools import groupby
from operator import attrgetter
from functools import reduce

from habit_tracker.models import Habit, Periodicity


def get_all_habits(habits: List[Habit]) -> List[Habit]:
    """Return all habits, sorted by name.
    
    Args:
        habits: List of habits to analyze
        
    Returns:
        List of habits sorted by name
    """
    return sorted(habits, key=lambda h: h.name)


def get_habits_by_periodicity(habits: List[Habit], periodicity: Periodicity) -> List[Habit]:
    """Return habits filtered by periodicity.
    
    Args:
        habits: List of habits to analyze
        periodicity: The periodicity to filter by
        
    Returns:
        List of habits with the specified periodicity
    """
    return list(filter(lambda h: h.periodicity == periodicity, habits))


def _get_date_diff(periodicity: Periodicity) -> timedelta:
    """Get the timedelta for a given periodicity."""
    return {
        Periodicity.DAILY: timedelta(days=1),
        Periodicity.WEEKLY: timedelta(weeks=1),
        Periodicity.MONTHLY: timedelta(days=30)  # Approximation
    }[periodicity]


def _is_streak(dates: List[date], periodicity: Periodicity) -> bool:
    """Check if a sequence of dates forms a streak based on periodicity."""
    if not dates:
        return False
        
    date_diff = _get_date_diff(periodicity)
    sorted_dates = sorted(dates)
    
    # Use zip to compare consecutive dates
    return all(
        b - a <= date_diff 
        for a, b in zip(sorted_dates, sorted_dates[1:])
    )


def _get_streaks(check_offs: List[date], periodicity: Periodicity) -> List[int]:
    """Get all streak lengths from a list of check-off dates."""
    if not check_offs:
        return [0]
        
    # Sort dates and group consecutive dates based on periodicity
    sorted_dates = sorted(check_offs)
    date_diff = _get_date_diff(periodicity)
    
    def group_consecutive_dates(dates: List[date]) -> List[List[date]]:
        result = []
        current_group = []
        
        for d in dates:
            if not current_group or d - current_group[-1] <= date_diff:
                current_group.append(d)
            else:
                result.append(current_group)
                current_group = [d]
                
        if current_group:
            result.append(current_group)
            
        return result
    
    # Get lengths of all streaks
    return [len(streak) for streak in group_consecutive_dates(sorted_dates)]


def get_longest_streak_for_habit(habit: Habit) -> int:
    """Return the longest streak for a given habit.
    
    Args:
        habit: The habit to analyze
        
    Returns:
        Length of the longest streak
    """
    check_off_dates = [co.date for co in habit.check_off_log]
    streaks = _get_streaks(check_off_dates, habit.periodicity)
    return max(streaks) if streaks else 0


def get_longest_streak_all_habits(habits: List[Habit]) -> Tuple[str, int]:
    """Return the longest streak across all habits.
    
    Args:
        habits: List of habits to analyze
        
    Returns:
        Tuple of (habit_name, streak_length) for the habit with longest streak
    """
    if not habits:
        return ("", 0)
        
    # Map habits to (name, streak) tuples
    habit_streaks = map(
        lambda h: (h.name, get_longest_streak_for_habit(h)), 
        habits
    )
    
    # Reduce to find the maximum streak
    return reduce(
        lambda a, b: a if a[1] > b[1] else b,
        habit_streaks
    )


def _get_period_dates(current_date: date, periodicity: Periodicity) -> Tuple[date, date]:
    """Get the start and end dates for the previous period.
    
    Args:
        current_date: The date to check from
        periodicity: The habit's periodicity
        
    Returns:
        Tuple of (period_start, period_end) dates
    """
    if periodicity == Periodicity.DAILY:
        return (
            current_date - timedelta(days=1),
            current_date - timedelta(days=1)
        )
    elif periodicity == Periodicity.WEEKLY:
        period_end = current_date - timedelta(days=1)
        return (
            period_end - timedelta(days=6),
            period_end
        )
    else:  # Monthly
        # Approximate month as 30 days
        period_end = current_date - timedelta(days=1)
        return (
            period_end - timedelta(days=29),
            period_end
        )


def is_habit_broken(habit: Habit, as_of_date: date = None) -> Tuple[bool, Optional[date]]:
    """Check if a habit is broken (missed in its last period).
    
    A habit is considered broken if it was not checked off in its previous period:
    - Daily habits: Not checked off yesterday
    - Weekly habits: Not checked off in the previous 7 days
    - Monthly habits: Not checked off in the previous 30 days
    
    Args:
        habit: The habit to analyze
        as_of_date: The date to check from (defaults to today)
        
    Returns:
        Tuple of (is_broken, last_check_off_date)
    """
    if not habit.start_date:
        return (False, None)
        
    current_date = as_of_date or date.today()
    
    # If habit started today or in the future, it's not broken
    if habit.start_date >= current_date:
        return (False, None)
        
    check_off_dates = sorted([co.date for co in habit.check_off_log])
    if not check_off_dates:
        # Only broken if start date is before the current period
        period_start, _ = _get_period_dates(current_date, habit.periodicity)
        return (habit.start_date <= period_start, None)
    
    # Get the previous period's date range
    period_start, period_end = _get_period_dates(current_date, habit.periodicity)
    
    # Check if the habit started before or during the period we're checking
    if habit.start_date > period_end:
        return (False, check_off_dates[-1])
    
    # Check if there are any check-offs in the previous period
    has_period_checkoff = any(
        period_start <= check_date <= period_end
        for check_date in check_off_dates
    )
    
    return (not has_period_checkoff, check_off_dates[-1])


def get_broken_habits(habits: List[Habit], as_of_date: date = None) -> List[Tuple[str, date, Periodicity]]:
    """Get all broken habits with their last check-off dates.
    
    Args:
        habits: List of habits to analyze
        as_of_date: The date to check from (defaults to today)
        
    Returns:
        List of (habit_name, last_check_off_date, periodicity) for broken habits,
        sorted by how long they've been broken
    """
    broken_habits = []
    current_date = as_of_date or date.today()
    
    for habit in habits:
        is_broken, last_check_off = is_habit_broken(habit, current_date)
        if is_broken:
            broken_habits.append((
                habit.name,
                last_check_off or habit.start_date,
                habit.periodicity
            ))
    
    # Sort by days since last check-off
    return sorted(
        broken_habits,
        key=lambda x: current_date - (x[1] or current_date),
        reverse=True
    )


def get_habit_completion_rate(habit: Habit) -> float:
    """Calculate the completion rate for a habit.
    
    Args:
        habit: The habit to analyze
        
    Returns:
        Percentage of completion (0-100)
    """
    if not habit.start_date:
        return 0.0
        
    # Calculate expected completions based on periodicity
    days_since_start = (date.today() - habit.start_date).days
    expected = {
        Periodicity.DAILY: days_since_start,
        Periodicity.WEEKLY: days_since_start // 7,
        Periodicity.MONTHLY: days_since_start // 30
    }[habit.periodicity]
    
    if expected == 0:
        return 100.0
        
    actual = len(habit.check_off_log)
    return (actual / expected) * 100 if expected > 0 else 0.0


def get_all_completion_rates(habits: List[Habit]) -> List[Tuple[str, float]]:
    """Get completion rates for all habits.
    
    Args:
        habits: List of habits to analyze
        
    Returns:
        List of (habit_name, completion_rate) tuples
    """
    return sorted([
        (habit.name, get_habit_completion_rate(habit))
        for habit in habits
    ], key=lambda x: x[1], reverse=True)
