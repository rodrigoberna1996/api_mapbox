"""Application configuration via environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Load configuration from environment variables or .env files."""

    app_name: str = "api-mapbox"
    debug: bool = False
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/api_mapbox"
    )

    model_config = SettingsConfigDict(env_file=('.env',), env_prefix='API_MAPBOX_')

    @property
    def async_database_url(self) -> str:
        """Ensure the database URL uses the asyncpg driver when connecting to PostgreSQL."""
        url = make_url(self.database_url)
        driver = url.drivername
        if driver.startswith("postgresql") and "+asyncpg" not in driver:
            url = url.set(drivername="postgresql+asyncpg")
        return url.render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
