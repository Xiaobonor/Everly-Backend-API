"""Media service for the media module."""

import logging
import os
import uuid
from typing import Dict, Optional, Any

from fastapi import HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.modules.media.config import MediaConfig


class MediaService:
    """Media file handling service."""
    
    def __init__(self, config: MediaConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MediaService")
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
        os.makedirs(self.config.MEDIA_UPLOAD_PATH, exist_ok=True)
        
        self.logger.info("媒體服務初始化完成")
    
    async def upload_media_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Upload a media file and return the file information.
        
        Args:
            file: The uploaded file.
            
        Returns:
            Dictionary with file information including URL and metadata.
            
        Raises:
            HTTPException: If upload fails or file is invalid.
        """
        # Validate file type
        if file.content_type not in self.config.allowed_types:
            self.logger.error(f"Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} is not allowed"
            )
        
        # Read and validate file size
        file_content = await file.read()
        if len(file_content) > self.config.MAX_FILE_SIZE:
            self.logger.error(f"File too large: {len(file_content)} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {self.config.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'bin'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.config.MEDIA_UPLOAD_PATH, unique_filename)
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            # Determine file type category
            file_type = self._get_file_type_category(file.content_type)
            
            # Return file information
            file_url = f"{self.config.BASE_URL}/static/uploads/media/{unique_filename}"
            
            file_info = {
                "url": file_url,
                "filename": unique_filename,
                "original_filename": file.filename,
                "content_type": file.content_type,
                "file_type": file_type,
                "size": len(file_content),
                "path": file_path
            }
            
            self.logger.info(f"Media file uploaded successfully: {file_url}")
            return file_info
            
        except Exception as e:
            self.logger.error(f"Failed to save uploaded file: {str(e)}")
            # Clean up file if it was partially created
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded file"
            )
    
    def _get_file_type_category(self, content_type: str) -> str:
        """
        Determine the file type category based on content type.
        
        Args:
            content_type: The MIME type of the file.
            
        Returns:
            File type category (image, video, audio, or other).
        """
        if content_type in self.config.ALLOWED_IMAGE_TYPES:
            return "image"
        elif content_type in self.config.ALLOWED_VIDEO_TYPES:
            return "video"
        elif content_type in self.config.ALLOWED_AUDIO_TYPES:
            return "audio"
        else:
            return "other"
    
    async def delete_media_file(self, filename: str) -> bool:
        """
        Delete a media file.
        
        Args:
            filename: The filename to delete.
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            file_path = os.path.join(self.config.MEDIA_UPLOAD_PATH, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Media file deleted successfully: {filename}")
                return True
            else:
                self.logger.warning(f"File not found for deletion: {filename}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to delete file {filename}: {str(e)}")
            return False 