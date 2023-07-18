from pydantic import BaseSettings


class Settings(BaseSettings):
    MONGO_INITDB_DATABASE: str
    DATABASE_URL: str

    class Config:
        env_file = './.env'

settings = Settings()