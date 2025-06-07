# Habit Tracker

A command-line habit tracking application that helps you build and maintain good habits by tracking their completion over time.

## Overview

The Habit Tracker helps you:
- Create and manage habits with different periodicities (daily, weekly, monthly)
- Track habit completion and maintain streaks
- Identify broken habits that need attention
- View detailed habit analytics

Built with:
- Python 3.10+
- SQLite for data storage
- Click for CLI interface
- Rich for beautiful terminal output
- SQLAlchemy for database management

## Features

### Core Features
- Create, modify, and delete habits
- Track habits with different periodicities
- Check off completed habits
- View habit history and progress

### Analytics
- Track streak information
- Identify broken habits (not checked off in their period)
- Monitor habit status and health
- Analyze performance over time

### User Experience
- Intuitive command-line interface
- Beautiful terminal output
- Clear error messages and feedback
- Easy-to-use command structure

## Installation

1. **Prerequisites**
   - Python 3.10 or newer
   - pip or Poetry (recommended)

2. **Install Python**
   ```bash
   # Verify Python installation
   python --version  # Should be 3.10 or higher
   ```

3. **Install Poetry** (recommended)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. **Get the Code**
   ```bash
   git clone https://github.com/rchindris/habit_tracker
   cd habit_tracker
   ```

5. **Install Dependencies**
   ```bash
   poetry install
   ```

## Usage Guide

### Quick Start with Sample Data

To quickly get started with some sample habits, you can use the sample data initialization tool:

```bash
# Initialize with sample habits
poetry run create-habit-samples

# Initialize with custom database file
poetry run create-habit-samples --db my_habits.sqlite

# Force recreation of sample data
poetry run create-habit-samples --force
```

This will create 5 sample habits with realistic check-off history:
- Daily habits: "Morning Exercise" and "Read Book"
- Weekly habit: "Weekly Review"
- Monthly habits: "Deep Clean" and "Budget Review"

After initialization, you can use the regular commands to interact with these habits:
```bash
# View all sample habits
poetry run habit list

# Show detailed information for a habit
poetry run habit show "Morning Exercise"

# View check-off history
poetry run habit history "Morning Exercise"

# Check broken habits
poetry run habit show-broken

# View streaks
poetry run habit streaks
```

### Analytics Features

The habit tracker provides several ways to analyze your habits and track progress:

#### Viewing All Habits
```bash
# List all tracked habits
poetry run habit list

# List habits by periodicity (daily/weekly/monthly)
poetry run habit list --periodicity daily
poetry run habit list --periodicity weekly
poetry run habit list --periodicity monthly
```

#### Tracking Streaks
```bash
# View streaks for all habits
poetry run habit streaks

# View streaks by periodicity
poetry run habit streaks --periodicity daily

# View detailed statistics for a specific habit (includes longest streak)
poetry run habit show "Morning Exercise"
```

The streaks command shows:
- Current streak for each habit
- Longest streak for each habit
- The overall longest streak across all habits

#### Monitoring Habit Health
```bash
# Show broken habits (not checked off in their period)
poetry run habit show-broken

# Show broken habits by periodicity
poetry run habit show-broken --periodicity daily
```

#### Viewing Habit Details
```bash
# Show detailed statistics for a habit
poetry run habit show "Morning Exercise"

# View complete check-off history
poetry run habit history "Morning Exercise"
```

Example outputs:

1. List command shows:
   - Habit name and description
   - Periodicity
   - Start date
   - Last check-off date
   - Current status

2. Streaks command shows:
   - Longest streak for each habit
   - Current streak
   - Overall best streak across all habits

3. Show command displays:
   - Basic habit information
   - Streak information
   - Current status (Streak/Broken)
   - Days tracked
   - Total completions

4. History command shows:
   - Complete check-off history
   - Dates of all completions
   - Days since each check-off

### Basic Commands

#### Creating Habits
```bash
# Create a new habit
poetry run habit create "Morning Exercise" \
  --description "30 minutes of morning exercise" \
  --periodicity daily

# Create a weekly habit
poetry run habit create "Weekly Review" \
  --description "Review weekly goals" \
  --periodicity weekly
```

#### Managing Habits
```bash
# List all habits
poetry run habit list

# List habits by periodicity
poetry run habit list --periodicity daily

# Show detailed information for a habit
poetry run habit show "Morning Exercise"

# View check-off history for a habit
poetry run habit history "Morning Exercise"

# Delete a habit
poetry run habit delete "Morning Exercise"
```

#### Tracking Progress
```bash
# Check off a habit
poetry run habit check-off "Morning Exercise"

# Check off with specific date
poetry run habit check-off "Morning Exercise" --date "2024-01-15"
```

### Analytics Commands

#### Viewing Streaks
```bash
# View all streaks
poetry run habit streaks

# View streaks for specific periodicity
poetry run habit streaks --periodicity daily
```

#### Monitoring Broken Habits
```bash
# View all broken habits
poetry run habit show-broken

# View broken habits by periodicity
poetry run habit show-broken --periodicity daily

# Get detailed status for a specific habit
poetry run habit analyze habit "Morning Exercise"
```

The broken habits analysis shows:
- Which habits need attention
- Last check-off date for each habit
- Days since last completion
- Habit status (Active/Broken)

### Common Options

Most commands support these options:
- `--db`: Custom database file (default: habits.sqlite)
- `--periodicity`: Filter by frequency (daily, weekly, monthly)
- `--start-date`: Custom start date (YYYY-MM-DD)
- `--date`: Specific date for check-offs (YYYY-MM-DD)

### Getting Help

```bash
# General help
poetry run habit --help

# Command-specific help
poetry run habit create --help
poetry run habit analyze --help
```

## Data Storage

The application uses SQLite for data storage:
- Default database file: `habits.sqlite`
- Custom database can be specified with `--db` option
- Data is persisted between sessions
- Each habit stores:
  - Name and description
  - Periodicity (daily/weekly/monthly)
  - Start date
  - Check-off history

## License

This project is licensed under the MIT License - see the LICENSE file for details.
