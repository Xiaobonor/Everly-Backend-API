"""Diary schemas for request and response validation."""

import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any

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


class LocationModel(BaseModel):
    """Schema for location information."""

    name: str
    lat: float
    lng: float


class MediaModel(BaseModel):
    """Schema for media content."""

    type: str
    url: str


class DiaryBase(BaseModel):
    """Base diary schema."""

    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None


class DiaryCreate(DiaryBase):
    """Schema for creating a diary."""
    pass


class DiaryUpdate(BaseModel):
    """Schema for updating a diary."""

    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None


class DiaryResponse(DiaryBase):
    """Schema for diary response."""

    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    entry_count: int = 0

    class Config:
        """Pydantic config."""
        from_attributes = True


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
    location: Optional[LocationModel] = None
    media: List[MediaModel] = []


class DiaryEntryCreate(DiaryEntryBase):
    """Schema for creating a diary entry."""
    pass


class DiaryEntryUpdate(BaseModel):
    """Schema for updating a diary entry."""

    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    content_type: Optional[ContentType] = None
    location: Optional[LocationModel] = None
    media: Optional[List[MediaModel]] = None


class DiaryEntryResponse(DiaryEntryBase):
    """Schema for diary entry response."""

    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class DiaryEntriesResponse(BaseModel):
    """Schema for paginated entries response."""
    
    entries: List[DiaryEntryResponse]
    total: int
    page: int
    limit: int
    pages: int


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
    location: Optional[LocationModel] = None
    radius: Optional[float] = None  # in kilometers 