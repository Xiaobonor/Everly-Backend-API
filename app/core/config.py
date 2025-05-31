from pydantic_settings import BaseSettings
from pydantic import Field, AnyHttpUrl, validator


class Settings(BaseSettings):
    """All application settings loaded from environment variables."""

    API_VERSION: str = Field("v1", env="API_VERSION")
    DEBUG: bool = Field(False, env="DEBUG")
    PROJECT_NAME: str = Field("Everly API", env="PROJECT_NAME")
    ENV: str = Field("development", env="ENV")
    BASE_URL: AnyHttpUrl = Field("http://localhost:8000", env="BASE_URL")

    # MongoDB
    MONGODB_URL: str = Field("mongodb://localhost:27017/everly", env="MONGODB_URL")
    MONGODB_DATABASE: str = Field("everly", env="MONGODB_DATABASE")

    # Redis
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: str | None = Field(None, env="REDIS_PASSWORD")

    # JWT
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_SECONDS: int = Field(604800, env="JWT_EXPIRATION_SECONDS")

    # Google OAuth
    GOOGLE_CLIENT_ID: str | None = Field(None, env="GOOGLE_CLIENT_ID")
    GOOGLE_REDIRECT_URI: str | None = Field(None, env="GOOGLE_REDIRECT_URI")

    # OpenAI
    OPENAI_API_KEY: str | None = Field(None, env="OPENAI_API_KEY")

    # HTTP server
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")

    # CORS origins (comma-separated list of allowed origins for future iOS/web clients)
    CORS_ORIGINS: list[AnyHttpUrl] = Field(default_factory=list, env="CORS_ORIGINS")

    @validator("MONGODB_URL")
    def validate_mongodb_url(cls, v: str) -> str:
        """Validate that the MongoDB URL has correct scheme."""
        if not v.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MONGODB_URL must start with mongodb:// or mongodb+srv://")
        return v

    @validator("CORS_ORIGINS", pre=True)
    def _split_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    class Config:
        """Pydantic config class."""

        env_file = ".env"
        case_sensitive = True


# Singleton settings instance for app-wide import
settings = Settings()