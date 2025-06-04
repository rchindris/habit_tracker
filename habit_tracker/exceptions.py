"""Define custom exception classes."""


class HabitStoreException(Exception):
    """Signals that a habit cannot be stored."""

    def __init__(self, cause: str):
        super().__init__(
            f"Failed to store habit. Cause: {cause}"
        )


class DeleteHabitException(Exception):
    """Signals that a habit failed to be removed."""

    def __init__(self, cause: str):
        super().__init__(
            f"Failed to delete habit. Cause: {cause}"
        )
