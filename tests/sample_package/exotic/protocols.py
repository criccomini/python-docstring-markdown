"""Protocol and structural subtyping examples.

This module demonstrates the use of Protocol for structural subtyping
and abstract base classes.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class Loggable(Protocol):
    """Protocol for objects that can be logged.

    Example:
        >>> class MyClass(Loggable):
        ...     def log_format(self) -> str:
        ...         return "MyClass instance"
    """

    @abstractmethod
    def log_format(self) -> str:
        """Format the object for logging.

        Returns:
            A string representation of the object
        """
