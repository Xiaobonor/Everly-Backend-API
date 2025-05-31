"""Diary service for the diary module."""

import logging
from typing import Dict, List, Optional, Any

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.modules.diary.config import DiaryConfig
from app.db.models.diary import Diary, DiaryEntry
from app.db.models.user import User
from app.schemas.diary import DiaryEntrySearchParams


class DiaryService:
    """Diary and diary entry management service."""
    
    def __init__(self, config: DiaryConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.DiaryService")
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
        self.logger.info("日記服務初始化完成")
    
    def get_user_diaries(self, user: User) -> List[Dict[str, Any]]:
        """
        Get all diaries for a user.
        
        Args:
            user: The user object.
            
        Returns:
            List of diary dictionaries.
        """
        try:
            diaries = Diary.get_by_user(user_id=user.id)
            return [diary.to_dict() for diary in diaries]
        except Exception as e:
            self.logger.error(f"Error getting user diaries: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving diaries"
            )
    
    def create_diary(self, user: User, title: str, description: Optional[str] = None, cover_image: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new diary for a user.
        
        Args:
            user: The user object.
            title: Diary title.
            description: Optional diary description.
            cover_image: Optional cover image URL.
            
        Returns:
            Created diary dictionary.
        """
        try:
            new_diary = Diary(
                user=user,
                title=title,
                description=description,
                cover_image=cover_image
            )
            new_diary.save()
            return new_diary.to_dict()
        except Exception as e:
            self.logger.error(f"Error creating diary: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating diary"
            )
    
    def get_diary_by_id(self, diary_id: str, user: User) -> Optional[Dict[str, Any]]:
        """
        Get a diary by ID for a specific user.
        
        Args:
            diary_id: The diary ID.
            user: The user object.
            
        Returns:
            Diary dictionary or None if not found.
        """
        try:
            diary = Diary.get_by_id(diary_id=diary_id, user_id=user.id)
            return diary.to_dict() if diary else None
        except Exception as e:
            self.logger.error(f"Error getting diary by ID: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving diary"
            )
    
    def update_diary(self, diary_id: str, user: User, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a diary for a specific user.
        
        Args:
            diary_id: The diary ID.
            user: The user object.
            update_data: Dictionary of fields to update.
            
        Returns:
            Updated diary dictionary or None if not found.
        """
        try:
            diary = Diary.get_by_id(diary_id=diary_id, user_id=user.id)
            if not diary:
                return None
            
            for field, value in update_data.items():
                setattr(diary, field, value)
            
            diary.save()
            return diary.to_dict()
        except Exception as e:
            self.logger.error(f"Error updating diary: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating diary"
            )
    
    def delete_diary(self, diary_id: str, user: User) -> bool:
        """
        Delete a diary for a specific user.
        
        Args:
            diary_id: The diary ID.
            user: The user object.
            
        Returns:
            True if deleted, False if not found.
        """
        try:
            diary = Diary.get_by_id(diary_id=diary_id, user_id=user.id)
            if not diary:
                return False
            
            diary.delete()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting diary: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting diary"
            )
    
    def get_diary_entries(self, diary_id: str, user: User, page: int = 1, limit: int = 10, sort: str = "desc") -> Dict[str, Any]:
        """
        Get diary entries for a specific diary.
        
        Args:
            diary_id: The diary ID.
            user: The user object.
            page: Page number.
            limit: Number of entries per page.
            sort: Sort order (asc or desc).
            
        Returns:
            Dictionary with entries and pagination info.
        """
        try:
            diary = Diary.get_by_id(diary_id=diary_id, user_id=user.id)
            if not diary:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Diary not found"
                )
            
            # Validate pagination parameters
            limit = min(limit, self.config.MAX_PAGE_SIZE)
            
            entries = DiaryEntry.get_by_diary_paginated(
                diary_id=diary_id,
                page=page,
                limit=limit,
                sort_order=sort
            )
            
            total_count = DiaryEntry.count_by_diary(diary_id=diary_id)
            total_pages = (total_count + limit - 1) // limit
            
            return {
                "entries": [entry.to_dict() for entry in entries],
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_entries": total_count,
                    "entries_per_page": limit
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting diary entries: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving diary entries"
            )
    
    def create_diary_entry(self, diary_id: str, user: User, title: str, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new diary entry.
        
        Args:
            diary_id: The diary ID.
            user: The user object.
            title: Entry title.
            content: Entry content.
            media_urls: Optional list of media URLs.
            
        Returns:
            Created diary entry dictionary.
        """
        try:
            diary = Diary.get_by_id(diary_id=diary_id, user_id=user.id)
            if not diary:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Diary not found"
                )
            
            new_entry = DiaryEntry(
                diary=diary,
                title=title,
                content=content,
                media_urls=media_urls or []
            )
            new_entry.save()
            return new_entry.to_dict()
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating diary entry: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating diary entry"
            )
    
    def search_diary_entries(self, user: User, search_params: DiaryEntrySearchParams, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Search diary entries for a user.
        
        Args:
            user: The user object.
            search_params: Search parameters.
            page: Page number.
            limit: Number of entries per page.
            
        Returns:
            Dictionary with search results and pagination info.
        """
        try:
            # Validate pagination parameters
            limit = min(limit, self.config.SEARCH_RESULT_LIMIT)
            
            entries = DiaryEntry.search(
                user_id=user.id,
                search_params=search_params,
                page=page,
                limit=limit
            )
            
            return {
                "entries": [entry.to_dict() for entry in entries],
                "search_info": {
                    "query": search_params.query,
                    "diary_id": search_params.diary_id,
                    "start_date": search_params.start_date,
                    "end_date": search_params.end_date
                },
                "pagination": {
                    "current_page": page,
                    "entries_per_page": limit
                }
            }
        except Exception as e:
            self.logger.error(f"Error searching diary entries: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error searching diary entries"
            ) 