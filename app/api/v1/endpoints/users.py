"""User endpoints."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.user import UserResponse, UserUpdate
from app.services.auth import get_current_user
from app.db.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me", response_model=UserResponse)
async def get_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current authenticated user information.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        User information.
    """
    # 將 User 實例轉換為字典，確保 id 被轉換為字符串
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "profile_picture": current_user.profile_picture,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "preferences": current_user.preferences or []
    }


@router.put("/me", response_model=UserResponse)
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
        
        # 將 User 實例轉換為字典，確保 id 被轉換為字符串
        return {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
            "profile_picture": current_user.profile_picture,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
            "preferences": current_user.preferences or []
        }
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user information"
        )


@router.get("/me/preferences", response_model=List[str])
async def get_user_preferences(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user preferences.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        List of user preferences.
    """
    return current_user.preferences or []


@router.put("/me/preferences", response_model=List[str])
async def update_user_preferences(
    preferences: List[str], current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update current user preferences.
    
    Args:
        preferences: The new list of preferences.
        current_user: The current authenticated user.
        
    Returns:
        Updated list of preferences.
    """
    try:
        current_user.preferences = preferences
        current_user.save()
        return current_user.preferences
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user preferences"
        ) 