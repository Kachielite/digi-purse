from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_host: str
    database_name: str
    database_password: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
