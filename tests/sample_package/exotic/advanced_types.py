"""Advanced type hints and generic types demonstration.

This module uses various type hints and generic types to showcase
complex typing scenarios.
"""

from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T")
S = TypeVar("S", bound="Serializable")
"""
Serializable container type.
"""


class Serializable(Generic[T]):
    """A generic serializable container.

    Type Parameters
    --------------
    T
        The type of value being stored

    Attributes
    ----------
    value : T
        The contained value
    created_at : datetime
        Timestamp of creation
    """

    def __init__(self, value: T):
        self.value = value
        self.created_at = datetime.now()

    def serialize(self) -> dict:
        """Convert the container to a dictionary.

        Returns
        -------
        dict
            A dictionary containing the value and metadata
        """
        return {"value": self.value, "created_at": self.created_at.isoformat()}
