from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "63-45"
    base_currency: str = "USD"

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    database_url: str = "sqlite:///./mini_hedge_fund.db"
    frontend_origin: str = "http://localhost:5173"

    kiwoom_base_url: str = "https://api.kiwoom.com"
    kiwoom_mock_base_url: str = "https://mockapi.kiwoom.com"
    kiwoom_use_mock: bool = False

    kiwoom_app_key: str = ""
    kiwoom_secret_key: str = ""
    kiwoom_account_no: str = ""

    kiwoom_timeout_seconds: int = 15
    kiwoom_raw_archive_dir: str = "backend/raw/kiwoom"

    @property
    def kiwoom_active_base_url(self) -> str:
        return self.kiwoom_mock_base_url if self.kiwoom_use_mock else self.kiwoom_base_url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()