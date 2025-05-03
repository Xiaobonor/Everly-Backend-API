"""User schemas for request and response validation."""

import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, HttpUrl


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str
    profile_picture: Optional[HttpUrl] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a user."""

    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    full_name: Optional[str] = None
    profile_picture: Optional[HttpUrl] = None
    preferences: Optional[List[str]] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: str
    created_at: datetime.datetime
    preferences: List[str] = []

    class Config:
        """Pydantic config."""

        from_attributes = True 