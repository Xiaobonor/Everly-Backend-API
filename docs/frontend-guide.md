# Everly API Documentation

## Overview

Everly is a personal diary and travel journal application that allows users to record, organize, and analyze their thoughts, experiences, and memories. This document provides technical guidance for frontend developers who will be integrating with the Everly backend API.

## Technical Architecture

Everly's backend is built with FastAPI, a modern, high-performance web framework for building APIs with Python. The application uses MongoDB for data storage and Redis for caching and session management. The backend follows a modular architecture with clear separation of concerns.

### Key Components:

- **FastAPI Framework**: Handles HTTP requests, routing, and response serialization
- **MongoDB**: Document database for storing user profiles and diary entries
- **Redis**: Caching and session management
- **JWT Authentication**: Secures API endpoints with token-based authentication
- **Google OAuth**: Provides social login capabilities

## API Endpoints

All API endpoints are prefixed with `/api/v1`. The API is versioned to ensure backward compatibility as the application evolves.

### Authentication

#### Google OAuth Authentication

```
POST /api/v1/auth/google
```

**Request Body:**
```json
{
  "code": "google-authorization-code"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "jwt-token",
    "token_type": "bearer"
  },
  "message": "Authentication successful"
}
```

**Implementation Notes:**
- Frontend should implement Google OAuth 2.0 flow
- After receiving the authorization code from Google, send it to this endpoint
- Store the returned JWT token securely (localStorage or httpOnly cookies)
- Include the token in the Authorization header for subsequent requests

#### Get Current User Profile

```
GET /api/v1/auth/me
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Response:**
```json
{
  "id": "user-id",
  "email": "user@example.com",
  "full_name": "User Name",
  "profile_picture": "https://example.com/profile.jpg",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "preferences": ["theme:dark", "language:en"]
}
```

### User Management

#### Get User Profile

```
GET /api/v1/users/me
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Response:** Same as `/api/v1/auth/me`

#### Update User Profile

```
PUT /api/v1/users/me
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Request Body:**
```json
{
  "full_name": "New Name",
  "profile_picture": "https://example.com/new-profile.jpg"
}
```

**Response:**
```json
{
  "id": "user-id",
  "email": "user@example.com",
  "full_name": "New Name",
  "profile_picture": "https://example.com/new-profile.jpg",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "preferences": ["theme:dark", "language:en"]
}
```

#### Get User Preferences

```
GET /api/v1/users/me/preferences
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Response:**
```json
["theme:dark", "language:en"]
```

#### Update User Preferences

```
PUT /api/v1/users/me/preferences
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Request Body:**
```json
["theme:light", "language:en", "notifications:enabled"]
```

**Response:**
```json
["theme:light", "language:en", "notifications:enabled"]
```

### Diary Entries

#### Create Diary Entry

```
POST /api/v1/diaries
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Request Body:**
```json
{
  "title": "My Day in Paris",
  "content": "Today I visited the Eiffel Tower and it was amazing...",
  "content_type": "text",
  "location": [48.8584, 2.2945],
  "location_name": "Paris, France",
  "tags": ["travel", "europe", "paris"],
  "media_content": [
    {
      "url": "https://example.com/image1.jpg",
      "content_type": "image",
      "thumbnail_url": "https://example.com/thumbnail1.jpg",
      "description": "View from the top"
    }
  ]
}
```

**Response:**
```json
{
  "id": "entry-id",
  "user": "user-id",
  "title": "My Day in Paris",
  "content": "Today I visited the Eiffel Tower and it was amazing...",
  "content_type": "text",
  "location": [48.8584, 2.2945],
  "location_name": "Paris, France",
  "tags": ["travel", "europe", "paris"],
  "media_content": [
    {
      "url": "https://example.com/image1.jpg",
      "content_type": "image",
      "thumbnail_url": "https://example.com/thumbnail1.jpg",
      "description": "View from the top",
      "created_at": "2023-01-01T12:00:00Z"
    }
  ],
  "sentiment_score": 0.87,
  "topics": ["travel", "sightseeing"],
  "entities": ["Eiffel Tower", "Paris"],
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### Get Diary Entries (Paginated)

```
GET /api/v1/diaries?page=1&limit=10
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Response:**
```json
{
  "items": [
    {
      "id": "entry-id-1",
      "user": "user-id",
      "title": "My Day in Paris",
      "content": "Today I visited the Eiffel Tower and it was amazing...",
      "content_type": "text",
      "location": [48.8584, 2.2945],
      "location_name": "Paris, France",
      "tags": ["travel", "europe", "paris"],
      "media_content": [
        {
          "url": "https://example.com/image1.jpg",
          "content_type": "image",
          "thumbnail_url": "https://example.com/thumbnail1.jpg",
          "description": "View from the top",
          "created_at": "2023-01-01T12:00:00Z"
        }
      ],
      "sentiment_score": 0.87,
      "topics": ["travel", "sightseeing"],
      "entities": ["Eiffel Tower", "Paris"],
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    },
    // Additional entries...
  ],
  "total": 42,
  "page": 1,
  "limit": 10
}
```

