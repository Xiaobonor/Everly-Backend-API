"""User endpoints."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

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
    # 將 User 實例轉換為字典，確保 id 被轉換為字符串
    preferences_list = []
    if current_user.preferences:
        for key, value in current_user.preferences.items():
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
    try:
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(current_user, field, value)
            
        current_user.save()
        
        preferences_list = []
        if current_user.preferences:
            for key, value in current_user.preferences.items():
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
                
        return {
            "status": "success",
            "data": user_data,
            "message": "User information updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating user: {e}")
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
    try:
        # 上傳圖片並獲取URL
        image_url = await upload_profile_image(file)
        
        # 更新用戶資料
        current_user.profile_picture = image_url
        current_user.save()
        
        preferences_list = []
        if current_user.preferences:
            for key, value in current_user.preferences.items():
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
        
        return {
            "status": "success",
            "data": user_data,
            "message": "Profile picture updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating profile picture: {e}")
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
    preferences_list = []
    if current_user.preferences:
        for key, value in current_user.preferences.items():
            preferences_list.append({"key": key, "value": value})
            
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
        Success response with updated preferences.
    """
    try:
        # 首先確保 preferences 是一個字典
        if current_user.preferences is None:
            current_user.preferences = {}
            
        # 更新 preferences
        pref_dict = preferences.to_dict()
        current_user.preferences.update(pref_dict)
        
        # 保存用戶
        current_user.save()
        
        # 將字典轉換為列表用於響應
        preferences_list = []
        for key, value in current_user.preferences.items():
            preferences_list.append({"key": key, "value": value})
            
        return {
            "status": "success",
            "data": {"preferences": preferences_list},
            "message": "User preferences updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user preferences"
        ) 