"""Authentication service for the auth module."""

import datetime
import logging
from typing import Dict, Optional

import jwt
import httpx
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.modules.auth.config import AuthConfig
from app.modules.auth.schemas import TokenData
from app.db.models.user import User


class AuthService:
    """Authentication service."""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AuthService")
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._redis: Optional[Redis] = None
    
    def initialize(
        self, 
        db: AsyncIOMotorDatabase, 
        redis: Optional[Redis] = None
    ) -> None:
        """Initialize the service with database and cache connections."""
        self._db = db
        self._redis = redis
        self.logger.info("認證服務初始化完成")
    
    async def verify_google_token(self, token: str) -> Dict:
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
        self.logger.info(f"Verifying Google token with length: {token_length}")
        
        if not token:
            self.logger.error("Empty Google token provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google token is required"
            )
        
        try:
            self.logger.debug(f"Sending GET request to {google_user_info_url}")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    google_user_info_url,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                # 詳細記錄響應情況
                status_code = response.status_code
                self.logger.info(f"Google user info response status: {status_code}")
                
                if status_code != 200:
                    # 記錄錯誤響應內容以幫助診斷
                    try:
                        error_details = response.json()
                        self.logger.error(f"Google user info error details: {error_details}")
                    except Exception:
                        self.logger.error(f"Google user info error, raw response: {response.text}")
                
                response.raise_for_status()
                
                user_info = response.json()
                self.logger.info(f"Successfully retrieved user info for email: {user_info.get('email', 'unknown')}")
                return user_info
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error during token verification: {e.response.status_code} {e.response.reason_phrase}")
            try:
                error_body = e.response.json()
                self.logger.error(f"Error response body: {error_body}")
            except Exception:
                self.logger.error(f"Error response text: {e.response.text}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate Google credentials: {e.response.reason_phrase}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error verifying Google token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate Google credentials"
            )

    async def find_or_create_user(
        self, 
        email: str, 
        name: str, 
        picture: Optional[str] = None, 
        google_id: Optional[str] = None
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
            self.logger.info(f"創建新用戶: {email}")
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
                    self.logger.info(f"Converting preferences from list to dict for user: {user.id}")
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
            self.logger.info(f"更新現有用戶: {email}")
        
        return user

    def create_access_token(self, data: Dict, expires_delta: Optional[int] = None) -> str:
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
            minutes=expires_delta or self.config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        
        return jwt.encode(
            to_encode,
            self.config.JWT_SECRET_KEY,
            algorithm=self.config.JWT_ALGORITHM
        )

    async def get_current_user_by_token(self, token: str) -> User:
        """
        Get the current authenticated user from JWT token.
        
        Args:
            token: JWT token string.
            
        Returns:
            User object.
            
        Raises:
            HTTPException: If authentication fails.
        """
        try:
            self.logger.debug(f"Decoding JWT token for authentication")
            
            payload = jwt.decode(
                token,
                self.config.JWT_SECRET_KEY,
                algorithms=[self.config.JWT_ALGORITHM]
            )
            
            user_id = payload.get("sub")
            if user_id is None:
                self.logger.error("No user ID found in JWT token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            self.logger.debug(f"Looking up user with ID: {user_id}")
            
            # 嘗試不同方式查找用戶，處理 ObjectId 轉換問題
            user = None
            try:
                # 方法1：直接用字符串 ID 查詢
                user = User.objects(id=user_id).first()
            except Exception as e:
                self.logger.debug(f"Direct string ID lookup failed: {e}")
                
            if not user:
                try:
                    # 方法2：如果是 ObjectId 字符串，嘗試轉換
                    from bson import ObjectId
                    if ObjectId.is_valid(user_id):
                        object_id = ObjectId(user_id)
                        user = User.objects(id=object_id).first()
                        self.logger.debug(f"Found user using ObjectId conversion")
                except Exception as e:
                    self.logger.debug(f"ObjectId conversion failed: {e}")
                    
            if not user:
                try:
                    # 方法3：嘗試用 email 查詢（fallback）
                    email = payload.get("email")
                    if email:
                        user = User.objects(email=email).first()
                        self.logger.debug(f"Found user using email fallback: {email}")
                except Exception as e:
                    self.logger.debug(f"Email fallback failed: {e}")
            
            if user is None:
                self.logger.error(f"User not found with ID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            if not user.is_active:
                self.logger.error(f"User {user_id} is inactive")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Inactive user",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            self.logger.debug(f"Successfully authenticated user: {user.id}")
            return user
            
        except jwt.PyJWTError as e:
            self.logger.error(f"JWT error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            self.logger.error(f"Unexpected authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"}
            ) 