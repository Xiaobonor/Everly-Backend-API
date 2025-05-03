"""Authentication service."""

import datetime
import logging
from typing import Dict, Optional, Tuple

import jwt
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.db.models.user import User

logger = logging.getLogger(__name__)

# Setup Bearer token authentication
security = HTTPBearer()


async def verify_google_token(token: str) -> Dict:
    """
    Verify Google OAuth token and get user info.
    
    Args:
        token: The Google OAuth token.
        
    Returns:
        Dictionary with user information.
        
    Raises:
        HTTPException: If token verification fails.
    """
    google_user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                google_user_info_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            
            user_info = response.json()
            return user_info
    except Exception as e:
        logger.error(f"Error verifying Google token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate Google credentials"
        )


async def exchange_code_for_token(code: str) -> str:
    """
    Exchange authorization code for access token.
    
    Args:
        code: The authorization code from Google OAuth.
        
    Returns:
        Access token.
        
    Raises:
        HTTPException: If token exchange fails.
    """
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data["access_token"]
    except Exception as e:
        logger.error(f"Error exchanging code for token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not exchange code for token"
        )


async def find_or_create_user(
    email: str, name: str, picture: Optional[str] = None, google_id: Optional[str] = None
) -> User:
    """
    Find a user by email or create a new one.
    
    Args:
        email: The user's email.
        name: The user's name.
        picture: Optional profile picture URL.
        google_id: Optional Google ID.
        
    Returns:
        User object.
    """
    # Try to find by email first
    user = User.get_by_email(email)
    
    if not user and google_id:
        # Try to find by Google ID if provided
        user = User.get_by_google_id(google_id)
    
    if not user:
        # Create new user
        user = User(
            email=email,
            full_name=name,
            profile_picture=picture,
            google_id=google_id,
            last_login=datetime.datetime.utcnow()
        )
        user.save()
    else:
        # Update existing user
        user.last_login = datetime.datetime.utcnow()
        if google_id and not user.google_id:
            user.google_id = google_id
        if picture and not user.profile_picture:
            user.profile_picture = picture
        user.save()
    
    return user


def create_access_token(data: Dict, expires_delta: Optional[int] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token.
        expires_delta: Optional expiration time in seconds.
        
    Returns:
        JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=expires_delta or settings.JWT_EXPIRATION_SECONDS
    )
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials.
        
    Returns:
        User object.
        
    Raises:
        HTTPException: If authentication fails.
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user = User.objects(id=user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        return user
    except jwt.PyJWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        ) 