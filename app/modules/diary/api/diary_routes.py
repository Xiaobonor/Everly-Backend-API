"""Diary API routes."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path

from app.modules.diary.services import DiaryService
from app.modules.diary.config import DiaryConfig
from app.schemas.diary import (
    DiaryCreate,
    DiaryUpdate,
    DiaryEntryCreate,
    DiaryEntryUpdate,
    DiaryEntrySearchParams,
)
from app.schemas.user import ApiResponse
from app.db.models.user import User

# Import auth dependency from auth module
from app.modules.auth.api.auth_routes import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize diary service with config
diary_config = DiaryConfig.from_env()
diary_service = DiaryService(diary_config)


# 日記相關端點
@router.get("", response_model=ApiResponse)
async def get_diaries(current_user: User = Depends(get_current_user)) -> Any:
    """
    獲取用戶的所有日記列表。
    
    Args:
        current_user: 當前認證用戶。
        
    Returns:
        日記列表。
    """
    logger.info(f"API 請求 GET /diaries - 用戶ID: {current_user.id}")
    logger.debug(f"獲取用戶所有日記 - 請求開始處理")
    
    try:
        diaries_data = diary_service.get_user_diaries(current_user)
        logger.debug(f"找到 {len(diaries_data)} 個日記")
        
        logger.info(f"API 請求 GET /diaries 完成 - 用戶ID: {current_user.id}, 共返回 {len(diaries_data)} 個日記")
        return {
            "status": "success",
            "data": diaries_data,
            "message": "Diaries retrieved successfully"
        }
    except Exception as e:
        logger.error(f"獲取日記時發生錯誤 - 用戶ID: {current_user.id}, 錯誤: {str(e)}", exc_info=True)
        raise


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_diary(diary: DiaryCreate, current_user: User = Depends(get_current_user)) -> Any:
    """
    創建新日記。
    
    Args:
        diary: 日記數據。
        current_user: 當前認證用戶。
        
    Returns:
        創建的日記。
    """
    logger.info(f"API 請求 POST /diaries - 用戶ID: {current_user.id}")
    logger.debug(f"創建新日記 - 標題: '{diary.title}'")
    
    try:
        new_diary_data = diary_service.create_diary(
            user=current_user,
            title=diary.title,
            description=diary.description,
            cover_image=diary.cover_image
        )
        
        logger.info(f"API 請求 POST /diaries 完成 - 用戶ID: {current_user.id}")
        return {
            "status": "success",
            "data": new_diary_data,
            "message": "Diary created successfully"
        }
    except Exception as e:
        logger.error(f"創建日記時發生錯誤 - 用戶ID: {current_user.id}, 錯誤: {str(e)}", exc_info=True)
        raise


@router.get("/{diary_id}", response_model=ApiResponse)
async def get_diary(
    diary_id: str = Path(..., title="The ID of the diary to get"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    獲取特定日記的詳細信息。
    
    Args:
        diary_id: 日記ID。
        current_user: 當前認證用戶。
        
    Returns:
        日記詳細信息。
    """
    logger.info(f"API 請求 GET /diaries/{diary_id} - 用戶ID: {current_user.id}")
    logger.debug(f"獲取日記詳細信息 - 日記ID: {diary_id}")
    
    try:
        diary_data = diary_service.get_diary_by_id(diary_id, current_user)
        
        if not diary_data:
            logger.warning(f"日記未找到 - 日記ID: {diary_id}, 用戶ID: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary not found"
            )
        
        logger.info(f"API 請求 GET /diaries/{diary_id} 完成 - 用戶ID: {current_user.id}")
        return {
            "status": "success",
            "data": diary_data,
            "message": "Diary retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取日記詳情時發生錯誤 - 日記ID: {diary_id}, 用戶ID: {current_user.id}, 錯誤: {str(e)}", exc_info=True)
        raise


