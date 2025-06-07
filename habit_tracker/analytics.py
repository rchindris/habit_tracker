"""Analytics module for habit tracking analysis.

This module implements analytics functionality using functional programming principles.
It provides functions to analyze habits and their completion patterns.
"""
from typing import List, Optional, Tuple, Literal
from datetime import date, timedelta
from itertools import groupby
from operator import attrgetter
from functools import reduce
from enum import Enum

from habit_tracker.models import Habit, Periodicity, HabitStatus


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


def _get_period_dates(current_date: date, periodicity: Periodicity, offset: int = 0) -> Tuple[date, date]:
    """Get the start and end dates for a period.
    
    Args:
        current_date: The date to check from
        periodicity: The habit's periodicity
        offset: Period offset (0 for current, 1 for previous, etc.)
        
    Returns:
        Tuple of (period_start, period_end) dates
    """
    if periodicity == Periodicity.DAILY:
        period_end = current_date - timedelta(days=offset)
        return (period_end, period_end)
    elif periodicity == Periodicity.WEEKLY:
        period_end = current_date - timedelta(days=offset * 7)
        return (
            period_end - timedelta(days=6),
            period_end
        )
    else:  # Monthly
        # Approximate month as 30 days
        period_end = current_date - timedelta(days=offset * 30)
        return (
            period_end - timedelta(days=29),
            period_end
        )


def get_habit_status(habit: Habit, as_of_date: date = None) -> Tuple[HabitStatus, Optional[date]]:
    """Get the current status of a habit.
    
    A habit's status is determined as follows:
    - STREAK: Checked off in the current period
    - PENDING: Not checked off in current period, but checked off in previous period
    - BROKEN: Not checked off in both current and previous periods
    
    Args:
        habit: The habit to analyze
        as_of_date: The date to check from (defaults to today)
        
    Returns:
        Tuple of (status, last_check_off_date)
    """
    if not habit.start_date:
        return (HabitStatus.STREAK, None)
        
    current_date = as_of_date or date.today()
    
    # If habit hasn't started yet, it's not broken
    if habit.start_date > current_date:
        return (HabitStatus.STREAK, None)
        
    check_off_dates = sorted([co.date for co in habit.check_off_log])
    if not check_off_dates:
        # If no check-offs and should have started, it's broken
        period_start, _ = _get_period_dates(current_date, habit.periodicity, 1)
        return (
            HabitStatus.BROKEN if habit.start_date <= period_start 
            else HabitStatus.PENDING,
            None
        )
    
    # Get current and previous period dates
    curr_start, curr_end = _get_period_dates(current_date, habit.periodicity, 0)
    prev_start, prev_end = _get_period_dates(current_date, habit.periodicity, 1)
    
    # If habit started after the previous period, it can't be broken
    if habit.start_date > prev_end:
        has_current = any(
            curr_start <= check_date <= curr_end
            for check_date in check_off_dates
        )
        return (
            HabitStatus.STREAK if has_current else HabitStatus.PENDING,
            check_off_dates[-1]
        )
    
    # Check both periods
    has_current = any(
        curr_start <= check_date <= curr_end
        for check_date in check_off_dates
    )
    has_previous = any(
        prev_start <= check_date <= prev_end
        for check_date in check_off_dates
    )
    
    if has_current:
        status = HabitStatus.STREAK
    elif has_previous:
        status = HabitStatus.PENDING
    else:
        status = HabitStatus.BROKEN
    
    return (status, check_off_dates[-1])


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
        status, last_check_off = get_habit_status(habit, current_date)
        if status == HabitStatus.BROKEN:
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
