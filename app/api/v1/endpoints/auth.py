"""Authentication endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth import AuthResponse, GoogleAuthRequest
from app.schemas.user import UserResponse
from app.services.auth import (
    create_access_token,
    exchange_code_for_token,
    find_or_create_user,
    get_current_user,
    verify_google_token,
)
from app.db.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/google", response_model=AuthResponse)
async def login_with_google(auth_request: GoogleAuthRequest) -> Any:
    """
    Authenticate using Google OAuth.
    
    Args:
        auth_request: The authentication request containing the authorization code.
        
    Returns:
        Authentication response with access token.
    """
    try:
        # Exchange authorization code for access token
        token = await exchange_code_for_token(auth_request.code)
        
        # Verify token and get user info
        user_info = await verify_google_token(token)
        
        # Extract user data
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")
        google_id = user_info.get("sub")  # Google's user ID
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google authentication"
            )
        
        # Find or create user
        user = await find_or_create_user(
            email=email,
            name=name or email.split("@")[0],
            picture=picture,
            google_id=google_id
        )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return {
            "status": "success",
            "data": {
                "access_token": access_token,
                "token_type": "bearer"
            },
            "message": "Authentication successful"
        }
    except Exception as e:
        logger.error(f"Google authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current authenticated user information.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        User information.
    """
    # 將 User 實例轉換為字典，確保 id 被轉換為字符串
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "profile_picture": current_user.profile_picture,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "preferences": current_user.preferences or []
    } 