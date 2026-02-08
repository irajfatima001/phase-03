from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str

    # Auth settings
    BETTER_AUTH_SECRET: str
    BETTER_AUTH_URL: str

    # Cohere settings
    COHERE_API_KEY: str

    # Application settings
    APP_NAME: str = "AI Todo Chatbot API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # CORS settings
    BACKEND_CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    def get_database_url(self) -> str:
        """Return async-compatible database URL"""
        db_url = self.DATABASE_URL
        if db_url.startswith("postgresql://"):
            # Check if the URL has query parameters and handle them appropriately
            if "?" in db_url:
                base_url, params = db_url.split("?", 1)
                # Remove sslmode and channel_binding parameters that may not be supported
                params_parts = [p for p in params.split("&") if not p.startswith("sslmode=") and not p.startswith("channel_binding=")]
                clean_params = "&".join(params_parts)
                clean_url = f"{base_url}?{clean_params}" if clean_params else base_url
                return clean_url.replace(
                    "postgresql://",
                    "postgresql+asyncpg://",
                    1
                )
            else:
                return db_url.replace(
                    "postgresql://",
                    "postgresql+asyncpg://",
                    1
                )
        return db_url


settings = Settings()
