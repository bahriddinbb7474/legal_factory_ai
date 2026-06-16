from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Legal Factory AI"
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/legal_factory_ai"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_timeout_seconds: float = 30.0
    openrouter_max_output_tokens: int = 1200
    openrouter_app_referer: str = ""
    openrouter_app_title: str = "Legal Factory AI"
    document_vision_model: str = ""
    document_vision_provider: str = ""
    max_upload_size_mb: int = 25
    xlsx_max_rows: int = 1000
    monthly_budget_usd: float = 100.0
    budget_warning_percent: int = 80
    block_expensive_calls: bool = False
    embedding_model: str = ""
    embedding_provider: str = ""
    embedding_dimensions: int = 0
    dev_current_user_role: str = "admin"
    dev_current_user_id: int = 1
    cors_origins: str = "http://127.0.0.1:3000,http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
