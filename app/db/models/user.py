"""User model for the application."""

import datetime
from enum import Enum
from typing import Dict, List, Optional

from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    EmailField,
    EnumField,
    ListField,
    StringField,
    URLField,
)


class UserRole(str, Enum):
    """User role enum."""

    USER = "user"
    ADMIN = "admin"


class User(Document):
    """User model for the application."""

    email = EmailField(required=True, unique=True)
    full_name = StringField(required=True, max_length=100)
    profile_picture = URLField()
    google_id = StringField(unique=True, sparse=True)
    role = EnumField(UserRole, default=UserRole.USER)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    last_login = DateTimeField()
    is_active = BooleanField(default=True)
    preferences = ListField(StringField())
    
    meta = {
        "collection": "users",
        "indexes": [
            "email",
            "google_id",
            "-created_at"
        ]
    }
    
    def clean(self):
        """Update the updated_at field on save."""
        self.updated_at = datetime.datetime.utcnow()
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional["User"]:
        """
        Get a user by email.
        
        Args:
            email: The email of the user to find.
            
        Returns:
            The user document or None if not found.
        """
        return cls.objects(email=email).first()
    
    @classmethod
    def get_by_google_id(cls, google_id: str) -> Optional["User"]:
        """
        Get a user by Google ID.
        
        Args:
            google_id: The Google ID of the user to find.
            
        Returns:
            The user document or None if not found.
        """
        return cls.objects(google_id=google_id).first()
    
    def to_dict(self) -> Dict:
        """
        Convert the user to a dictionary.
        
        Returns:
            A dictionary representation of the user.
        """
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "profile_picture": self.profile_picture,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
            "preferences": self.preferences
        } 