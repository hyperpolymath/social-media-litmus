"""Application configuration"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # Service
    port: int = Field(default=3002, alias="ANALYZER_PORT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Database
    database_url: str = Field(..., alias="DATABASE_URL")

    # Redis
    redis_url: str = Field(..., alias="REDIS_URL")

    # OpenAI
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", alias="OPENAI_MODEL")

    # NLP Configuration
    min_confidence_threshold: float = Field(default=0.70, alias="MIN_CONFIDENCE_THRESHOLD")
    spacy_model: str = Field(default="en_core_web_lg", alias="SPACY_MODEL")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:4000", "http://localhost:3000"],
        alias="CORS_ORIGINS"
    )

    # Analysis settings
    max_concurrent_analyses: int = Field(default=5, alias="MAX_CONCURRENT_ANALYSES")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
