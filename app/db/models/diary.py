"""Diary entry model for the application."""

import datetime
from enum import Enum
from typing import Dict, List, Optional

from mongoengine import (
    DateTimeField,
    Document,
    EnumField,
    FloatField,
    ListField,
    ReferenceField,
    StringField,
    EmbeddedDocument,
    EmbeddedDocumentField,
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

    url = URLField(required=True)
    content_type = StringField(required=True)
    thumbnail_url = URLField()
    description = StringField()
    location = GeoPointField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)


class DiaryEntry(Document):
    """Diary entry model for the application."""

    user = ReferenceField(User, required=True)
    title = StringField(required=True, max_length=200)
    content = StringField()
    content_type = EnumField(ContentType, default=ContentType.TEXT)
    media_content = ListField(EmbeddedDocumentField(MediaContent))
    location = GeoPointField()
    location_name = StringField()
    tags = ListField(StringField())
    sentiment_score = FloatField()
    topics = ListField(StringField())
    entities = ListField(StringField())
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        "collection": "diary_entries",
        "indexes": [
            "user",
            ("user", "-created_at"),
            "tags",
            "location",
            ("user", "tags"),
            ("user", "sentiment_score")
        ]
    }
    
    def clean(self):
        """Update the updated_at field on save."""
        self.updated_at = datetime.datetime.utcnow()
    
    @classmethod
    def get_by_user(cls, user_id: str, limit: int = 10, skip: int = 0) -> List["DiaryEntry"]:
        """
        Get diary entries for a user.
        
        Args:
            user_id: The ID of the user.
            limit: The maximum number of entries to return.
            skip: The number of entries to skip.
            
        Returns:
            A list of diary entries.
        """
        return cls.objects(user=user_id).order_by("-created_at").skip(skip).limit(limit)
    
    @classmethod
    def get_by_id(cls, entry_id: str, user_id: Optional[str] = None) -> Optional["DiaryEntry"]:
        """
        Get a diary entry by ID.
        
        Args:
            entry_id: The ID of the diary entry.
            user_id: Optional user ID to restrict access.
            
        Returns:
            The diary entry document or None if not found.
        """
        query = {"id": entry_id}
        if user_id:
            query["user"] = user_id
            
        return cls.objects(**query).first()
    
    def to_dict(self) -> Dict:
        """
        Convert the diary entry to a dictionary.
        
        Returns:
            A dictionary representation of the diary entry.
        """
        return {
            "id": str(self.id),
            "user": str(self.user.id) if self.user else None,
            "title": self.title,
            "content": self.content,
            "content_type": self.content_type,
            "media_content": [
                {
                    "url": m.url,
                    "content_type": m.content_type,
                    "thumbnail_url": m.thumbnail_url,
                    "description": m.description,
                    "location": m.location,
                    "created_at": m.created_at.isoformat() if m.created_at else None
                }
                for m in self.media_content
            ] if self.media_content else [],
            "location": self.location,
            "location_name": self.location_name,
            "tags": self.tags,
            "sentiment_score": self.sentiment_score,
            "topics": self.topics,
            "entities": self.entities,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 