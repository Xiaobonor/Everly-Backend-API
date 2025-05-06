# Everly API - Frontend Developer Guide

## Introduction

This document provides a comprehensive guide for frontend developers who need to integrate with the Everly backend API. It covers authentication, available endpoints, request/response formats, and implementation guidelines.

## Authentication

Everly uses JWT (JSON Web Tokens) for API authentication after initial authentication through Google OAuth.

### Google OAuth Authentication Flow

1. **Frontend Initiates Login**:
   - Direct the user to Google's OAuth authorization page
   - Include your client ID, redirect URI, and requested scopes

2. **User Authenticates with Google**:
   - User grants permission to your application

3. **Google Redirects Back**:
   - Google redirects to your redirect URI with an authorization code

4. **Frontend Exchanges Code for Token**:
   - Frontend exchanges the authorization code for a Google access token
   - This step is handled on the client side using Google OAuth libraries

5. **Frontend Sends Token to Backend**:
   - Send the Google access token to `/api/v1/auth/google`
   - Backend verifies the token with Google and retrieves user info
   - Backend creates or updates the user record
   - Backend generates a JWT token and returns it to the frontend

6. **Frontend Stores JWT Token**:
   - Store the JWT token securely
   - Include it in the Authorization header for authenticated requests

### Authentication Endpoint

**POST /api/v1/auth/google**

Authenticates a user using a Google OAuth token.

Request:
```json
{
  "token": "google-oauth-access-token"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "message": "Authentication successful"
}
```

### Using JWT for Authenticated Requests

For all authenticated API endpoints, include the JWT token in the Authorization header:

```
Authorization: Bearer [jwt-token]
```

### Get Current User

**GET /api/v1/auth/me**

Returns information about the currently authenticated user.

Response:
```json
{
  "status": "success",
  "data": {
    "id": "user-id",
    "email": "user@example.com",
    "full_name": "User Name",
    "profile_picture": "https://example.com/profile.jpg",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "preferences": [
      {
        "key": "language",
        "value": "zh-TW"
      },
      {
        "key": "theme",
        "value": "dark"
      }
    ]
  },
  "message": "User information retrieved successfully"
}
```

### Update User Profile

**PUT /api/v1/users/me**

Updates the user's name and other general profile information.

Request:
```json
{
  "full_name": "New User Name"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": "user-id",
    "email": "user@example.com",
    "full_name": "New User Name",
    "profile_picture": "https://example.com/profile.jpg",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "preferences": [
      {
        "key": "language",
        "value": "zh-TW"
      },
      {
        "key": "theme",
        "value": "dark"
      }
    ]
  },
  "message": "User information updated successfully"
}
```

### Upload Profile Picture

**PUT /api/v1/users/me/profile-picture**

Updates the user's profile picture.

Request:
- Content-Type: multipart/form-data
- Form field: file (image file)

Response:
```json
{
  "status": "success",
  "data": {
    "id": "user-id",
    "email": "user@example.com",
    "full_name": "User Name",
    "profile_picture": "/static/uploads/profiles/uuid-filename.jpg",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "preferences": [
      {
        "key": "language",
        "value": "zh-TW"
      },
      {
        "key": "theme",
        "value": "dark"
      }
    ]
  },
  "message": "Profile picture updated successfully"
}
```

### Get User Preferences

**GET /api/v1/users/me/preferences**

Returns the user's preference settings.

Response:
```json
{
  "status": "success",
  "data": [
    {
      "key": "language",
      "value": "zh-TW"
    },
    {
      "key": "theme",
      "value": "dark"
    }
  ],
  "message": "User preferences retrieved successfully"
}
```

### Update User Preferences

**PUT /api/v1/users/me/preferences**

Updates the user's preference settings.

Request:
```json
{
  "language": "zh-TW",
  "theme": "dark"
}
```

Response:
```json
{
  "status": "success",
  "data": [
    {
      "key": "language",
      "value": "zh-TW"
    },
    {
      "key": "theme",
      "value": "dark"
    }
  ],
  "message": "User preferences updated successfully"
}
```

## Diaries

