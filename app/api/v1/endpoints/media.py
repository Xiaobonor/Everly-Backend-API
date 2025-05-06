"""Media upload endpoints."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.services.auth import get_current_user
from app.services.media import upload_media_file
from app.db.models.user import User
from app.schemas.user import ApiResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    上傳媒體文件（圖片、音頻或視頻）以在日記條目中使用。
    
    Args:
        file: 媒體文件。
        current_user: 當前認證用戶。
        
    Returns:
        上傳的文件信息。
    """
    try:
        # 上傳媒體文件
        media_info = await upload_media_file(file)
        
        return {
            "status": "success",
            "data": media_info,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        logger.error(f"Error uploading media file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the file"
        ) 