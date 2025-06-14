"""Diary endpoints."""

import logging
from typing import Any, Dict, List, Optional
import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path

from app.schemas.diary import (
    DiaryCreate,
    DiaryUpdate,
    DiaryResponse,
    DiaryEntryCreate,
    DiaryEntryUpdate,
    DiaryEntryResponse,
    DiaryEntriesResponse,
    DiaryEntrySearchParams,
)
from app.schemas.user import ApiResponse
from app.services.auth import get_current_user
from app.db.models.diary import Diary, DiaryEntry
from app.db.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


# Diary-related endpoints
@router.get("", response_model=ApiResponse)
async def get_diaries(current_user: User = Depends(get_current_user)) -> Any:
    """
    Retrieve all diaries for the user.

    Args:
        current_user: The current authenticated user.

    Returns:
        List of diaries.
    """
    logger.info(f"API request GET /diaries - User ID: {current_user.id}")
    logger.debug(f"Retrieving all diaries for user - Request started")
    
    try:
        logger.debug(f"Querying database for all diaries of user {current_user.id}")
        diaries = Diary.get_by_user(user_id=current_user.id)
        logger.debug(f"Found {len(diaries)} diaries")
        
        diaries_data = [diary.to_dict() for diary in diaries]
        logger.debug(f"Diary data conversion completed")
        
        logger.info(f"API request GET /diaries completed - User ID: {current_user.id}, returned {len(diaries)} diaries")
        return {
            "status": "success",
            "data": diaries_data,
            "message": "Diaries retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error occurred while retrieving diaries - User ID: {current_user.id}, Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving diaries"
        )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_diary(diary: DiaryCreate, current_user: User = Depends(get_current_user)) -> Any:
    """
    Create a new diary.

    Args:
        diary: Diary data.
        current_user: The current authenticated user.

    Returns:
        Created diary.
    """
    logger.info(f"API request POST /diaries - User ID: {current_user.id}")
    logger.debug(f"Creating new diary - Title: '{diary.title}'")
    
    try:
        logger.debug(f"Preparing to create new diary object - User ID: {current_user.id}, Title: '{diary.title}'")
        new_diary = Diary(
            user=current_user,
            title=diary.title,
            description=diary.description,
            cover_image=diary.cover_image
        )
        new_diary.save()
        logger.debug(f"New diary saved to database - Diary ID: {new_diary.id}")
        
        logger.info(f"API request POST /diaries completed - User ID: {current_user.id}, Diary ID: {new_diary.id}")
        return {
            "status": "success",
            "data": new_diary.to_dict(),
            "message": "Diary created successfully"
        }
    except Exception as e:
        logger.error(f"Error occurred while creating diary - User ID: {current_user.id}, Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the diary"
        )