@router.put("/{diary_id}", response_model=ApiResponse)
async def update_diary(
    diary_update: DiaryUpdate,
    diary_id: str = Path(..., title="The ID of the diary to update"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    更新特定日記的信息。
    
    Args:
        diary_id: 日記ID。
        diary_update: 更新的日記數據。
        current_user: 當前認證用戶。
        
    Returns:
        更新後的日記信息。
    """
    logger.info(f"API 請求 PUT /diaries/{diary_id} - 用戶ID: {current_user.id}")
    update_data = diary_update.dict(exclude_unset=True, exclude_none=True)
    logger.debug(f"更新日記 - 日記ID: {diary_id}, 更新字段: {', '.join(update_data.keys())}")
    
    try:
        updated_diary = diary_service.update_diary(diary_id, current_user, update_data)
        
        if not updated_diary:
            logger.warning(f"日記未找到 - 日記ID: {diary_id}, 用戶ID: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary not found"
            )
        
        logger.info(f"API 請求 PUT /diaries/{diary_id} 完成 - 用戶ID: {current_user.id}")
        return {
            "status": "success",
            "data": updated_diary,
            "message": "Diary updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新日記時發生錯誤 - 日記ID: {diary_id}, 用戶ID: {current_user.id}, 錯誤: {str(e)}", exc_info=True)
        raise


@router.delete("/{diary_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def delete_diary(
    diary_id: str = Path(..., title="The ID of the diary to delete"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    刪除特定日記。
    
    Args:
        diary_id: 日記ID。
        current_user: 當前認證用戶。
        
    Returns:
        刪除確認信息。
    """
    logger.info(f"API 請求 DELETE /diaries/{diary_id} - 用戶ID: {current_user.id}")
    logger.debug(f"刪除日記 - 日記ID: {diary_id}")
    
    try:
        deleted = diary_service.delete_diary(diary_id, current_user)
        
        if not deleted:
            logger.warning(f"日記未找到 - 日記ID: {diary_id}, 用戶ID: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diary not found"
            )
        
        logger.info(f"API 請求 DELETE /diaries/{diary_id} 完成 - 用戶ID: {current_user.id}")
        return {
            "status": "success",
            "data": {"diary_id": diary_id},
            "message": "Diary deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除日記時發生錯誤 - 日記ID: {diary_id}, 用戶ID: {current_user.id}, 錯誤: {str(e)}", exc_info=True)
        raise


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
    獲取特定日記的條目列表。
    
    Args:
        diary_id: 日記ID。
        page: 頁碼。
        limit: 每頁條目數。
        sort: 排序方式 (asc 或 desc)。
        current_user: 當前認證用戶。
        
    Returns:
        日記條目列表。
    """
    logger.info(f"API 請求 GET /diaries/{diary_id}/entries - 用戶ID: {current_user.id}")
    logger.debug(f"獲取日記條目 - 日記ID: {diary_id}, 頁碼: {page}, 每頁: {limit}, 排序: {sort}")
    
    try:
        result = diary_service.get_diary_entries(diary_id, current_user, page, limit, sort)
        
        logger.info(f"API 請求 GET /diaries/{diary_id}/entries 完成 - 用戶ID: {current_user.id}")
        return {
            "status": "success",
            "data": result,
            "message": "Diary entries retrieved successfully"
        }
    except Exception as e:
        logger.error(f"獲取日記條目時發生錯誤 - 日記ID: {diary_id}, 用戶ID: {current_user.id}, 錯誤: {str(e)}", exc_info=True)
        raise


@router.post("/{diary_id}/entries", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_diary_entry(
    entry: DiaryEntryCreate,
    diary_id: str = Path(..., title="The ID of the diary"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    為特定日記創建新條目。
    
    Args:
        entry: 日記條目數據。
        diary_id: 日記ID。
        current_user: 當前認證用戶。
        
    Returns:
        創建的日記條目。
    """
    logger.info(f"API 請求 POST /diaries/{diary_id}/entries - 用戶ID: {current_user.id}")
    logger.debug(f"創建日記條目 - 日記ID: {diary_id}, 標題: '{entry.title}'")
    
    try:
        new_entry_data = diary_service.create_diary_entry(
            diary_id=diary_id,
            user=current_user,
            title=entry.title,
            content=entry.content,
            media_urls=entry.media_urls
        )
        
        logger.info(f"API 請求 POST /diaries/{diary_id}/entries 完成 - 用戶ID: {current_user.id}")
        return {
            "status": "success",
            "data": new_entry_data,
            "message": "Diary entry created successfully"
        }
    except Exception as e:
        logger.error(f"創建日記條目時發生錯誤 - 日記ID: {diary_id}, 用戶ID: {current_user.id}, 錯誤: {str(e)}", exc_info=True)
        raise


@router.post("/search", response_model=ApiResponse)
async def search_diary_entries(
    search_params: DiaryEntrySearchParams,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    搜索用戶的日記條目。
    
    Args:
        search_params: 搜索參數。
        page: 頁碼。
        limit: 每頁條目數。
        current_user: 當前認證用戶。
        
    Returns:
        搜索結果。
    """
    logger.info(f"API 請求 POST /diaries/search - 用戶ID: {current_user.id}")
    logger.debug(f"搜索日記條目 - 查詢: '{search_params.query}', 頁碼: {page}, 每頁: {limit}")
    
    try:
        result = diary_service.search_diary_entries(current_user, search_params, page, limit)
        
        logger.info(f"API 請求 POST /diaries/search 完成 - 用戶ID: {current_user.id}")
        return {
            "status": "success",
            "data": result,
            "message": "Search completed successfully"
        }
    except Exception as e:
        logger.error(f"搜索日記條目時發生錯誤 - 用戶ID: {current_user.id}, 錯誤: {str(e)}", exc_info=True)
        raise 