### List Diaries

**GET /api/v1/diaries**

Returns a list of all diaries for the authenticated user.

Response:
```json
{
  "status": "success",
  "data": [
    {
      "id": "diary-id-1",
      "title": "My Travel Journal",
      "description": "Documenting my travels",
      "cover_image": "https://example.com/cover1.jpg",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-02T00:00:00Z",
      "entry_count": 12
    },
    {
      "id": "diary-id-2",
      "title": "Daily Thoughts",
      "description": "My daily journal",
      "cover_image": null,
      "created_at": "2025-02-01T00:00:00Z",
      "updated_at": "2025-02-05T00:00:00Z",
      "entry_count": 5
    }
  ],
  "message": "Diaries retrieved successfully"
}
```

### Create Diary

**POST /api/v1/diaries**

Creates a new diary.

Request:
```json
{
  "title": "My Travel Journal",
  "description": "Documenting my travels",
  "cover_image": "https://example.com/cover1.jpg"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": "new-diary-id",
    "title": "My Travel Journal",
    "description": "Documenting my travels",
    "cover_image": "https://example.com/cover1.jpg",
    "created_at": "2025-05-01T00:00:00Z",
    "updated_at": "2025-05-01T00:00:00Z",
    "entry_count": 0
  },
  "message": "Diary created successfully"
}
```

### Get Diary

**GET /api/v1/diaries/{diary_id}**

Returns details for a specific diary.

Response:
```json
{
  "status": "success",
  "data": {
    "id": "diary-id",
    "title": "My Travel Journal",
    "description": "Documenting my travels",
    "cover_image": "https://example.com/cover1.jpg",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-02T00:00:00Z",
    "entry_count": 12
  },
  "message": "Diary retrieved successfully"
}
```

### Update Diary

**PUT /api/v1/diaries/{diary_id}**

Updates a diary.

Request:
```json
{
  "title": "Updated Travel Journal",
  "description": "New description",
  "cover_image": "https://example.com/newcover.jpg"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": "diary-id",
    "title": "Updated Travel Journal",
    "description": "New description",
    "cover_image": "https://example.com/newcover.jpg",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-05-05T00:00:00Z",
    "entry_count": 12
  },
  "message": "Diary updated successfully"
}
```

### Delete Diary

**DELETE /api/v1/diaries/{diary_id}**

Deletes a diary and all its entries.

Response:
```json
{
  "status": "success",
  "data": null,
  "message": "Diary deleted successfully"
}
```

## Diary Entries

### List Entries

**GET /api/v1/diaries/{diary_id}/entries**

Returns a list of entries for a specific diary.

Parameters:
- `page` (optional): Page number, default 1
- `limit` (optional): Number of entries per page, default 10
- `sort` (optional): Sort order, either "asc" or "desc", default "desc"

Response:
```json
{
  "status": "success",
  "data": {
    "entries": [
      {
        "id": "entry-id-1",
        "title": "Day 1 in Paris",
        "content": "Today I visited the Eiffel Tower...",
        "content_type": "text",
        "location": {
          "name": "Paris, France",
          "lat": 48.8566,
          "lng": 2.3522
        },
        "media": [],
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
      },
      {
        "id": "entry-id-2",
        "title": "Notre Dame Cathedral",
        "content": "The architecture is amazing!",
        "content_type": "mixed",
        "location": {
          "name": "Notre Dame, Paris",
          "lat": 48.8530,
          "lng": 2.3499
        },
        "media": [
          {
            "type": "image",
            "url": "https://example.com/image1.jpg"
          }
        ],
        "created_at": "2025-01-02T00:00:00Z",
        "updated_at": "2025-01-02T00:00:00Z"
      }
    ],
    "total": 12,
    "page": 1,
    "limit": 10,
    "pages": 2
  },
  "message": "Entries retrieved successfully"
}
```

### Create Entry

**POST /api/v1/diaries/{diary_id}/entries**

Creates a new entry in a diary.

