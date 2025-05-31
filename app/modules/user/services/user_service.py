"""User service for the user module."""

import logging
import os
import uuid
from typing import Dict, Optional, Any

from fastapi import HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.modules.user.config import UserConfig
from app.db.models.user import User


class UserService:
    """User management service."""
    
    def __init__(self, config: UserConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.UserService")
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
        
        # Ensure upload directory exists
        os.makedirs(self.config.PROFILE_UPLOAD_PATH, exist_ok=True)
        
        self.logger.info("用戶服務初始化完成")
    
    async def upload_profile_image(self, file: UploadFile) -> str:
        """
        Upload a profile image and return the URL.
        
        Args:
            file: The uploaded image file.
            
        Returns:
            The URL of the uploaded image.
            
        Raises:
            HTTPException: If upload fails or file is invalid.
        """
        # Validate file type
        if file.content_type not in self.config.ALLOWED_IMAGE_TYPES:
            self.logger.error(f"Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} is not allowed. Allowed types: {', '.join(self.config.ALLOWED_IMAGE_TYPES)}"
            )
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > self.config.MAX_PROFILE_IMAGE_SIZE:
            self.logger.error(f"File too large: {len(file_content)} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {self.config.MAX_PROFILE_IMAGE_SIZE // (1024*1024)}MB"
            )
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.config.PROFILE_UPLOAD_PATH, unique_filename)
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            # Return full URL
            file_url = f"{self.config.BASE_URL}/static/uploads/profiles/{unique_filename}"
            
            self.logger.info(f"Profile image uploaded successfully: {file_url}")
            return file_url
            
        except Exception as e:
            self.logger.error(f"Failed to save uploaded file: {str(e)}")
            # Clean up file if it was partially created
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded file"
            )
    
    def format_user_data(self, user: User, include_large_data: bool = False) -> Dict[str, Any]:
        """
        Format user data for API response.
        
        Args:
            user: The user object.
            include_large_data: Whether to include large data like profile images.
            
        Returns:
            Formatted user data dictionary.
        """
        preferences_list = []
        if user.preferences:
            self.logger.debug(f"處理用戶偏好設定 - 共 {len(user.preferences)} 項")
            for key, value in user.preferences.items():
                # Skip large profile image data unless explicitly requested
                if key == "profileImage" and not include_large_data:
                    self.logger.debug(f"跳過大型 profileImage 數據 - 數據大小: {len(str(value)) if value else 0} 字符")
                    continue
                    
                # Convert binary data to Base64 string
                if isinstance(value, bytes):
                    import base64
                    value = base64.b64encode(value).decode('ascii')
                preferences_list.append({"key": key, "value": value})
        
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "profile_picture": user.profile_picture,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "preferences": preferences_list
        }
    
    async def update_user_preferences(
        self, 
        user: User, 
        preferences_dict: Dict[str, Any]
    ) -> User:
        """
        Update user preferences.
        
        Args:
            user: The user to update.
            preferences_dict: Dictionary of preferences to update.
            
        Returns:
            Updated user object.
        """
        # Ensure user has preferences dictionary
        if not user.preferences:
            self.logger.debug("用戶無現有偏好設定 - 創建新偏好字典")
            user.preferences = {}
            
        # Update preferences
        for key, value in preferences_dict.items():
            self.logger.debug(f"更新偏好設定: {key}")
            user.preferences[key] = value
            
        # Save to database
        user.save()
        self.logger.debug(f"用戶偏好設定已保存到數據庫")
        
        return user 