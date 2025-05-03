#!/usr/bin/env python
"""
Run Script - Everly Backend Service Launcher
Usage: python run.py [--host HOST] [--port PORT] [--reload]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check and install necessary dependencies."""
    try:
        import pydantic_settings
    except ImportError:
        print("Installing pydantic-settings...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic-settings"])

    try:
        import dotenv
    except ImportError:
        print("Installing python-dotenv...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])


def check_env_file():
    """Check if .env file exists, create an example file if not."""
    env_file = Path(".env")
    if not env_file.exists():
        print(".env file not found, creating example file...")
        example = """
# API Settings
API_VERSION=v1
DEBUG=True
PROJECT_NAME=Everly API
ENV=development

# MongoDB Settings
MONGODB_URL=mongodb://localhost:27017/everly
MONGODB_DATABASE=everly

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379

# Authentication
JWT_SECRET=everly-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=604800  # 7 days

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# AI Services
OPENAI_API_KEY=your-openai-api-key

# Server
HOST=0.0.0.0
PORT=8000
"""
        with open(".env", "w", encoding="utf-8") as f:
            f.write(example.strip())
        print(".env example file created. Please modify the configuration as needed.")


def run_app(host=None, port=None, reload=False):
    """Run the FastAPI application."""
    # Load configuration from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception as e:
        print(f"Error loading .env file: {e}")

    # Use values from environment variables (if command line arguments are not provided)
    host = host or os.getenv("HOST", "127.0.0.1")
    port = port or int(os.getenv("PORT", "8000"))

    # Build command
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"Starting Everly backend service at http://{host}:{port}")
    print("Press Ctrl+C to stop the service")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nService stopped")


def main():
    """Main function, parse command line arguments and start the application."""
    parser = argparse.ArgumentParser(description="Everly Backend Service Launcher")
    parser.add_argument("--host", help="Host address (default: read from .env file or 127.0.0.1)")
    parser.add_argument("--port", type=int, help="Port number (default: read from .env file or 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable code hot reloading")
    args = parser.parse_args()

    # Check dependencies and environment file
    check_dependencies()
    check_env_file()
    
    # Start the application
    run_app(args.host, args.port, args.reload)


if __name__ == "__main__":
    main() 