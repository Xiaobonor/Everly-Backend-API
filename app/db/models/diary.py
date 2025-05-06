"""Diary models for the application."""

import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

from mongoengine import (
    DateTimeField,
    Document,
    EnumField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
    URLField,
    GeoPointField,
)

from app.db.models.user import User


class ContentType(str, Enum):
    """Content type enum for diary entries."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    DRAWING = "drawing"
    VIDEO = "video"
    LOCATION = "location"
    MIXED = "mixed"


class MediaContent(EmbeddedDocument):
    """Media content embedded document for diary entries."""

    type = StringField(required=True)
    url = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)


class Location(EmbeddedDocument):
    """Location embedded document for diary entries."""

    name = StringField(required=True)
    lat = FloatField(required=True)
    lng = FloatField(required=True)


class Diary(Document):
    """Diary model for the application."""

    user = ReferenceField(User, required=True)
    title = StringField(required=True, max_length=200)
    description = StringField()
    cover_image = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        "collection": "diaries",
        "indexes": [
            "user",
            ("user", "-created_at"),
        ]
    }
    
    def clean(self):
        """Update the updated_at field on save."""
        self.updated_at = datetime.datetime.utcnow()
    
    @classmethod
    def get_by_user(cls, user_id: str) -> List["Diary"]:
        """
        Get diaries for a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            A list of diaries.
        """
        return cls.objects(user=user_id).order_by("-created_at")
    
    @classmethod
    def get_by_id(cls, diary_id: str, user_id: Optional[str] = None) -> Optional["Diary"]:
        """
        Get a diary by ID.
        
        Args:
            diary_id: The ID of the diary.
            user_id: Optional user ID to restrict access.
            
        Returns:
            The diary document or None if not found.
        """
        query = {"id": diary_id}
        if user_id:
            query["user"] = user_id
            
        return cls.objects(**query).first()
        
    def to_dict(self) -> Dict:
        """
        Convert the diary to a dictionary.
        
        Returns:
            A dictionary representation of the diary.
        """
        entry_count = DiaryEntry.objects(diary=self.id).count()
        
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "cover_image": self.cover_image,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "entry_count": entry_count
        }


class DiaryEntry(Document):
    """Diary entry model for the application."""

    user = ReferenceField(User, required=True)
    diary = ReferenceField(Diary, required=True)
    title = StringField(required=True, max_length=200)
    content = StringField()
    content_type = EnumField(ContentType, default=ContentType.TEXT)
    location = EmbeddedDocumentField(Location)
    media = ListField(EmbeddedDocumentField(MediaContent))
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        "collection": "diary_entries",
        "indexes": [
            "user",
            "diary",
            ("diary", "-created_at"),
            ("user", "-created_at"),
        ]
    }
    
    def clean(self):
        """Update the updated_at field on save."""
        self.updated_at = datetime.datetime.utcnow()
    
    @classmethod
    def get_by_diary(cls, diary_id: str, limit: int = 10, skip: int = 0, sort: str = "desc") -> List["DiaryEntry"]:
        """
        Get diary entries for a diary.
        
        Args:
            diary_id: The ID of the diary.
            limit: The maximum number of entries to return.
            skip: The number of entries to skip.
            sort: Sort order ("asc" or "desc").
            
        Returns:
            A list of diary entries.
        """
        sort_field = "created_at" if sort == "asc" else "-created_at"
        return cls.objects(diary=diary_id).order_by(sort_field).skip(skip).limit(limit)
    
    @classmethod
    def get_by_id(cls, entry_id: str, diary_id: Optional[str] = None, user_id: Optional[str] = None) -> Optional["DiaryEntry"]:
        """
        Get a diary entry by ID.
        
        Args:
            entry_id: The ID of the diary entry.
            diary_id: Optional diary ID to restrict access.
            user_id: Optional user ID to restrict access.
            
        Returns:
            The diary entry document or None if not found.
        """
        query = {"id": entry_id}
        if diary_id:
            query["diary"] = diary_id
        if user_id:
            query["user"] = user_id
            
        return cls.objects(**query).first()
    
    def to_dict(self) -> Dict:
        """
        Convert the diary entry to a dictionary.
        
        Returns:
            A dictionary representation of the diary entry.
        """
        location_dict = None
        if self.location:
            location_dict = {
                "name": self.location.name,
                "lat": self.location.lat,
                "lng": self.location.lng
            }
            
        media_list = []
        if self.media:
            for m in self.media:
                media_list.append({
                    "type": m.type,
                    "url": m.url
                })
                
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "content_type": self.content_type,
            "location": location_dict,
            "media": media_list,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 