"""Media service for file uploads."""

import os
import uuid
import logging
import mimetypes
from typing import Dict, Optional

from fastapi import UploadFile, HTTPException, status
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

# 設定上傳目錄
UPLOAD_DIR = Path("static/uploads")
PROFILE_UPLOAD_DIR = UPLOAD_DIR / "profiles"
MEDIA_UPLOAD_DIR = UPLOAD_DIR / "media"


async def ensure_upload_dirs():
    """Ensure upload directories exist."""
    UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
    PROFILE_UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
    MEDIA_UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


async def upload_profile_image(file: UploadFile) -> str:
    """
    Upload a profile image file.
    
    Args:
        file: The uploaded file.
        
    Returns:
        URL to the uploaded file.
    """
    await ensure_upload_dirs()
    
    # 驗證文件類型
    valid_extensions = [".jpg", ".jpeg", ".png", ".gif"]
    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    
    if file_ext not in valid_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Supported formats: {', '.join(valid_extensions)}"
        )
    
    # 創建唯一文件名
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = PROFILE_UPLOAD_DIR / unique_filename
    
    try:
        # 寫入文件
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # 返回URL (相對於API根目錄)
        return f"/static/uploads/profiles/{unique_filename}"
    except Exception as e:
        logger.error(f"Error uploading profile image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not upload the file"
        )


async def upload_media_file(file: UploadFile) -> Dict:
    """
    Upload a media file (image, audio, or video).
    
    Args:
        file: The uploaded file.
        
    Returns:
        Dictionary with the file URL, type, and size.
    """
    await ensure_upload_dirs()
    
    # 驗證文件類型
    content_type = file.content_type or "application/octet-stream"
    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    
    # 如果沒有擴展名，嘗試從content_type猜測
    if not file_ext and content_type != "application/octet-stream":
        guess_ext = mimetypes.guess_extension(content_type)
        if guess_ext:
            file_ext = guess_ext
    
    # 檢查是否是支持的媒體類型
    media_type = "unknown"
    if content_type.startswith("image/"):
        media_type = "image"
        valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
    elif content_type.startswith("audio/"):
        media_type = "audio"
        valid_extensions = [".mp3", ".wav", ".ogg", ".aac", ".m4a"]
    elif content_type.startswith("video/"):
        media_type = "video"
        valid_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    
    if media_type == "unknown" or (file_ext and file_ext not in valid_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported media type. Please upload an image, audio, or video file."
        )
    
    # 創建唯一文件名
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = MEDIA_UPLOAD_DIR / unique_filename
    
    try:
        # 讀取文件內容
        content = await file.read()
        file_size = len(content)
        
        # 檢查文件大小（限制為20MB）
        max_size = 20 * 1024 * 1024  # 20 MB in bytes
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the limit (20MB)"
            )
        
        # 寫入文件
        async with aiofiles.open(file_path, "wb") as out_file:
            await out_file.write(content)
        
        # 返回文件信息
        return {
            "url": f"/static/uploads/media/{unique_filename}",
            "type": media_type,
            "size": file_size
        }
    except HTTPException:
        # 重新拋出HTTP異常
        raise
    except Exception as e:
        logger.error(f"Error uploading media file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not upload the file"
        ) 