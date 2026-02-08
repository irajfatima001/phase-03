from sqlmodel import create_engine
from src.core.config import settings

# Create sync engine for use with SQLModel
# Use the database URL from settings and convert to sync format
def get_sync_db_url():
    # Get the async database URL from settings
    async_db_url = settings.get_database_url()

    # Convert to sync format for SQLModel
    if "postgresql+asyncpg://" in async_db_url:
        sync_url = async_db_url.replace("postgresql+asyncpg://", "postgresql://")
        # Remove query parameters that may not be supported by psycopg2
        if "?sslmode=" in sync_url:
            sync_url = sync_url.split("?sslmode=")[0]
        if "&sslmode=" in sync_url:
            sync_url = sync_url.split("&sslmode=")[0]
        if "?channel_binding=" in sync_url:
            sync_url = sync_url.split("?channel_binding=")[0]
        if "&channel_binding=" in sync_url:
            sync_url = sync_url.split("&channel_binding=")[0]
        return sync_url
    elif "postgres+asyncpg://" in async_db_url:
        sync_url = async_db_url.replace("postgres+asyncpg://", "postgres://")
        # Remove query parameters that may not be supported by psycopg2
        if "?sslmode=" in sync_url:
            sync_url = sync_url.split("?sslmode=")[0]
        if "&sslmode=" in sync_url:
            sync_url = sync_url.split("&sslmode=")[0]
        if "?channel_binding=" in sync_url:
            sync_url = sync_url.split("?channel_binding=")[0]
        if "&channel_binding=" in sync_url:
            sync_url = sync_url.split("&channel_binding=")[0]
        return sync_url
    return async_db_url

engine = create_engine(get_sync_db_url(), echo=True)