Request:
```json
{
  "title": "Day 1 in Paris",
  "content": "Today I visited the Eiffel Tower...",
  "content_type": "text",
  "location": {
    "name": "Paris, France",
    "lat": 48.8566,
    "lng": 2.3522
  },
  "media": []
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": "new-entry-id",
    "title": "Day 1 in Paris",
    "content": "Today I visited the Eiffel Tower...",
    "content_type": "text",
    "location": {
      "name": "Paris, France",
      "lat": 48.8566,
      "lng": 2.3522
    },
    "media": [],
    "created_at": "2025-05-05T00:00:00Z",
    "updated_at": "2025-05-05T00:00:00Z"
  },
  "message": "Entry created successfully"
}
```

### Get Entry

**GET /api/v1/diaries/{diary_id}/entries/{entry_id}**

Returns details for a specific entry.

Response:
```json
{
  "status": "success",
  "data": {
    "id": "entry-id",
    "title": "Day 1 in Paris",
    "content": "Today I visited the Eiffel Tower...",
    "content_type": "text",
    "location": {
      "name": "Paris, France",
      "lat": 48.8566,
      "lng": 2.3522
    },
    "media": [],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  },
  "message": "Entry retrieved successfully"
}
```

### Update Entry

**PUT /api/v1/diaries/{diary_id}/entries/{entry_id}**

Updates a diary entry.

Request:
```json
{
  "title": "Updated: Day 1 in Paris",
  "content": "Today I visited the Eiffel Tower and the Louvre...",
  "content_type": "text",
  "location": {
    "name": "Paris, France",
    "lat": 48.8566,
    "lng": 2.3522
  },
  "media": []
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": "entry-id",
    "title": "Updated: Day 1 in Paris",
    "content": "Today I visited the Eiffel Tower and the Louvre...",
    "content_type": "text",
    "location": {
      "name": "Paris, France",
      "lat": 48.8566,
      "lng": 2.3522
    },
    "media": [],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-05-05T00:00:00Z"
  },
  "message": "Entry updated successfully"
}
```

### Delete Entry

**DELETE /api/v1/diaries/{diary_id}/entries/{entry_id}**

Deletes a diary entry.

Response:
```json
{
  "status": "success",
  "data": null,
  "message": "Entry deleted successfully"
}
```

## Media Upload

### Upload Media

**POST /api/v1/media/upload**

Uploads a media file and returns a URL that can be used in diary entries.

Request:
- Content-Type: multipart/form-data
- Form field: file

Response:
```json
{
  "status": "success",
  "data": {
    "url": "https://storage.everly.app/media/1234567890.jpg",
    "type": "image",
    "size": 1024000
  },
  "message": "File uploaded successfully"
}
```

## Content Types

Diary entries support various content types:

- `text`: Plain text entries
- `image`: Photo entries with URLs
- `audio`: Audio recordings with URLs
- `drawing`: Hand-drawn entries
- `video`: Video entries with URLs
- `location`: Location-only entries
- `mixed`: Entries with multiple content types

## Error Handling

The API uses standard HTTP status codes and returns error responses in a consistent format:

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Human-readable error message"
}
```

Common error codes:

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Development Environment

### Base URLs

- Development: `http://localhost:8000`
- Production: `https://api.everly.app`

### Required Headers for API Requests

- Content-Type: `application/json`
- Accept: `application/json`
- Authorization: `Bearer {jwt-token}` (for authenticated endpoints)

## Implementation Guidelines

### Recommended Libraries

- Authentication: Google Sign-In, Firebase Auth
- API Requests: Axios, Fetch API
- State Management: Redux, MobX, Zustand
- Form Handling: Formik, React Hook Form
- Internationalization: i18next, react-intl

### Example Integration (React + TypeScript)

