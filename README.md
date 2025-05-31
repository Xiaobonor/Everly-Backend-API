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

### Pre-commit Hooks

This project uses pre-commit to enforce consistent code style and quality. To install and run hooks locally:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```
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

# Everly API Test Client

This is a command-line tool for testing the Everly backend API. It can be used for automatic, manual, or simulated frontend operations to help developers test and validate API functionality.

## Features

- Set up backend API URL
- Google OAuth login flow
- User information management
- CRUD operations for diary entries
- Automated testing workflows
- Configuration saving and loading

## Installation and Setup

1. Ensure Python 3.8 or higher is installed
2. Clone this repository or download the source code
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the script directly to start the test client:

```bash
python test_client.py
```

On first run, you will be prompted to enter the base URL of the backend API.

### Command Line Arguments

```bash
python test_client.py --url=http://localhost:8000 --token=your_access_token --autotest
```

- `--url`: Set the backend API base URL
- `--token`: Use an existing access token
- `--autotest`: Run automated tests directly

## Main Functions

### 1. Set Backend API URL

Set the Everly backend API address to connect to.

### 2. Google Login

Provides a Google OAuth login flow, guiding you through authentication to obtain an access token.

### 3. User Information

Get detailed information about the currently logged-in user.

### 4. Diary Entry Management

- Get list of diary entries
- Create new diary entries
- View diary entry details
- Update existing diary entries
- Delete diary entries
- Search diary entries

### 5. Automated Testing

Run automated test workflows to test the main API functionality.

## Notes

- Ensure the backend API server is running
- Google login requires proper OAuth credentials configuration in the backend
- Access tokens are temporarily saved in a local configuration file

## Developer Information

This test client was developed by the Everly team for internal testing and development.