#### Get Single Diary Entry

```
GET /api/v1/diaries/{entry_id}
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Response:** Same structure as individual diary entry

#### Update Diary Entry

```
PUT /api/v1/diaries/{entry_id}
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "tags": ["travel", "europe", "paris", "vacation"]
}
```

**Response:** Updated diary entry

#### Delete Diary Entry

```
DELETE /api/v1/diaries/{entry_id}
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Response:** Status 204 No Content

#### Search Diary Entries

```
POST /api/v1/diaries/search
```

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Request Body:**
```json
{
  "query": "Paris",
  "tags": ["travel"],
  "start_date": "2023-01-01",
  "end_date": "2023-01-31",
  "sentiment_min": 0.5
}
```

**Response:**
```json
{
  "items": [
    // Diary entries matching search criteria
  ],
  "total": 3,
  "page": 1,
  "limit": 10
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

## Authentication Flow

### Google OAuth Flow

1. **Frontend Initiates Login**:
   - Direct the user to Google's OAuth authorization page
   - Include your client ID, redirect URI, and requested scopes

2. **User Authenticates with Google**:
   - User grants permission to your application

3. **Google Redirects Back**:
   - Google redirects to your redirect URI with an authorization code

4. **Exchange Code for Token**:
   - Send the authorization code to `/api/v1/auth/google`
   - Backend exchanges the code for a Google access token
   - Backend verifies the token with Google and retrieves user info
   - Backend creates or updates the user record
   - Backend generates a JWT token and returns it to the frontend

5. **Frontend Stores Token**:
   - Store the JWT token securely
   - Include it in the Authorization header for authenticated requests

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

- **HTTP Requests**: axios, fetch API
- **State Management**: Redux, MobX, or React Context
- **Form Handling**: Formik or React Hook Form
- **Validation**: Yup or Zod
- **Date Handling**: date-fns or Luxon

### Authentication Implementation

```javascript
// Example code for Google OAuth integration
const handleGoogleLogin = async (googleResponse) => {
  try {
    const response = await axios.post('https://api.everly.app/api/v1/auth/google', {
      code: googleResponse.code
    });
    
    const { access_token } = response.data.data;
    
    // Store token securely
    localStorage.setItem('token', access_token);
    
    // Configure axios defaults for future requests
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    // Fetch user profile
    const userResponse = await axios.get('https://api.everly.app/api/v1/users/me');
    return userResponse.data;
  } catch (error) {
    console.error('Authentication error:', error);
    throw error;
  }
};
```

### Creating a Diary Entry

```javascript
// Example code for creating a diary entry
const createDiaryEntry = async (entryData) => {
  try {
    const token = localStorage.getItem('token');
    
    const response = await axios.post('https://api.everly.app/api/v1/diaries', entryData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error creating diary entry:', error);
    throw error;
  }
};
```

## Webhooks and Real-time Updates

Currently, the API does not provide webhooks or real-time updates. For new content, frontend applications should poll the relevant endpoints or implement a manual refresh mechanism.

## Rate Limiting

The API implements rate limiting to protect the service from abuse. Limits are as follows:

- 60 requests per minute for authenticated users
- 10 requests per minute for unauthenticated requests

When rate limits are exceeded, the API returns a 429 Too Many Requests status code.

## Conclusion

This documentation provides an overview of the Everly API for frontend integration. For additional details, explore the API documentation available at `/api/docs` when running the backend service.

For support or questions, please contact the backend team or refer to the project's internal communication channels. 