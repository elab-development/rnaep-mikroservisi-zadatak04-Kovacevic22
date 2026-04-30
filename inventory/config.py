from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    redis_host: str
    redis_port: int
    redis_password: str | None = None
    inventory_url: str
    frontend_url: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()