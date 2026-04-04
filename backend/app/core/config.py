from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "63-45"
    base_currency: str = "USD"

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    database_url: str = "sqlite:///./mini_hedge_fund.db"
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()