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
    
    # 記錄令牌驗證嘗試
    token_length = len(token) if token else 0
    logger.info(f"Verifying Google token with length: {token_length}")
    
    if not token:
        logger.error("Empty Google token provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token is required"
        )
    
    try:
        logger.debug(f"Sending GET request to {google_user_info_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                google_user_info_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # 詳細記錄響應情況
            status_code = response.status_code
            logger.info(f"Google user info response status: {status_code}")
            
            if status_code != 200:
                # 記錄錯誤響應內容以幫助診斷
                try:
                    error_details = response.json()
                    logger.error(f"Google user info error details: {error_details}")
                except Exception:
                    logger.error(f"Google user info error, raw response: {response.text}")
            
            response.raise_for_status()
            
            user_info = response.json()
            logger.info(f"Successfully retrieved user info for email: {user_info.get('email', 'unknown')}")
            return user_info
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during token verification: {e.response.status_code} {e.response.reason_phrase}")
        try:
            error_body = e.response.json()
            logger.error(f"Error response body: {error_body}")
        except Exception:
            logger.error(f"Error response text: {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate Google credentials: {e.response.reason_phrase}"
        )
    except Exception as e:
        logger.error(f"Unexpected error verifying Google token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate Google credentials"
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
            last_login=datetime.datetime.utcnow(),
            preferences={}  # 初始化為空字典
        )
        user.save()
    else:
        # Update existing user
        user.last_login = datetime.datetime.utcnow()
        if google_id and not user.google_id:
            user.google_id = google_id
        if picture and not user.profile_picture:
            user.profile_picture = picture
            
        # 處理 preferences 欄位從列表轉為字典的遷移
        if hasattr(user, 'preferences'):
            # 檢查 preferences 是否為列表，如果是列表則轉換為字典
            if isinstance(user.preferences, list):
                logger.info(f"Converting preferences from list to dict for user: {user.id}")
                # 將舊的列表格式轉為新的字典格式
                prefs_dict = {}
                for i, pref in enumerate(user.preferences):
                    if isinstance(pref, str):
                        # 如果是字符串，則使用索引作為鍵
                        prefs_dict[f"pref_{i}"] = pref
                user.preferences = prefs_dict
            elif user.preferences is None:
                # 如果 preferences 為 None，設置為空字典
                user.preferences = {}
                
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