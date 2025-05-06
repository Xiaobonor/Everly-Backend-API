# Everly API 端點文檔

本文檔詳細說明了 Everly 後端 API 的所有端點，包括必要的請求參數和響應格式，供前端開發人員參考。

## 目錄

- [認證相關](#認證相關)
  - [Google OAuth 登錄](#google-oauth-登錄)
  - [獲取當前用戶信息](#獲取當前用戶信息)
- [用戶設定相關](#用戶設定相關)
  - [更新用戶個人資料](#更新用戶個人資料)
  - [上傳用戶頭像](#上傳用戶頭像)
  - [獲取用戶偏好設定](#獲取用戶偏好設定)
  - [更新用戶偏好設定](#更新用戶偏好設定)
- [日記相關](#日記相關)
  - [獲取用戶日記列表](#獲取用戶日記列表)
  - [創建新日記](#創建新日記)
  - [獲取特定日記](#獲取特定日記)
  - [更新日記](#更新日記)
  - [刪除日記](#刪除日記)
- [日記條目相關](#日記條目相關)
  - [獲取日記條目列表](#獲取日記條目列表)
  - [創建新日記條目](#創建新日記條目)
  - [獲取特定日記條目](#獲取特定日記條目)
  - [更新日記條目](#更新日記條目)
  - [刪除日記條目](#刪除日記條目)
- [媒體相關](#媒體相關)
  - [上傳媒體文件](#上傳媒體文件)

## 認證相關

### Google OAuth 登錄

**端點**: `POST /api/v1/auth/google`

使用 Google OAuth 訪問令牌進行認證。

**請求體**:

```json
{
  "token": "google-oauth-access-token"
}
```

**響應**:

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

**錯誤情況**:
- 400 Bad Request: 缺少 token 或 token 格式不正確
- 401 Unauthorized: Google token 無效或已過期
- 500 Internal Server Error: 服務器處理錯誤

### 獲取當前用戶信息

**端點**: `GET /api/v1/auth/me`

獲取當前已認證用戶的信息。

**請求頭**:
```
Authorization: Bearer {jwt-token}
```

**響應**:

```json
{
  "status": "success",
  "data": {
    "id": "user-id",
    "email": "user@example.com",
    "full_name": "用戶名稱",
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

**錯誤情況**:
- 401 Unauthorized: 未提供 token 或 token 無效
- 500 Internal Server Error: 服務器處理錯誤

## 用戶設定相關

### 更新用戶個人資料

**端點**: `PUT /api/v1/users/me`

更新用戶的名稱等個人資料信息。

**請求頭**:
```
Authorization: Bearer {jwt-token}
Content-Type: application/json
```

**請求體**:

```json
{
  "full_name": "新用戶名稱"
}
```

**響應**:

```json
{
  "status": "success",
  "data": {
    "id": "user-id",
    "email": "user@example.com",
    "full_name": "新用戶名稱",
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

**錯誤情況**:
- 400 Bad Request: 請求格式不正確
- 401 Unauthorized: 未提供 token 或 token 無效
- 500 Internal Server Error: 服務器處理錯誤

### 上傳用戶頭像

**端點**: `PUT /api/v1/users/me/profile-picture`

上傳或更新用戶頭像。

**請求頭**:
```
Authorization: Bearer {jwt-token}
Content-Type: multipart/form-data
```

**請求參數**:
- `file`: 圖片文件（支持 .jpg, .jpeg, .png, .gif 格式）

**響應**:

```json
{
  "status": "success",
  "data": {
    "id": "user-id",
    "email": "user@example.com",
    "full_name": "用戶名稱",
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

**錯誤情況**:
- 400 Bad Request: 文件格式不支持或文件無效
- 401 Unauthorized: 未提供 token 或 token 無效
- 500 Internal Server Error: 上傳失敗或服務器處理錯誤

### 獲取用戶偏好設定

**端點**: `GET /api/v1/users/me/preferences`

獲取用戶的偏好設定，如語言和主題。

**請求頭**:
```
Authorization: Bearer {jwt-token}
```

**響應**:

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

**錯誤情況**:
- 401 Unauthorized: 未提供 token 或 token 無效
- 500 Internal Server Error: 服務器處理錯誤

### 更新用戶偏好設定

**端點**: `PUT /api/v1/users/me/preferences`

更新用戶的偏好設定，如語言和主題。

**請求頭**:
```
Authorization: Bearer {jwt-token}
Content-Type: application/json
```

**請求體**:

```json
{
  "language": "zh-TW",
  "theme": "dark"
}
```

**響應**:

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

**錯誤情況**:
- 400 Bad Request: 請求格式不正確
- 401 Unauthorized: 未提供 token 或 token 無效
- 500 Internal Server Error: 服務器處理錯誤

## 日記相關

### 獲取用戶日記列表

**端點**: `GET /api/v1/diaries`

獲取當前用戶的所有日記。

**請求頭**:
```
Authorization: Bearer {jwt-token}
```

**響應**:

```json
{
  "status": "success",
  "data": [
    {
      "id": "diary-id-1",
      "title": "旅行日記",
      "description": "記錄我的旅行經歷",
      "cover_image": "https://example.com/cover1.jpg",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-02T00:00:00Z",
      "entry_count": 12
    },
    {
      "id": "diary-id-2",
      "title": "日常隨筆",
      "description": "我的日常思考",
      "cover_image": null,
      "created_at": "2025-02-01T00:00:00Z",
      "updated_at": "2025-02-05T00:00:00Z",
      "entry_count": 5
    }
  ],
  "message": "Diaries retrieved successfully"
}
```

**錯誤情況**:
- 401 Unauthorized: 未提供 token 或 token 無效
- 500 Internal Server Error: 服務器處理錯誤

### 創建新日記

**端點**: `POST /api/v1/diaries`

創建一個新的日記。

**請求頭**:
```
Authorization: Bearer {jwt-token}
Content-Type: application/json
```

**請求體**:

```json
{
  "title": "旅行日記",
  "description": "記錄我的旅行經歷",
  "cover_image": "https://example.com/cover1.jpg"
}
```

**響應**:

```json
{
  "status": "success",
  "data": {
    "id": "new-diary-id",
    "title": "旅行日記",
    "description": "記錄我的旅行經歷",
    "cover_image": "https://example.com/cover1.jpg",
    "created_at": "2025-05-01T00:00:00Z",
    "updated_at": "2025-05-01T00:00:00Z",
    "entry_count": 0
  },
  "message": "Diary created successfully"
}
```

**錯誤情況**:
- 400 Bad Request: 請求格式不正確或缺少必要字段
- 401 Unauthorized: 未提供 token 或 token 無效
- 500 Internal Server Error: 服務器處理錯誤

### 獲取特定日記

**端點**: `GET /api/v1/diaries/{diary_id}`

獲取特定日記的詳細信息。

**請求頭**:
```
Authorization: Bearer {jwt-token}
```

**路徑參數**:
- `diary_id`: 日記的唯一標識符

**響應**:

```json
{
  "status": "success",
  "data": {
    "id": "diary-id",
    "title": "旅行日記",
    "description": "記錄我的旅行經歷",
    "cover_image": "https://example.com/cover1.jpg",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-02T00:00:00Z",
    "entry_count": 12
  },
  "message": "Diary retrieved successfully"
}
```

**錯誤情況**:
- 401 Unauthorized: 未提供 token 或 token 無效
- 403 Forbidden: 用戶無權訪問該日記
- 404 Not Found: 指定的日記不存在
- 500 Internal Server Error: 服務器處理錯誤

### 更新日記

**端點**: `PUT /api/v1/diaries/{diary_id}`

更新特定日記的信息。

**請求頭**:
```
Authorization: Bearer {jwt-token}
Content-Type: application/json
```

**路徑參數**:
- `diary_id`: 日記的唯一標識符

**請求體**:

```json
{
  "title": "更新後的旅行日記",
  "description": "新的描述",
  "cover_image": "https://example.com/newcover.jpg"
}
```

**響應**:

```json
{
  "status": "success",
  "data": {
    "id": "diary-id",
    "title": "更新後的旅行日記",
    "description": "新的描述",
    "cover_image": "https://example.com/newcover.jpg",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-05-05T00:00:00Z",
    "entry_count": 12
  },
  "message": "Diary updated successfully"
}
```

**錯誤情況**:
- 400 Bad Request: 請求格式不正確
- 401 Unauthorized: 未提供 token 或 token 無效
- 403 Forbidden: 用戶無權修改該日記
- 404 Not Found: 指定的日記不存在
- 500 Internal Server Error: 服務器處理錯誤

### 刪除日記

**端點**: `DELETE /api/v1/diaries/{diary_id}`

刪除特定日記及其所有條目。

**請求頭**:
```
Authorization: Bearer {jwt-token}
```

**路徑參數**:
- `diary_id`: 日記的唯一標識符

**響應**:

```json
{
  "status": "success",
  "data": null,
  "message": "Diary deleted successfully"
}
```

**錯誤情況**:
- 401 Unauthorized: 未提供 token 或 token 無效
- 403 Forbidden: 用戶無權刪除該日記
- 404 Not Found: 指定的日記不存在
- 500 Internal Server Error: 服務器處理錯誤

## 日記條目相關

### 獲取日記條目列表

**端點**: `GET /api/v1/diaries/{diary_id}/entries`

獲取特定日記的條目列表。

**請求頭**:
```
Authorization: Bearer {jwt-token}
```

**路徑參數**:
- `diary_id`: 日記的唯一標識符

**查詢參數**:
- `page` (可選): 頁碼，默認為 1
- `limit` (可選): 每頁條目數，默認為 10
- `sort` (可選): 排序順序，"asc" 或 "desc"，默認為 "desc"

**響應**:

```json
{
  "status": "success",
  "data": {
    "entries": [
      {
        "id": "entry-id-1",
        "title": "巴黎第一天",
        "content": "今天我參觀了艾菲爾鐵塔...",
        "content_type": "text",
        "location": {
          "name": "巴黎，法國",
          "lat": 48.8566,
          "lng": 2.3522
        },
        "media": [],
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
      },
      {
        "id": "entry-id-2",
        "title": "巴黎聖母院",
        "content": "建築真是太驚人了！",
        "content_type": "mixed",
        "location": {
          "name": "巴黎聖母院，巴黎",
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

**錯誤情況**:
- 401 Unauthorized: 未提供 token 或 token 無效
- 403 Forbidden: 用戶無權訪問該日記
- 404 Not Found: 指定的日記不存在
- 500 Internal Server Error: 服務器處理錯誤

### 創建新日記條目

**端點**: `POST /api/v1/diaries/{diary_id}/entries`

在指定日記中創建新條目。

**請求頭**:
```
Authorization: Bearer {jwt-token}
Content-Type: application/json
```

**路徑參數**:
- `diary_id`: 日記的唯一標識符

**請求體**:

```json
{
  "title": "巴黎第一天",
  "content": "今天我參觀了艾菲爾鐵塔...",
  "content_type": "text",
  "location": {
    "name": "巴黎，法國",
    "lat": 48.8566,
    "lng": 2.3522
  },
  "media": []
}
```

**響應**:

```json
{
  "status": "success",
  "data": {
    "id": "new-entry-id",
    "title": "巴黎第一天",
    "content": "今天我參觀了艾菲爾鐵塔...",
    "content_type": "text",
    "location": {
      "name": "巴黎，法國",
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

**錯誤情況**:
- 400 Bad Request: 請求格式不正確或缺少必要字段
- 401 Unauthorized: 未提供 token 或 token 無效
- 403 Forbidden: 用戶無權訪問該日記
- 404 Not Found: 指定的日記不存在
- 500 Internal Server Error: 服務器處理錯誤

### 獲取特定日記條目

**端點**: `GET /api/v1/diaries/{diary_id}/entries/{entry_id}`

獲取特定日記條目的詳細信息。

**請求頭**:
```
Authorization: Bearer {jwt-token}
```

**路徑參數**:
- `diary_id`: 日記的唯一標識符
- `entry_id`: 條目的唯一標識符

**響應**:

```json
{
  "status": "success",
  "data": {
    "id": "entry-id",
    "title": "巴黎第一天",
    "content": "今天我參觀了艾菲爾鐵塔...",
    "content_type": "text",
    "location": {
      "name": "巴黎，法國",
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

**錯誤情況**:
- 401 Unauthorized: 未提供 token 或 token 無效
- 403 Forbidden: 用戶無權訪問該日記或條目
- 404 Not Found: 指定的日記或條目不存在
- 500 Internal Server Error: 服務器處理錯誤

### 更新日記條目

**端點**: `PUT /api/v1/diaries/{diary_id}/entries/{entry_id}`

更新特定日記條目的信息。

**請求頭**:
```
Authorization: Bearer {jwt-token}
Content-Type: application/json
```

**路徑參數**:
- `diary_id`: 日記的唯一標識符
- `entry_id`: 條目的唯一標識符

**請求體**:

```json
{
  "title": "更新：巴黎第一天",
  "content": "今天我參觀了艾菲爾鐵塔和盧浮宮...",
  "content_type": "text",
  "location": {
    "name": "巴黎，法國",
    "lat": 48.8566,
    "lng": 2.3522
  },
  "media": []
}
```

**響應**:

```json
{
  "status": "success",
  "data": {
    "id": "entry-id",
    "title": "更新：巴黎第一天",
    "content": "今天我參觀了艾菲爾鐵塔和盧浮宮...",
    "content_type": "text",
    "location": {
      "name": "巴黎，法國",
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

**錯誤情況**:
- 400 Bad Request: 請求格式不正確
- 401 Unauthorized: 未提供 token 或 token 無效
- 403 Forbidden: 用戶無權修改該日記或條目
- 404 Not Found: 指定的日記或條目不存在
- 500 Internal Server Error: 服務器處理錯誤

### 刪除日記條目

**端點**: `DELETE /api/v1/diaries/{diary_id}/entries/{entry_id}`

刪除特定日記條目。

**請求頭**:
```
Authorization: Bearer {jwt-token}
```

**路徑參數**:
- `diary_id`: 日記的唯一標識符
- `entry_id`: 條目的唯一標識符

**響應**:

```json
{
  "status": "success",
  "data": null,
  "message": "Entry deleted successfully"
}
```

**錯誤情況**:
- 401 Unauthorized: 未提供 token 或 token 無效
- 403 Forbidden: 用戶無權刪除該日記或條目
- 404 Not Found: 指定的日記或條目不存在
- 500 Internal Server Error: 服務器處理錯誤

## 媒體相關

### 上傳媒體文件

**端點**: `POST /api/v1/media/upload`

上傳媒體文件（圖片、音頻或視頻）以在日記條目中使用。

**請求頭**:
```
Authorization: Bearer {jwt-token}
Content-Type: multipart/form-data
```

**請求參數**:
- `file`: 媒體文件

**響應**:

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

**錯誤情況**:
- 400 Bad Request: 文件格式不支持或文件無效
- 401 Unauthorized: 未提供 token 或 token 無效
- 413 Payload Too Large: 文件大小超過限制
- 500 Internal Server Error: 上傳失敗或服務器處理錯誤 