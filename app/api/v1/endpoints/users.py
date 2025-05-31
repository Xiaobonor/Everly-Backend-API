"""User endpoints."""

import logging
import json
import base64
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.encoders import jsonable_encoder

from app.schemas.user import UserResponse, UserUpdate, UserPreferenceUpdate, PreferenceModel, ApiResponse
from app.services.auth import get_current_user
from app.services.media import upload_profile_image
from app.db.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me", response_model=ApiResponse)
async def get_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current authenticated user information.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        User information.
    """
    logger.info(f"API request GET /users/me - User ID: {current_user.id}")
    logger.debug(f"Getting user information - Request processing started")
    
    # Convert User instance to dict, ensuring id is a string
    preferences_list = []
    if current_user.preferences:
        logger.debug(f"Processing user preferences - {len(current_user.preferences)} items")
        for key, value in current_user.preferences.items():
            # 排除大型的 profileImage base64 數據，避免響應過大
            if key == "profileImage":
                logger.debug(f"Skipping large profileImage data - size: {len(str(value)) if value else 0} characters")
                continue
                
            # 如果值是二進制數據，轉換為Base64字符串
            if isinstance(value, bytes):
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
            
    logger.debug(f"User information retrieval successful - Response ready")
    logger.info(f"API request GET /users/me completed - User ID: {current_user.id}")
    
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
    logger.info(f"API request PUT /users/me - User ID: {current_user.id}")
    logger.debug(f"Updating user information - Request data: {user_update.dict(exclude_unset=True)}")
    
    try:
        update_data = user_update.dict(exclude_unset=True)
        
        logger.debug(f"Updating user fields: {', '.join(update_data.keys())}")
        for field, value in update_data.items():
            setattr(current_user, field, value)
            
        current_user.save()
        logger.debug(f"User information saved to the database")
        
        preferences_list = []
        if current_user.preferences:
            logger.debug(f"Processing user preferences - {len(current_user.preferences)} items")
            for key, value in current_user.preferences.items():
                # 排除大型的 profileImage base64 數據，避免響應過大
                if key == "profileImage":
                    logger.debug(f"跳過大型 profileImage 數據 - 數據大小: {len(str(value)) if value else 0} 字符")
                    continue
                    
                # 如果值是二進制數據，轉換為Base64字符串
                if isinstance(value, bytes):
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
        
        logger.debug(f"User information update successful - Response ready")
        logger.info(f"API request PUT /users/me completed - User ID: {current_user.id}")
                
        return {
            "status": "success",
            "data": user_data,
            "message": "User information updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating user information - User ID: {current_user.id}, Error: {str(e)}")
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
    logger.info(f"API request PUT /users/me/profile-picture - User ID: {current_user.id}")
    logger.debug(f"Updating profile picture - Filename: {file.filename}, Size: {file.size}, Content type: {file.content_type}")
    
    try:
        # Upload image and get URL
        logger.debug(f"Starting upload of profile picture to storage service")
        image_url = await upload_profile_image(file)
        logger.debug(f"Image uploaded successfully - URL: {image_url}")
        
        # 更新用戶資料
        current_user.profile_picture = image_url
        current_user.save()
        logger.debug(f"User profile picture URL updated and saved to database")
        
        preferences_list = []
        if current_user.preferences:
            logger.debug(f"處理用戶偏好設定 - 共 {len(current_user.preferences)} 項")
            for key, value in current_user.preferences.items():
                # 排除大型的 profileImage base64 數據，避免響應過大
                if key == "profileImage":
                    logger.debug(f"跳過大型 profileImage 數據 - 數據大小: {len(str(value)) if value else 0} 字符")
                    continue
                    
                # 如果值是二進制數據，轉換為Base64字符串
                if isinstance(value, bytes):
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
        
        logger.debug(f"User profile picture update successful - Response ready")
        logger.info(f"API request PUT /users/me/profile-picture completed - User ID: {current_user.id}")
        
        return {
            "status": "success",
            "data": user_data,
            "message": "Profile picture updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating profile picture - User ID: {current_user.id}, Error: {str(e)}")
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
    logger.info(f"API request GET /users/me/preferences - User ID: {current_user.id}")
    logger.debug(f"Getting user preferences - Request processing started")
    
    preferences_list = []
    if current_user.preferences:
        logger.debug(f"Processing user preferences - {len(current_user.preferences)} items")
        for key, value in current_user.preferences.items():
            # 排除大型的 profileImage base64 數據，避免響應過大
            if key == "profileImage":
                logger.debug(f"跳過大型 profileImage 數據 - 數據大小: {len(str(value)) if value else 0} 字符")
                continue
                
            # 如果值是二進制數據，轉換為Base64字符串
            if isinstance(value, bytes):
                value = base64.b64encode(value).decode('ascii')
            preferences_list.append({"key": key, "value": value})
    
    logger.debug(f"User preferences retrieval successful - Response ready")
    logger.info(f"API request GET /users/me/preferences completed - User ID: {current_user.id}")
            
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
    logger.info(f"API request PUT /users/me/preferences - User ID: {current_user.id}")

    # Determine how many fields need to be updated
    update_fields = [field for field, value in preferences.dict(exclude_unset=True, exclude_none=True).items() if value is not None]
    logger.debug(f"Updating user preferences - Request includes {len(update_fields)} updates: {', '.join(update_fields)}")
    
    try:
        # 確保用戶有偏好字典
        if not current_user.preferences:
        logger.debug("User has no existing preferences - creating new preferences dictionary")
            current_user.preferences = {}
            
        # 將偏好設定轉換為字典格式
        preferences_dict = preferences.to_dict()
        logger.debug(f"Converted preferences dict keys: {list(preferences_dict.keys())}")
        
        # 更新用戶偏好
        for key, value in preferences_dict.items():
            logger.debug(f"Updating preference: {key}")
            current_user.preferences[key] = value
            
        # 保存到數據庫
        current_user.save()
        logger.debug(f"User preferences saved to the database")
        
        # 準備響應數據
        preferences_list = []
        if current_user.preferences:
        logger.debug(f"Processing user preferences response - {len(current_user.preferences)} items")
            for key, value in current_user.preferences.items():
                # 排除大型的 profileImage base64 數據，避免響應過大
                if key == "profileImage":
                    logger.debug(f"跳過大型 profileImage 數據 - 數據大小: {len(str(value)) if value else 0} 字符")
                    continue
                    
                # 如果值是二進制數據，轉換為Base64字符串
                if isinstance(value, bytes):
                    value = base64.b64encode(value).decode('ascii')
                preferences_list.append({"key": key, "value": value})
        
        logger.debug(f"User preferences update successful - Response ready")
        logger.info(f"API request PUT /users/me/preferences completed - User ID: {current_user.id}")
        
        return {
            "status": "success",
            "data": preferences_list,
            "message": "User preferences updated successfully"
        }
    except UnicodeDecodeError as e:
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decoding error during user preferences update - User ID: {current_user.id}, Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Binary data must be Base64-encoded. Please convert binary data to a Base64 string before submitting."
        )
    except Exception as e:
        logger.error(f"Error updating user preferences - User ID: {current_user.id}, Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user preferences"
        )