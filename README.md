# Everly Backend API

Backend service for Everly - Your Personal Diary and Travel Journal with AI Integration

## Overview

Everly is an iOS/Android application that helps users capture and organize their thoughts, experiences, and travel journeys through various media formats, enhanced with AI capabilities.

### Key Features

- Multi-format diary entries (text, image, audio, drawing, video)
- Travel location tracking and memories
- AI-powered content analysis and personalization
- Google authentication
- Cloud synchronization

## Technical Stack

- **Framework**: FastAPI (Python)
- **Databases**: MongoDB (via MongoEngine) + Redis
- **Authentication**: Google OAuth 2.0 with JWT
- **AI Integration**: Sentiment analysis, entity extraction, topic modeling

## Setup Instructions

### Prerequisites

- Python 3.9+
- MongoDB
- Redis
- Poetry (recommended) or pip

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/everly-backend.git
   cd everly-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # For development:
   pip install -r requirements-dev.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration values
   ```

### Database Setup

1. MongoDB:
   - Install MongoDB or use MongoDB Atlas
   - Update the MongoDB connection string in `.env`

2. Redis:
   - Install Redis or use a hosted service
   - Update Redis connection details in `.env`

### Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

API Documentation is available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### Authentication

- `POST /api/v1/auth/google`: Authenticate with Google OAuth
- `GET /api/v1/auth/me`: Get current user information

### Users

- `GET /api/v1/users/me`: Get current user profile
- `PUT /api/v1/users/me`: Update user profile
- `GET /api/v1/users/me/preferences`: Get user preferences
- `PUT /api/v1/users/me/preferences`: Update user preferences

### Diaries

- `POST /api/v1/diaries`: Create a new diary entry
- `GET /api/v1/diaries`: List user's diary entries
- `GET /api/v1/diaries/{entry_id}`: Get a specific diary entry
- `PUT /api/v1/diaries/{entry_id}`: Update a diary entry
- `DELETE /api/v1/diaries/{entry_id}`: Delete a diary entry
- `POST /api/v1/diaries/search`: Search diary entries with filters

## Development

### Testing

```bash
pytest
# With coverage:
pytest --cov=app tests/
```

### Code Formatting

```bash
# Format code
black app tests

# Sort imports
isort app tests
```

### Code Linting

```bash
flake8 app tests
mypy app
```

## Deployment

### Docker Deployment

```bash
docker build -t everly-backend .
docker run -p 8000:8000 everly-backend
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

## License

This project is proprietary and confidential.

## Contact

For any inquiries, please contact:
- Developer: your.email@example.com

# Everly API 測試客戶端

這是一個用於測試 Everly 後端 API 的命令行工具。可用於自動、手動或模擬前端的各種操作，幫助開發人員測試和驗證 API 功能。

## 功能特點

- 設置後端 API 地址
- Google OAuth 登入流程
- 用戶信息管理
- 日記條目的 CRUD 操作
- 自動化測試流程
- 配置保存和加載

## 安裝與設置

1. 確保已安裝 Python 3.8 或更高版本
2. 克隆此倉庫或下載源代碼
3. 安裝依賴包:

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

直接運行腳本啟動測試客戶端:

```bash
python test_client.py
```

首次運行時，會提示您輸入後端 API 的基礎 URL。

### 命令行參數

```bash
python test_client.py --url=http://localhost:8000 --token=your_access_token --autotest
```

- `--url`: 設置後端 API 基礎 URL
- `--token`: 使用已有的訪問令牌
- `--autotest`: 直接執行自動化測試

## 主要功能

### 1. 設置後端 API URL

設置要連接的 Everly 後端 API 地址。

### 2. Google 登入

提供 Google OAuth 登入流程，引導您完成身份驗證並獲取訪問令牌。

### 3. 用戶信息

獲取當前登入用戶的詳細信息。

### 4. 日記條目管理

- 獲取日記條目列表
- 創建新的日記條目
- 查看日記條目詳情
- 更新現有日記條目
- 刪除日記條目
- 搜索日記條目

### 5. 自動化測試

執行自動化測試流程，測試 API 的主要功能點。

## 注意事項

- 請確保後端 API 服務器正在運行
- Google 登入需要在後端正確配置 OAuth 憑證
- 訪問令牌會臨時保存在本地配置文件中

## 開發者信息

此測試客戶端由 Everly 團隊開發，用於內部測試和開發。
