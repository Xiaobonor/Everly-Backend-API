"""Authentication API routes."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.modules.auth.schemas import AuthResponse, GoogleAuthRequest, AuthData
from app.modules.auth.services import AuthService
from app.modules.auth.config import AuthConfig
from app.schemas.user import UserResponse, ApiResponse
from app.db.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

# Setup Bearer token authentication
security = HTTPBearer()

# Initialize auth service with config
auth_config = AuthConfig.from_env()
auth_service = AuthService(auth_config)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get the current authenticated user from JWT token."""
    return await auth_service.get_current_user_by_token(credentials.credentials)


@router.post("/google", response_model=AuthResponse)
async def login_with_google(auth_request: GoogleAuthRequest) -> Any:
    """
    Authenticate using Google OAuth token.
    
    Args:
        auth_request: The authentication request containing the Google OAuth access token.
        
    Returns:
        Authentication response with JWT access token.
    """
    logger.info("API request POST /auth/google - Start processing Google authentication")
    
    # Log basic information of the authentication request
    token_length = len(auth_request.token) if auth_request.token else 0
    logger.info(f"Google OAuth token length: {token_length}")
    
    if not auth_request.token:
        logger.error("Received empty Google OAuth token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth token is required"
        )
    
    try:
        # Log start of token verification and user info retrieval
        logger.info("Starting token verification and user info retrieval")
        
        # Verify token and get user info
        user_info = await auth_service.verify_google_token(auth_request.token)
        logger.info("Token verified and user information retrieved successfully")
        
        # Extract user data
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")
        google_id = user_info.get("sub")  # Google's user ID
        
        # Log user info
        logger.info(f"User info obtained - Email: {email}, Name: {name}, Has Google ID: {bool(google_id)}")
        
        if not email:
        logger.error("Google authentication did not provide email")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google authentication"
            )
        
        # Log user lookup or creation
        logger.info(f"Looking up or creating user with email: {email}")
        
        # Find or create user
        user = await auth_service.find_or_create_user(
            email=email,
            name=name or email.split("@")[0],
            picture=picture,
            google_id=google_id
        )
        logger.info(f"User found or created, ID: {user.id}")
        
        # Log access token creation
        logger.info("Creating JWT access token")
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        logger.info("JWT access token created successfully")
        
        auth_data = AuthData(
            access_token=access_token,
            token_type="bearer"
        )
        
        logger.info(f"API request POST /auth/google completed - User {email} logged in successfully")
        
        return AuthResponse(
            status="success",
            data=auth_data,
            message="Authentication successful"
        )
    except Exception as e:
        # Log detailed error information and stack trace
        logger.error(f"Google authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.get("/me", response_model=ApiResponse)
async def get_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current authenticated user information.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        User information.
    """
    logger.info(f"API request GET /auth/me - User ID: {current_user.id}")
    logger.debug(f"Getting current authenticated user info - Request processing started")
    
    preferences_list = []
    if current_user.preferences:
        logger.debug(f"Processing user preferences - {len(current_user.preferences)} items")
        for key, value in current_user.preferences.items():
            if isinstance(value, bytes):
                import base64
                value = base64.b64encode(value).decode('ascii')
            preferences_list.append({"key": key, "value": value})
    
    user_data = {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "profile_picture": current_user.profile_picture,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "preferences": preferences_list
    }
    
    logger.debug(f"User information retrieval successful - Preparing response")
    logger.info(f"API request GET /auth/me completed - User ID: {current_user.id}")
            
    return {
        "status": "success",
        "data": user_data,
        "message": "User information retrieved successfully"
    } 