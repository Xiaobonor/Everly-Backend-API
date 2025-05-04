"""Authentication schemas for request and response validation."""

from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Schema for authentication token."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for token payload."""

    sub: Optional[str] = None
    email: Optional[str] = None


class AuthResponse(BaseModel):
    """Schema for authentication response."""

    status: str = "success"
    data: Dict
    message: str


class GoogleAuthRequest(BaseModel):
    """Schema for Google authentication request."""

    token: str = Field(..., description="Google OAuth access token")


class TokenData(BaseModel):
    """Schema for JWT token data."""

    sub: str
    exp: Optional[int] = None
    email: Optional[EmailStr] = None 