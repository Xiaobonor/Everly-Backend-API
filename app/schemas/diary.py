"""Diary schemas for request and response validation."""

import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field, HttpUrl


class ContentType(str, Enum):
    """Content type enum for diary entries."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    DRAWING = "drawing"
    VIDEO = "video"
    LOCATION = "location"
    MIXED = "mixed"


class MediaContentCreate(BaseModel):
    """Schema for creating media content."""

    url: HttpUrl
    content_type: str
    thumbnail_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    location: Optional[Tuple[float, float]] = None


class MediaContentResponse(MediaContentCreate):
    """Schema for media content response."""

    created_at: datetime.datetime


class DiaryEntryBase(BaseModel):
    """Base diary entry schema."""

    title: str = Field(..., max_length=200)
    content: Optional[str] = None
    content_type: ContentType = ContentType.TEXT
    location: Optional[Tuple[float, float]] = None
    location_name: Optional[str] = None
    tags: List[str] = []


class DiaryEntryCreate(DiaryEntryBase):
    """Schema for creating a diary entry."""

    media_content: Optional[List[MediaContentCreate]] = None


class DiaryEntryUpdate(BaseModel):
    """Schema for updating a diary entry."""

    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    content_type: Optional[ContentType] = None
    media_content: Optional[List[MediaContentCreate]] = None
    location: Optional[Tuple[float, float]] = None
    location_name: Optional[str] = None
    tags: Optional[List[str]] = None


class DiaryEntryAnalysis(BaseModel):
    """Schema for diary entry analysis results."""

    sentiment_score: Optional[float] = None
    topics: List[str] = []
    entities: List[str] = []
    analyzed_at: datetime.datetime


class DiaryEntryResponse(DiaryEntryBase):
    """Schema for diary entry response."""

    id: str
    user: str
    media_content: List[MediaContentResponse] = []
    sentiment_score: Optional[float] = None
    topics: List[str] = []
    entities: List[str] = []
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class DiaryEntryList(BaseModel):
    """Schema for a list of diary entries."""

    items: List[DiaryEntryResponse]
    total: int
    page: int
    limit: int


class DiaryEntrySearchParams(BaseModel):
    """Schema for diary entry search parameters."""

    query: Optional[str] = None
    tags: Optional[List[str]] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    location: Optional[Tuple[float, float]] = None
    radius: Optional[float] = None  # in kilometers
    sentiment_min: Optional[float] = None
    sentiment_max: Optional[float] = None 