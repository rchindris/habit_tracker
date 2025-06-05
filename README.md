# Habit Tracker

A command-line habit tracking application that helps you build and maintain good habits by tracking their completion over time.

## Features

- **Habit Management**
  - Create new habits with custom names and descriptions
  - Delete existing habits when they're no longer needed
  - List all habits with their current status
  - Filter habits by periodicity (daily, weekly, monthly)

- **Tracking**
  - Check off habits as they're completed
  - View habit completion history
  - Track habits with different periodicities:
    - Daily habits
    - Weekly habits
    - Monthly habits

- **User Interface**
  - Beautiful CLI interface with colored output
  - Clear error messages and feedback
  - Easy-to-use command structure
  - Tabulated data display

## Installation

1. Ensure you have Python 3.10 or newer installed:
   ```bash
   python --version
   ```

2. Install Poetry (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Clone the repository:
   ```bash
   git clone https://github.com/rchindris/habit_tracker
   cd habit_tracker
   ```

4. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

## Usage

The habit tracker provides several commands for managing your habits. Here are the main commands:

### Creating a Habit

Create a new habit with a name, description, and periodicity:

```bash
poetry run habit create "Morning Exercise" \
  --description "30 minutes of morning exercise" \
  --periodicity daily
```

### Listing Habits

View all your habits or filter by periodicity:

```bash
# List all habits
poetry run habit list

# List only daily habits
poetry run habit list --periodicity daily
```

### Checking Off a Habit

Mark a habit as completed:

```bash
poetry run habit check-off "Morning Exercise"
```

### Deleting a Habit

Remove a habit from tracking:

```bash
poetry run habit delete "Morning Exercise"
```

### Command Options

Each command supports various options:

- `--db`: Specify a custom database file (default: habits.sqlite)
- `--periodicity`: Filter habits by frequency (daily, weekly, monthly)
- `--start-date`: Set a custom start date for new habits (YYYY-MM-DD format)

For detailed help on any command, use the `--help` option:

```bash
poetry run habit --help
poetry run habit create --help
```
