"""Models module using Numpydoc-style docstrings.

This module demonstrates Numpydoc-style docstrings with data model classes.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class BaseModel:
    """Base model class for all data models.

    Attributes
    ----------
    id : str
        Unique identifier
    created_at : datetime
        Creation timestamp
    """

    id: str
    created_at: datetime = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the model
        """
        return {"id": self.id, "created_at": self.created_at.isoformat()}


class User(BaseModel):
    """User model representing system users.

    Examples
    --------
    >>> user = User("123", "johndoe", "john@example.com")
    >>> user.to_dict()
    {'id': '123', 'username': 'johndoe', 'email': 'john@example.com', 'active': True}
    """

    def __init__(self, id: str, username: str, email: str, active: bool = True):
        """
        Parameters
        ----------
        id : str
            Unique identifier for the user
        username : str
            User's username
        email : str
            User's email address
        active : bool, optional
            Whether the user is active, by default True

        Attributes
        ----------
        username : str
            User's username
        email : str
            User's email address
        active : bool
            User's active status
        """
        super().__init__(id)
        self.username = username
        self.email = email
        self.active = active

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing all user fields
        """
        base_dict = super().to_dict()
        base_dict.update(
            {"username": self.username, "email": self.email, "active": self.active}
        )
        return base_dict
