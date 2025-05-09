"""Authentication endpoints."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth import AuthResponse, GoogleAuthRequest, AuthData
from app.schemas.user import UserResponse, ApiResponse
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
    logger.info("API 請求 POST /auth/google - 開始處理 Google 認證")
    
    # 記錄認證請求的基本信息
    token_length = len(auth_request.token) if auth_request.token else 0
    logger.info(f"Google OAuth 令牌長度: {token_length}")
    
    if not auth_request.token:
        logger.error("收到空的 Google OAuth 令牌")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth token is required"
        )
    
    try:
        # 記錄開始驗證令牌並獲取用戶信息
        logger.info("開始驗證令牌並獲取用戶信息")
        
        # Verify token and get user info
        user_info = await verify_google_token(auth_request.token)
        logger.info("成功驗證令牌並獲取用戶信息")
        
        # Extract user data
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")
        google_id = user_info.get("sub")  # Google's user ID
        
        # 記錄用戶信息
        logger.info(f"獲取到用戶信息 - 郵箱: {email}, 姓名: {name}, 是否有Google ID: {bool(google_id)}")
        
        if not email:
            logger.error("Google 認證未提供郵箱")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google authentication"
            )
        
        # 記錄查找或創建用戶
        logger.info(f"查找或創建郵箱為 {email} 的用戶")
        
        # Find or create user
        user = await find_or_create_user(
            email=email,
            name=name or email.split("@")[0],
            picture=picture,
            google_id=google_id
        )
        logger.info(f"已找到或創建用戶，ID: {user.id}")
        
        # 記錄創建訪問令牌
        logger.info("創建 JWT 訪問令牌")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        logger.info("JWT 訪問令牌創建成功")
        
        auth_data = AuthData(
            access_token=access_token,
            token_type="bearer"
        )
        
        logger.info(f"API 請求 POST /auth/google 完成 - 用戶 {email} 登入成功")
        
        return AuthResponse(
            status="success",
            data=auth_data,
            message="Authentication successful"
        )
    except Exception as e:
        # 記錄具體的錯誤信息和堆棧跟踪
        logger.error(f"Google 認證錯誤: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.get("/me", response_model=ApiResponse)
async def get_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current authenticated user information.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        User information.
    """
    logger.info(f"API 請求 GET /auth/me - 用戶ID: {current_user.id}")
    logger.debug(f"獲取當前認證用戶信息 - 請求開始處理")
    
    preferences_list = []
    if current_user.preferences:
        logger.debug(f"處理用戶偏好設定 - 共 {len(current_user.preferences)} 項")
        for key, value in current_user.preferences.items():
            if isinstance(value, bytes):
                import base64
                value = base64.b64encode(value).decode('ascii')
            preferences_list.append({"key": key, "value": value})
    
    user_data = {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "profile_picture": current_user.profile_picture,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "preferences": preferences_list
    }
    
    logger.debug(f"用戶信息獲取成功 - 響應準備完成")
    logger.info(f"API 請求 GET /auth/me 完成 - 用戶ID: {current_user.id}")
            
    return {
        "status": "success",
        "data": user_data,
        "message": "User information retrieved successfully"
    } 