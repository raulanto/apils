from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Apils API"
    api_v1_prefix: str = "/api/v1"
    
    # Optional DB config for later
    database_url: str | None = None
    
    # Upload directory
    upload_dir: str = "data/uploads"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
