"""Media API routes."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.modules.media.services import MediaService
from app.modules.media.config import MediaConfig
from app.schemas.user import ApiResponse
from app.db.models.user import User

# Import auth dependency from auth module
from app.modules.auth.api.auth_routes import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize media service with config
media_config = MediaConfig.from_env()
media_service = MediaService(media_config)


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
    logger.info(f"API 請求 POST /media/upload - 用戶ID: {current_user.id}")
    logger.debug(f"上傳媒體文件 - 文件名: {file.filename}, 文件大小: {file.size}, 內容類型: {file.content_type}")
    
    try:
        # 上傳媒體文件
        logger.debug(f"開始處理媒體文件上傳 - 文件名: {file.filename}")
        media_info = await media_service.upload_media_file(file)
        logger.debug(f"媒體文件上傳成功 - URL: {media_info.get('url', 'N/A')}")
        
        logger.info(f"API 請求 POST /media/upload 完成 - 用戶ID: {current_user.id}, 文件名: {file.filename}")
        return {
            "status": "success",
            "data": media_info,
            "message": "File uploaded successfully"
        }
    except UnicodeDecodeError as e:
        # 特別處理Unicode編碼錯誤
        error_details = f"Unicode 解碼錯誤: {str(e)}"
        logger.error(f"{error_details} - 用戶ID: {current_user.id}, 文件名: {file.filename}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File encoding error. Make sure you are uploading a valid binary file."
        )
    except HTTPException:
        # 直接重新拋出HTTP異常
        logger.warning(f"上傳媒體文件時發生HTTP異常 - 用戶ID: {current_user.id}, 文件名: {file.filename}")
        raise
    except Exception as e:
        # 記錄詳細的異常信息
        error_type = type(e).__name__
        error_details = str(e)
        logger.error(f"上傳媒體文件時發生錯誤 - 錯誤類型: {error_type}, 錯誤信息: {error_details}, 用戶ID: {current_user.id}, 文件名: {file.filename}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the file"
        ) 