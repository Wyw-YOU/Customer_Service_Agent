from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mall_agent"
    database_url_sync: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/mall_agent"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"

    # LLM
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_model: str = "deepseek-v4-flash"

    # Embedding (local sentence-transformers model)
    embedding_model: str = "all-MiniLM-L6-v2"

    # JWT
    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 1440

    # App
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
