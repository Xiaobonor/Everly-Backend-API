"""User schemas for request and response validation."""

import datetime
import base64
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, EmailStr, HttpUrl, Field


class PreferenceModel(BaseModel):
    """Schema for a user preference."""
    
    key: str
    value: Any


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str
    profile_picture: Optional[HttpUrl] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a user."""

    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    full_name: Optional[str] = None
    profile_picture: Optional[HttpUrl] = None


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preferences."""
    
    language: Optional[str] = Field(None, description="User interface language preference (e.g., 'en', 'zh-TW')")
    theme: Optional[str] = Field(None, description="User interface theme preference (e.g., 'light', 'dark')")
    custom_settings: Optional[Dict[str, Any]] = Field(None, description="Custom user settings")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for storage."""
        result = {}
        if self.language:
            result["language"] = self.language
        if self.theme:
            result["theme"] = self.theme
        if self.custom_settings:
            for key, value in self.custom_settings.items():
                # 確保字典中的鍵是字符串
                str_key = str(key)
                
                # 如果值是二進制數據，轉換為Base64字符串
                if isinstance(value, bytes):
                    value = base64.b64encode(value).decode('ascii')
                
                result[str_key] = value
        return result


class UserResponse(UserBase):
    """Schema for user response."""

    id: str
    created_at: datetime.datetime
    preferences: List[PreferenceModel] = []

    class Config:
        """Pydantic config."""
        from_attributes = True


class ApiResponse(BaseModel):
    """Schema for standard API response."""
    
    status: str = "success"
    data: Any
    message: str = "" 