@router.get("/{diary_id}", response_model=ApiResponse)
async def get_diary(
    diary_id: str = Path(..., title="The ID of the diary to get"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve details of a specific diary.

    Args:
        diary_id: The diary ID.
        current_user: The current authenticated user.

    Returns:
        Diary details.
    """
    logger.info(f"API request GET /diaries/{diary_id} - User ID: {current_user.id}")
    logger.debug(f"Retrieving diary details - Diary ID: {diary_id}")
    
    try:
        logger.debug(f"Querying database for diary - Diary ID: {diary_id}, User ID: {current_user.id}")
        diary = Diary.get_by_id(diary_id=diary_id, user_id=current_user.id)
        
        if not diary:
            logger.warning(f"Diary not found - Diary ID: {diary_id}, User ID: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary not found"
            )
        
        logger.debug(f"Diary found - Title: '{diary.title}'")
        logger.info(f"API request GET /diaries/{diary_id} completed - User ID: {current_user.id}")
        
        return {
            "status": "success",
            "data": diary.to_dict(),
            "message": "Diary retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error occurred while retrieving diary details - Diary ID: {diary_id}, User ID: {current_user.id}, Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the diary"
        )


@router.put("/{diary_id}", response_model=ApiResponse)
async def update_diary(
    diary_update: DiaryUpdate,
    diary_id: str = Path(..., title="The ID of the diary to update"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update information of a specific diary.

    Args:
        diary_id: The diary ID.
        diary_update: Updated diary data.
        current_user: The current authenticated user.

    Returns:
        Updated diary information.
    """
    logger.info(f"API request PUT /diaries/{diary_id} - User ID: {current_user.id}")
    update_data = diary_update.dict(exclude_unset=True, exclude_none=True)
    logger.debug(f"Updating diary - Diary ID: {diary_id}, Fields updated: {', '.join(update_data.keys())}")
    
    try:
        logger.debug(f"Querying database for diary - Diary ID: {diary_id}, User ID: {current_user.id}")
        diary = Diary.get_by_id(diary_id=diary_id, user_id=current_user.id)
        
        if not diary:
            logger.warning(f"Diary not found - Diary ID: {diary_id}, User ID: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary not found"
            )
        
        logger.debug(f"Diary found, starting field updates - Diary ID: {diary_id}")
        for field, value in update_data.items():
        logger.debug(f"Updating field: {field} = {value}")
            setattr(diary, field, value)
        
        diary.save()
        logger.debug(f"Diary update saved to database - Diary ID: {diary_id}")
        
        logger.info(f"API request PUT /diaries/{diary_id} completed - User ID: {current_user.id}")
        return {
            "status": "success",
            "data": diary.to_dict(),
            "message": "Diary updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error occurred while updating diary - Diary ID: {diary_id}, User ID: {current_user.id}, Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the diary"
        )


@router.delete("/{diary_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def delete_diary(
    diary_id: str = Path(..., title="The ID of the diary to delete"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a specific diary and all its entries.

    Args:
        diary_id: The diary ID.
        current_user: The current authenticated user.

    Returns:
        Success message.
    """
    logger.info(f"API request DELETE /diaries/{diary_id} - User ID: {current_user.id}")
    logger.debug(f"Deleting diary - Diary ID: {diary_id}")
    
    try:
        logger.debug(f"Querying database for diary - Diary ID: {diary_id}, User ID: {current_user.id}")
        diary = Diary.get_by_id(diary_id=diary_id, user_id=current_user.id)
        
        if not diary:
            logger.warning(f"Diary not found - Diary ID: {diary_id}, User ID: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary not found"
            )
        
        # Delete all entries of the diary
        logger.debug(f"Deleting all entries of diary - Diary ID: {diary_id}")
        entries_count = DiaryEntry.objects(diary=diary.id).count()
        DiaryEntry.objects(diary=diary.id).delete()
        logger.debug(f"Deleted {entries_count} diary entries")
        
        # Delete the diary itself
        logger.debug(f"Deleting diary record - Diary ID: {diary_id}, Title: '{diary.title}'")
        diary.delete()
        
        logger.info(f"API request DELETE /diaries/{diary_id} completed - User ID: {current_user.id}, Deleted diary and {entries_count} entries")
        return {
            "status": "success",
            "data": None,
            "message": "Diary deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error occurred while deleting diary - Diary ID: {diary_id}, User ID: {current_user.id}, Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the diary"
        )


# 日記條目相關端點
@router.get("/{diary_id}/entries", response_model=ApiResponse)
async def get_diary_entries(
    diary_id: str = Path(..., title="The ID of the diary"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    獲取特定日記的所有條目（分頁）。
    
    Args:
        diary_id: 日記ID。
        page: 頁碼，從1開始。
        limit: 每頁條目數。
        sort: 排序方式，"asc"為升序，"desc"為降序。
        current_user: 當前認證用戶。
        
    Returns:
        日記條目列表。
    """
    logger.info(f"API 請求 GET /diaries/{diary_id}/entries - 用戶ID: {current_user.id}")
    logger.debug(f"獲取日記條目 - 日記ID: {diary_id}, 頁碼: {page}, 每頁: {limit}, 排序: {sort}")
    
    try:
        # 確認日記存在且屬於當前用戶
        logger.debug(f"驗證日記存在性 - 日記ID: {diary_id}, 用戶ID: {current_user.id}")
        diary = Diary.get_by_id(diary_id=diary_id, user_id=current_user.id)
        
        if not diary:
            logger.warning(f"日記未找到 - 日記ID: {diary_id}, 用戶ID: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary not found"
            )
        
        logger.debug(f"查詢日記條目 - 日記ID: {diary_id}, 排序: {sort}")
        entries, total = DiaryEntry.get_by_diary(
            diary_id=diary_id,
            page=page,
            limit=limit,
            sort=sort
        )
        
        logger.debug(f"找到 {len(entries)} 個條目，共 {total} 個")
        
        # 計算頁數
        total_pages = (total + limit - 1) // limit
        
        # 轉換為響應格式
        entries_data = [entry.to_dict() for entry in entries]
        
        pagination = {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
        
        logger.info(f"API 請求 GET /diaries/{diary_id}/entries 完成 - 用戶ID: {current_user.id}, 返回 {len(entries)} 個條目")
        
        return {
            "status": "success",
            "data": {
                "entries": entries_data,
                "pagination": pagination
            },
            "message": "Diary entries retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取日記條目時發生錯誤 - 日記ID: {diary_id}, 用戶ID: {current_user.id}, 錯誤: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving diary entries"
        )


@router.post("/{diary_id}/entries", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_diary_entry(
    entry: DiaryEntryCreate,
    diary_id: str = Path(..., title="The ID of the diary"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    在指定日記中創建新條目。
    
    Args:
        diary_id: 日記ID。
        entry: 日記條目數據。
        current_user: 當前認證用戶。
        
    Returns:
        創建的日記條目。
    """
    try:
        # 先確認日記存在且屬於當前用戶
        diary = Diary.get_by_id(diary_id=diary_id, user_id=current_user.id)
        if not diary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary not found"
            )
        
        # 創建日記條目
        new_entry = DiaryEntry(
            user=current_user,
            diary=diary,
            title=entry.title,
            content=entry.content,
            content_type=entry.content_type
        )
        
        # 處理位置信息
        if entry.location:
            from app.db.models.diary import Location
            location = Location(
                name=entry.location.name,
                lat=entry.location.lat,
                lng=entry.location.lng
            )
            new_entry.location = location
        
        # 處理媒體內容
        if entry.media:
            from app.db.models.diary import MediaContent
            for media in entry.media:
                media_content = MediaContent(
                    type=media.type,
                    url=media.url
                )
                new_entry.media.append(media_content)
        
        new_entry.save()
        
        # 更新日記的更新時間
        diary.updated_at = datetime.datetime.utcnow()
        diary.save()
        
        return {
            "status": "success",
            "data": new_entry.to_dict(),
            "message": "Entry created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating diary entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the diary entry"
        )


@router.get("/{diary_id}/entries/{entry_id}", response_model=ApiResponse)
async def get_diary_entry(
    diary_id: str = Path(..., title="The ID of the diary"),
    entry_id: str = Path(..., title="The ID of the entry"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    獲取特定日記條目的詳細信息。
    
    Args:
        diary_id: 日記ID。
        entry_id: 條目ID。
        current_user: 當前認證用戶。
        
    Returns:
        日記條目詳細信息。
    """
    # 先確認日記存在且屬於當前用戶
    diary = Diary.get_by_id(diary_id=diary_id, user_id=current_user.id)
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary not found"
        )
    
    entry = DiaryEntry.get_by_id(entry_id=entry_id, diary_id=diary.id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary entry not found"
        )
    
    return {
        "status": "success",
        "data": entry.to_dict(),
        "message": "Entry retrieved successfully"
    }


@router.put("/{diary_id}/entries/{entry_id}", response_model=ApiResponse)
async def update_diary_entry(
    entry_update: DiaryEntryUpdate,
    diary_id: str = Path(..., title="The ID of the diary"),
    entry_id: str = Path(..., title="The ID of the entry"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    更新特定日記條目的信息。
    
    Args:
        diary_id: 日記ID。
        entry_id: 條目ID。
        entry_update: 更新的條目數據。
        current_user: 當前認證用戶。
        
    Returns:
        更新後的條目信息。
    """
    try:
        # 先確認日記存在且屬於當前用戶
        diary = Diary.get_by_id(diary_id=diary_id, user_id=current_user.id)
        if not diary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary not found"
            )
        
        entry = DiaryEntry.get_by_id(entry_id=entry_id, diary_id=diary.id)
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary entry not found"
            )
        
        update_data = entry_update.dict(exclude_unset=True, exclude_none=True)
        
        # 分別處理嵌套字段
        location = update_data.pop("location", None)
        media = update_data.pop("media", None)
        
        # 更新簡單字段
        for field, value in update_data.items():
            setattr(entry, field, value)
        
        # 更新位置信息
        if location is not None:
            from app.db.models.diary import Location
            entry.location = Location(
                name=location.name,
                lat=location.lat,
                lng=location.lng
            ) if location else None
        
        # 更新媒體內容
        if media is not None:
            from app.db.models.diary import MediaContent
            entry.media = []
            for m in media:
                media_content = MediaContent(
                    type=m.type,
                    url=m.url
                )
                entry.media.append(media_content)
        
        entry.save()
        
        # 更新日記的更新時間
        diary.updated_at = datetime.datetime.utcnow()
        diary.save()
        
        return {
            "status": "success",
            "data": entry.to_dict(),
            "message": "Entry updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating diary entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the diary entry"
        )


@router.delete("/{diary_id}/entries/{entry_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def delete_diary_entry(
    diary_id: str = Path(..., title="The ID of the diary"),
    entry_id: str = Path(..., title="The ID of the entry"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    刪除特定日記條目。
    
    Args:
        diary_id: 日記ID。
        entry_id: 條目ID。
        current_user: 當前認證用戶。
        
    Returns:
        成功信息。
    """
    # 先確認日記存在且屬於當前用戶
    diary = Diary.get_by_id(diary_id=diary_id, user_id=current_user.id)
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary not found"
        )
    
    entry = DiaryEntry.get_by_id(entry_id=entry_id, diary_id=diary.id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary entry not found"
        )
    
    try:
        entry.delete()
        
        # 更新日記的更新時間
        diary.updated_at = datetime.datetime.utcnow()
        diary.save()
        
        return {
            "status": "success",
            "data": None,
            "message": "Entry deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting diary entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the diary entry"
        )


@router.post("/search", response_model=ApiResponse)
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
        
        # 計算總頁數
        pages = (total + limit - 1) // limit  # 向上取整
        
        # 轉換為字典列表
        entry_dicts = [entry.to_dict() for entry in entries]
        
        entries_data = {
            "entries": entry_dicts,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
        
        return {
            "status": "success",
            "data": entries_data,
            "message": "Entries search completed successfully"
        }
    except Exception as e:
        logger.error(f"Error searching diary entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching diary entries"
        ) 