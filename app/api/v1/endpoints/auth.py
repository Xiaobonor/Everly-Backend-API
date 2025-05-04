"""Authentication endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth import AuthResponse, GoogleAuthRequest
from app.schemas.user import UserResponse
from app.services.auth import (
    create_access_token,
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
    Authenticate using Google OAuth token.
    
    Args:
        auth_request: The authentication request containing the Google OAuth access token.
        
    Returns:
        Authentication response with JWT access token.
    """
    logger.info("Received Google authentication request")
    
    # 記錄認證請求的基本信息
    token_length = len(auth_request.token) if auth_request.token else 0
    logger.info(f"Google OAuth token length: {token_length}")
    
    if not auth_request.token:
        logger.error("Empty Google OAuth token received")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth token is required"
        )
    
    try:
        # 記錄開始驗證令牌並獲取用戶信息
        logger.info("Starting token verification and user info retrieval")
        
        # Verify token and get user info
        user_info = await verify_google_token(auth_request.token)
        logger.info("Successfully verified token and retrieved user info")
        
        # Extract user data
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")
        google_id = user_info.get("sub")  # Google's user ID
        
        # 記錄用戶信息
        logger.info(f"User info retrieved - email: {email}, name: {name}, google_id present: {bool(google_id)}")
        
        if not email:
            logger.error("Email not provided by Google authentication")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google authentication"
            )
        
        # 記錄查找或創建用戶
        logger.info(f"Finding or creating user with email: {email}")
        
        # Find or create user
        user = await find_or_create_user(
            email=email,
            name=name or email.split("@")[0],
            picture=picture,
            google_id=google_id
        )
        logger.info(f"User found or created with ID: {user.id}")
        
        # 記錄創建訪問令牌
        logger.info("Creating JWT access token")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        logger.info("JWT access token created successfully")
        
        return {
            "status": "success",
            "data": {
                "access_token": access_token,
                "token_type": "bearer"
            },
            "message": "Authentication successful"
        }
    except Exception as e:
        # 記錄具體的錯誤信息和堆棧跟踪
        logger.error(f"Google authentication error: {e}", exc_info=True)
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