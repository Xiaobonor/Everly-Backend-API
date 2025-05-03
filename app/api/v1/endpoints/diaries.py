"""Diary endpoints."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.diary import (
    DiaryEntryCreate,
    DiaryEntryList,
    DiaryEntryResponse,
    DiaryEntrySearchParams,
    DiaryEntryUpdate,
)
from app.services.auth import get_current_user
from app.db.models.diary import DiaryEntry
from app.db.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=DiaryEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_diary_entry(
    entry: DiaryEntryCreate, current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new diary entry.
    
    Args:
        entry: The diary entry data.
        current_user: The current authenticated user.
        
    Returns:
        Created diary entry.
    """
    try:
        # Create the diary entry
        new_entry = DiaryEntry(
            user=current_user,
            title=entry.title,
            content=entry.content,
            content_type=entry.content_type,
            location=entry.location,
            location_name=entry.location_name,
            tags=entry.tags
        )
        
        # Add media content if provided
        if entry.media_content:
            from app.db.models.diary import MediaContent
            
            for media in entry.media_content:
                media_content = MediaContent(
                    url=str(media.url),
                    content_type=media.content_type,
                    thumbnail_url=str(media.thumbnail_url) if media.thumbnail_url else None,
                    description=media.description,
                    location=media.location
                )
                new_entry.media_content.append(media_content)
        
        new_entry.save()
        
        # TODO: Schedule AI analysis of the entry content
        
        # 使用to_dict方法，確保ObjectId和User對象被正確轉換為字符串
        return new_entry.to_dict()
    except Exception as e:
        logger.error(f"Error creating diary entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the diary entry"
        )


@router.get("", response_model=DiaryEntryList)
async def get_diary_entries(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get paginated list of diary entries for the current user.
    
    Args:
        page: Page number (1-indexed).
        limit: Number of items per page.
        current_user: The current authenticated user.
        
    Returns:
        List of diary entries.
    """
    try:
        skip = (page - 1) * limit
        
        # Get total count
        total = DiaryEntry.objects(user=current_user.id).count()
        
        # Get paginated entries
        entries = DiaryEntry.get_by_user(
            user_id=current_user.id, 
            limit=limit, 
            skip=skip
        )
        
        # 轉換為字典列表
        entry_dicts = [entry.to_dict() for entry in entries]
        
        return {
            "items": entry_dicts,
            "total": total,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error retrieving diary entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving diary entries"
        )


@router.get("/{entry_id}", response_model=DiaryEntryResponse)
async def get_diary_entry(
    entry_id: str, current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific diary entry by ID.
    
    Args:
        entry_id: The ID of the diary entry.
        current_user: The current authenticated user.
        
    Returns:
        Diary entry.
    """
    entry = DiaryEntry.get_by_id(entry_id=entry_id, user_id=current_user.id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary entry not found"
        )
    
    # 使用to_dict方法轉換為字典
    return entry.to_dict()


@router.put("/{entry_id}", response_model=DiaryEntryResponse)
async def update_diary_entry(
    entry_id: str,
    entry_update: DiaryEntryUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a diary entry.
    
    Args:
        entry_id: The ID of the diary entry to update.
        entry_update: The diary entry data to update.
        current_user: The current authenticated user.
        
    Returns:
        Updated diary entry.
    """
    try:
        entry = DiaryEntry.get_by_id(entry_id=entry_id, user_id=current_user.id)
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary entry not found"
            )
        
        update_data = entry_update.dict(exclude_unset=True)
        
        # Handle media content separately
        media_content = update_data.pop("media_content", None)
        
        # Update fields
        for field, value in update_data.items():
            setattr(entry, field, value)
        
        # Update media content if provided
        if media_content is not None:
            from app.db.models.diary import MediaContent
            
            entry.media_content = []
            for media in media_content:
                media_obj = MediaContent(
                    url=str(media.url),
                    content_type=media.content_type,
                    thumbnail_url=str(media.thumbnail_url) if media.thumbnail_url else None,
                    description=media.description,
                    location=media.location
                )
                entry.media_content.append(media_obj)
        
        entry.save()
        
        # TODO: Schedule re-analysis of the entry content if it changed
        
        # 使用to_dict方法轉換為字典
        return entry.to_dict()
    except Exception as e:
        logger.error(f"Error updating diary entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the diary entry"
        )


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diary_entry(
    entry_id: str, current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a diary entry.
    
    Args:
        entry_id: The ID of the diary entry to delete.
        current_user: The current authenticated user.
    """
    entry = DiaryEntry.get_by_id(entry_id=entry_id, user_id=current_user.id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary entry not found"
        )
    
    try:
        entry.delete()
    except Exception as e:
        logger.error(f"Error deleting diary entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the diary entry"
        )


@router.post("/search", response_model=DiaryEntryList)
async def search_diary_entries(
    search_params: DiaryEntrySearchParams,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Search diary entries with various filters.
    
    Args:
        search_params: Search parameters.
        page: Page number (1-indexed).
        limit: Number of items per page.
        current_user: The current authenticated user.
        
    Returns:
        List of matching diary entries.
    """
    try:
        skip = (page - 1) * limit
        query = {"user": current_user.id}
        
        # Apply filters
        if search_params.query:
            query["$text"] = {"$search": search_params.query}
            
        if search_params.tags:
            query["tags__in"] = search_params.tags
            
        if search_params.start_date:
            query["created_at__gte"] = search_params.start_date
            
        if search_params.end_date:
            query["created_at__lte"] = search_params.end_date
            
        if search_params.sentiment_min is not None:
            query["sentiment_score__gte"] = search_params.sentiment_min
            
        if search_params.sentiment_max is not None:
            query["sentiment_score__lte"] = search_params.sentiment_max
            
        # Location search is complex and requires geo queries
        if search_params.location and search_params.radius:
            query["location__near"] = {
                "point": search_params.location,
                "maxDistance": search_params.radius * 1000  # Convert km to m
            }
        
        # Get total count
        total = DiaryEntry.objects(**query).count()
        
        # Get paginated entries
        entries = DiaryEntry.objects(**query).order_by("-created_at").skip(skip).limit(limit)
        
        # 轉換為字典列表
        entry_dicts = [entry.to_dict() for entry in entries]
        
        return {
            "items": entry_dicts,
            "total": total,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error searching diary entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching diary entries"
        ) 