"""Media upload endpoints."""

import logging
import sys
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
    Upload media files (images, audio, or video) for use in diary entries.

    Args:
        file: The media file.
        current_user: The currently authenticated user.

    Returns:
        Uploaded file information.
    """
    logger.info(f"API request POST /media/upload - User ID: {current_user.id}")
    logger.debug(f"Uploading media file - Filename: {file.filename}, Size: {file.size}, Content type: {file.content_type}")
    
    try:
        # 上傳媒體文件
        logger.debug(f"開始處理媒體文件上傳 - 文件名: {file.filename}")
        media_info = await upload_media_file(file)
        logger.debug(f"媒體文件上傳成功 - URL: {media_info.get('url', 'N/A')}")
        
        logger.info(f"API 請求 POST /media/upload 完成 - 用戶ID: {current_user.id}, 文件名: {file.filename}")
        return {
            "status": "success",
            "data": media_info,
            "message": "File uploaded successfully"
        }
    except UnicodeDecodeError as e:
        # Handle Unicode decoding errors specifically
        error_details = f"Unicode decode error: {str(e)}"
        logger.error(f"{error_details} - User ID: {current_user.id}, Filename: {file.filename}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File encoding error. Make sure you are uploading a valid binary file."
        )
    except HTTPException:
        # Re-raise HTTP exceptions directly
        logger.warning(f"HTTP exception occurred during file upload - User ID: {current_user.id}, Filename: {file.filename}")
        raise
    except Exception as e:
        # Log detailed exception information
        error_type = type(e).__name__
        error_details = str(e)
        logger.error(f"Error occurred while uploading media file - Error type: {error_type}, Error detail: {error_details}, User ID: {current_user.id}, Filename: {file.filename}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the file"
        ) 