from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    postgres_db: str = "codeatlas"
    postgres_user: str = "codeatlas"
    postgres_password: str = "codeatlas_dev_password"
    postgres_host: str = "postgres"
    redis_url: str = "redis://redis:6379/0"
    @property
    def postgres_dsn(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:5432/{self.postgres_db}"

@lru_cache
def get_settings() -> Settings:
    return Settings()
