"""Authentication schemas for request and response validation."""

from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for authentication token."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for token payload."""

    sub: Optional[str] = None
    email: Optional[str] = None


class GoogleAuthRequest(BaseModel):
    """Schema for Google authentication request."""

    code: str


class AuthResponse(BaseModel):
    """Schema for authentication response."""

    status: str = "success"
    data: Token
    message: Optional[str] = None 