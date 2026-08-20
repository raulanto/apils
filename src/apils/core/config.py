from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Apils API"
    api_v1_prefix: str = "/api/v1"

    # "development" | "production" — controls cookie_secure default below.
    environment: str = "development"

    # Optional DB config for later
    database_url: str | None = None

    # Upload directory
    upload_dir: str = "data/uploads"

    # Auth
    secret_key: str = "change_this_to_a_secure_random_string_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # Refresh token cookie. secure=False lets it work over plain http://localhost
    # in dev; set ENVIRONMENT=production (or override directly) for real deployments.
    # samesite="none" requires cookie_secure=True (browser requirement) — needed if the
    # frontend is hosted on a different site than this API.
    cookie_secure: bool | None = True
    cookie_samesite: str = "none"

    # CORS
    frontend_cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def resolved_cookie_secure(self) -> bool:
        if self.cookie_secure is not None:
            return self.cookie_secure
        return self.environment != "development"


settings = Settings()
