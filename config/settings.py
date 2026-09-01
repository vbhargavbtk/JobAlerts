"""
Central Configuration & Settings Module
Loads environment variables safely using Pydantic Settings.
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    APP_PORT: int = 8000
    APP_HOST: str = "0.0.0.0"
    ADMIN_SECRET_KEY: str = "default_dev_secret_key_change_in_prod"

    # Telegram User Account Listener (Telethon)
    TELEGRAM_API_ID: Optional[int] = None
    TELEGRAM_API_HASH: Optional[str] = None
    TELEGRAM_SESSION: Optional[str] = None

    # Telegram Bot for Outgoing Alerts
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ALERT_CHAT_ID: Optional[int] = None

    # Database URL
    DATABASE_URL: str = "sqlite+aiosqlite:///./job_alerts.db"

    # n8n Orchestration
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook/job-event"
    N8N_API_KEY: Optional[str] = None

    # AI Provider 1: NVIDIA NIM
    NIM_API_KEY: Optional[str] = None
    NIM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NIM_MODEL: str = "mistralai/mistral-large-2-instruct"

    # AI Provider 2: Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-flash-lite-latest"

    # AI Provider 3: OpenRouter
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "google/gemma-4-31b-it:free"

    # Content Acquisition Settings
    TAVILY_API_KEY: Optional[str] = None
    MAX_PDF_SIZE_MB: int = 25
    HTTP_TIMEOUT_SECONDS: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
