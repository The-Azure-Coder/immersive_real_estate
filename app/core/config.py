from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    NANOBANANA_API_KEY: str

    # S3 settings (optional)
    USE_S3: bool = False
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: Optional[str] = "us-east-1"

    # Local storage
    LOCAL_STORAGE_PATH: str = "./uploads"

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """
        Handle Render's postgres:// prefix by converting it to postgresql://
        as required by SQLAlchemy.
        """
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
