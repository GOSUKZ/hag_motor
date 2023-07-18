from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    MONGO_INITDB_DATABASE: str = os.environ.get('MONGO_INITDB_DATABASE')
    DATABASE_URL: str = os.environ.get('MONGODB_URI')

    class Config:
        env_file = f'{os.path.dirname(os.path.abspath(__file__))}/app/.env'

settings = Settings()