```typescript
// Authentication Service Example
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// Store JWT token
const setToken = (token: string) => {
  localStorage.setItem('token', token);
};

// Get JWT token
const getToken = () => {
  return localStorage.getItem('token');
};

// Send Google OAuth token to backend
const authenticateWithGoogle = async (googleToken: string) => {
  try {
    const response = await axios.post(`${API_URL}/auth/google`, {
      token: googleToken
    });
    
    const { access_token } = response.data.data;
    setToken(access_token);
    return access_token;
  } catch (error) {
    console.error('Authentication failed', error);
    throw error;
  }
};

// Get authenticated user
const getCurrentUser = async () => {
  try {
    const response = await axios.get(`${API_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${getToken()}`
      }
    });
    
    return response.data.data;
  } catch (error) {
    console.error('Failed to get user', error);
    throw error;
  }
};

// Update user preferences
const updateUserPreferences = async (preferences: { language?: string; theme?: string }) => {
  try {
    const response = await axios.put(
      `${API_URL}/users/me/preferences`,
      preferences,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`
        }
      }
    );
    
    return response.data.data;
  } catch (error) {
    console.error('Failed to update preferences', error);
    throw error;
  }
};

// Upload profile picture
const uploadProfilePicture = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.put(
      `${API_URL}/users/me/profile-picture`,
      formData,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    return response.data.data;
  } catch (error) {
    console.error('Failed to upload profile picture', error);
    throw error;
  }
};
```

### User Settings Implementation Example

```typescript
import React, { useState, useEffect } from 'react';
import { getCurrentUser, updateUserPreferences, uploadProfilePicture } from './api';

const UserSettings = () => {
  const [user, setUser] = useState(null);
  const [language, setLanguage] = useState('en');
  const [theme, setTheme] = useState('light');
  const [name, setName] = useState('');
  const [file, setFile] = useState(null);
  
  useEffect(() => {
    const fetchUser = async () => {
      const userData = await getCurrentUser();
      setUser(userData);
      
      // Parse preferences
      const langPref = userData.preferences.find(p => p.key === 'language');
      if (langPref) setLanguage(langPref.value);
      
      const themePref = userData.preferences.find(p => p.key === 'theme');
      if (themePref) setTheme(themePref.value);
      
      setName(userData.full_name);
    };
    
    fetchUser();
  }, []);
  
  const handleUpdatePreferences = async () => {
    await updateUserPreferences({ language, theme });
    // Update UI or show success message
  };
  
  const handleUpdateName = async () => {
    await axios.put(
      `${API_URL}/users/me`,
      { full_name: name },
      {
        headers: {
          Authorization: `Bearer ${getToken()}`
        }
      }
    );
    // Update UI or show success message
  };
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };
  
  const handleUploadPicture = async () => {
    if (!file) return;
    await uploadProfilePicture(file);
    // Update UI or show success message
  };
  
  if (!user) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>User Settings</h1>
      
      <section>
        <h2>Profile</h2>
        <div>
          <label>Name:</label>
          <input value={name} onChange={e => setName(e.target.value)} />
          <button onClick={handleUpdateName}>Update Name</button>
        </div>
        
        <div>
          <label>Profile Picture:</label>
          <input type="file" accept="image/*" onChange={handleFileChange} />
          <button onClick={handleUploadPicture} disabled={!file}>Upload</button>
        </div>
      </section>
      
      <section>
        <h2>Preferences</h2>
        <div>
          <label>Language:</label>
          <select value={language} onChange={e => setLanguage(e.target.value)}>
            <option value="en">English</option>
            <option value="zh-TW">Traditional Chinese</option>
            <option value="es">Spanish</option>
          </select>
        </div>
        
        <div>
          <label>Theme:</label>
          <select value={theme} onChange={e => setTheme(e.target.value)}>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System</option>
          </select>
        </div>
        
        <button onClick={handleUpdatePreferences}>Save Preferences</button>
      </section>
    </div>
  );
};

export default UserSettings;
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Ensure Google OAuth is configured correctly
   - Check that the correct Google OAuth token is being sent
   - Verify JWT token format in Authorization header

2. **Request Errors**:
   - Validate request payload against API schemas
   - Check for missing required fields
   - Ensure correct Content-Type header

3. **Network Issues**:
   - Verify API base URL
   - Check network connectivity
   - Implement proper timeout handling

### Support

For additional support or to report issues:

- Email: dev@everly.app
- Developer Portal: https://developers.everly.app
- API Status: https://status.everly.app 