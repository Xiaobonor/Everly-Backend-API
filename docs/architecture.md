# Everly Technical Architecture

## System Overview

Everly is a personal diary and travel journal application built with a modern, scalable architecture. The system consists of a backend API service, a database layer, and caching components. The backend is designed to support multiple frontends including web, iOS, and Android clients.

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  Web Client   │     │  iOS Client   │     │ Android Client│
│               │     │               │     │               │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        │                     │                     │
        └──────────┬──────────┴──────────┬─────────┘
                   │                     │
                   ▼                     ▼
        ┌──────────────────────────────────────────┐
        │                                          │
        │               API Gateway                │
        │                                          │
        └──────────────────┬───────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────┐
        │                                          │
        │          Everly Backend Service          │
        │                                          │
        └┬────────────────┬────────────────┬──────┘
         │                │                │
         ▼                ▼                ▼
┌────────────────┐ ┌─────────────┐ ┌─────────────────┐
│                │ │             │ │                 │
│    MongoDB     │ │    Redis    │ │  AI Services    │
│                │ │             │ │                 │
└────────────────┘ └─────────────┘ └─────────────────┘
```

## Backend Components

### FastAPI Application

The core of the Everly backend is built with FastAPI, a modern, high-performance web framework for building APIs with Python. FastAPI provides:

- Automatic API documentation via OpenAPI and Swagger UI
- Request validation using Pydantic models
- Type hints throughout the codebase
- Asynchronous request handling
- Dependency injection system

### MongoDB Database

Everly uses MongoDB, a NoSQL document database, for storing data:

- Users and authentication information
- Diary entries with rich content
- Media metadata
- Tagging and categorization data

The MongoDB integration uses MongoEngine as an ODM (Object Document Mapper) to provide structured access to the database with validation, type hints, and object-oriented design patterns.

### Redis Cache and Session Store

Redis is used for:

- Session management
- Caching frequently accessed data
- Rate limiting
- Temporary data storage

### Authentication and Security

Authentication is handled through:

- Google OAuth 2.0 for social login
- JWT (JSON Web Tokens) for maintaining authenticated sessions
- HTTPS for all communication

Security measures include:

- CORS (Cross-Origin Resource Sharing) configuration
- Rate limiting to prevent abuse
- Input validation for all endpoints
- Proper error handling

## API Structure

The API follows RESTful principles and is organized into modules:

- `/api/v1/auth`: Authentication endpoints
- `/api/v1/users`: User management endpoints
- `/api/v1/diaries`: Diary entry management endpoints

## Data Models

### User Model

The User model stores user information and preferences:

```python
class User(Document):
    email = EmailField(required=True, unique=True)
    full_name = StringField(required=True, max_length=100)
    profile_picture = URLField()
    google_id = StringField(unique=True, sparse=True)
    role = EnumField(UserRole, default=UserRole.USER)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    last_login = DateTimeField()
    is_active = BooleanField(default=True)
    preferences = ListField(StringField())
```

### Diary Entry Model

The DiaryEntry model represents a single journal entry:

```python
class DiaryEntry(Document):
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
```

## Deployment Architecture

Everly is designed to be deployed in a cloud environment with the following components:

### Development Environment

- Local development using Docker Compose
- MongoDB container for development database
- Redis container for development caching
- FastAPI application with hot reloading

### Production Environment

- Containerized application deployed on Kubernetes
- MongoDB Atlas for managed database service
- Redis Cloud for managed caching service
- Load balancing through cloud provider
- HTTPS termination at the load balancer
- Horizontal scaling for the API service

```
┌─────────────────────┐
│                     │
│   Load Balancer     │
│                     │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│                     │
│   Kubernetes        │
│   Cluster           │
│                     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│                                         │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│ │         │ │         │ │         │     │
│ │ API Pod │ │ API Pod │ │ API Pod │ ... │
│ │         │ │         │ │         │     │
│ └─────────┘ └─────────┘ └─────────┘     │
│                                         │
└─────────────────────────────────────────┘
          │           │
┌─────────▼─┐ ┌───────▼───────┐
│           │ │               │
│ MongoDB   │ │ Redis Cloud   │
│ Atlas     │ │               │
│           │ │               │
└───────────┘ └───────────────┘
```

## AI Features

The Everly backend incorporates AI capabilities for enhancing the user experience:

- **Sentiment Analysis**: Analyzes the emotional tone of diary entries
- **Topic Extraction**: Identifies key themes in the content
- **Entity Recognition**: Detects people, places, and things mentioned
- **Content Recommendations**: Suggests related entries

These AI capabilities are implemented using:

- OpenAI's API for natural language processing
- Asynchronous processing to avoid impacting user experience
- Caching of results to minimize API costs

## Configuration and Environment

The application uses a configuration system based on:

- Environment variables for deployment-specific settings
- `.env` file support for local development
- Pydantic settings class for validation and default values

Key configuration parameters include:

- API version
- MongoDB connection details
- Redis connection details
- JWT secret and expiration time
- Google OAuth credentials
- AI service API keys

## Error Handling and Logging

The application implements comprehensive error handling:

- Structured error responses for API clients
- Global exception handler for unexpected errors
- Detailed logging with different levels (INFO, WARNING, ERROR)
- Correlation IDs for tracking requests across services

## Future Architectural Considerations

The architecture is designed to support future enhancements:

- **Microservices**: Split into smaller, focused services as needed
- **Message Queues**: Add RabbitMQ or Kafka for async processing
- **Full-text Search**: Integrate Elasticsearch for advanced search
- **CDN Integration**: For media content delivery
- **WebSockets**: For real-time updates and notifications 