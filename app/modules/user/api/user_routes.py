"""User API routes."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.modules.user.services import UserService
from app.modules.user.config import UserConfig
from app.schemas.user import UserUpdate, UserPreferenceUpdate, ApiResponse
from app.db.models.user import User

# Import auth dependency from auth module
from app.modules.auth.api.auth_routes import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize user service with config
user_config = UserConfig.from_env()
user_service = UserService(user_config)


@router.get("/me", response_model=ApiResponse)
async def get_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current authenticated user information.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        User information.
    """
    logger.info(f"API 請求 GET /users/me - 用戶ID: {current_user.id}")
    logger.debug(f"獲取用戶信息 - 請求開始處理")
    
    user_data = user_service.format_user_data(current_user)
    
    logger.debug(f"用戶信息獲取成功 - 響應準備完成")
    logger.info(f"API 請求 GET /users/me 完成 - 用戶ID: {current_user.id}")
    
    return {
        "status": "success",
        "data": user_data,
        "message": "User information retrieved successfully"
    }


@router.put("/me", response_model=ApiResponse)
async def update_user_me(
    user_update: UserUpdate, current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update current authenticated user information.
    
    Args:
        user_update: The user data to update.
        current_user: The current authenticated user.
        
    Returns:
        Updated user information.
    """
    logger.info(f"API 請求 PUT /users/me - 用戶ID: {current_user.id}")
    logger.debug(f"更新用戶信息 - 請求數據: {user_update.dict(exclude_unset=True)}")
    
    try:
        update_data = user_update.dict(exclude_unset=True)
        
        logger.debug(f"更新用戶字段: {', '.join(update_data.keys())}")
        for field, value in update_data.items():
            setattr(current_user, field, value)
            
        current_user.save()
        logger.debug(f"用戶信息已保存到數據庫")
        
        user_data = user_service.format_user_data(current_user)
        
        logger.debug(f"用戶信息更新成功 - 響應準備完成")
        logger.info(f"API 請求 PUT /users/me 完成 - 用戶ID: {current_user.id}")
                
        return {
            "status": "success",
            "data": user_data,
            "message": "User information updated successfully"
        }
    except Exception as e:
        logger.error(f"更新用戶信息時發生錯誤 - 用戶ID: {current_user.id}, 錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user information"
        )


@router.put("/me/profile-picture", response_model=ApiResponse)
async def update_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update user profile picture.
    
    Args:
        file: The image file to upload.
        current_user: The current authenticated user.
        
    Returns:
        Success response with the new profile picture URL.
    """
    logger.info(f"API 請求 PUT /users/me/profile-picture - 用戶ID: {current_user.id}")
    logger.debug(f"更新用戶頭像 - 文件名: {file.filename}, 文件大小: {file.size}, 內容類型: {file.content_type}")
    
    try:
        # Upload image and get URL
        logger.debug(f"開始上傳頭像圖片到存儲服務")
        image_url = await user_service.upload_profile_image(file)
        logger.debug(f"圖片上傳成功 - URL: {image_url}")
        
        # Update user profile
        current_user.profile_picture = image_url
        current_user.save()
        logger.debug(f"用戶頭像URL已更新並保存到數據庫")
        
        user_data = user_service.format_user_data(current_user)
        
        logger.debug(f"用戶頭像更新成功 - 響應準備完成")
        logger.info(f"API 請求 PUT /users/me/profile-picture 完成 - 用戶ID: {current_user.id}")
        
        return {
            "status": "success",
            "data": user_data,
            "message": "Profile picture updated successfully"
        }
    except Exception as e:
        logger.error(f"更新用戶頭像時發生錯誤 - 用戶ID: {current_user.id}, 錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating profile picture"
        )


@router.get("/me/preferences", response_model=ApiResponse)
async def get_user_preferences(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user preferences.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        List of user preferences.
    """
    logger.info(f"API 請求 GET /users/me/preferences - 用戶ID: {current_user.id}")
    logger.debug(f"獲取用戶偏好設定 - 請求開始處理")
    
    user_data = user_service.format_user_data(current_user)
    preferences_list = user_data.get("preferences", [])
    
    logger.debug(f"用戶偏好設定獲取成功 - 響應準備完成")
    logger.info(f"API 請求 GET /users/me/preferences 完成 - 用戶ID: {current_user.id}")
            
    return {
        "status": "success",
        "data": preferences_list,
        "message": "User preferences retrieved successfully"
    }


@router.put("/me/preferences", response_model=ApiResponse)
async def update_user_preferences(
    preferences: UserPreferenceUpdate, current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update current user preferences.
    
    Args:
        preferences: The preferences to update.
        current_user: The current authenticated user.
        
    Returns:
        Updated list of user preferences.
    """
    logger.info(f"API 請求 PUT /users/me/preferences - 用戶ID: {current_user.id}")
    
    # Check how many fields need to be updated
    update_fields = [field for field, value in preferences.dict(exclude_unset=True, exclude_none=True).items() if value is not None]
    logger.debug(f"更新用戶偏好設定 - 請求包含 {len(update_fields)} 個更新項: {', '.join(update_fields)}")
    
    try:
        # Convert preferences to dictionary format
        preferences_dict = preferences.to_dict()
        logger.debug(f"轉換的偏好設定字典: {list(preferences_dict.keys())}")
        
        # Update user preferences using service
        await user_service.update_user_preferences(current_user, preferences_dict)
        
        # Prepare response data
        user_data = user_service.format_user_data(current_user)
        preferences_list = user_data.get("preferences", [])
        
        logger.debug(f"用戶偏好設定更新成功 - 響應準備完成")
        logger.info(f"API 請求 PUT /users/me/preferences 完成 - 用戶ID: {current_user.id}")
        
        return {
            "status": "success",
            "data": preferences_list,
            "message": "User preferences updated successfully"
        }
    except UnicodeDecodeError as e:
        logger.error(f"用戶偏好設定更新時發生Unicode解碼錯誤 - 用戶ID: {current_user.id}, 錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="二進制數據必須使用Base64編碼。請將二進制數據轉換為Base64字符串後再提交。"
        )
    except Exception as e:
        logger.error(f"用戶偏好設定更新時發生錯誤 - 用戶ID: {current_user.id}, 錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用戶偏好設定時發生錯誤"
        ) 