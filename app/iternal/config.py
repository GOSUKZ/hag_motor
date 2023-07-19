from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    MONGO_INITDB_DATABASE: str = os.environ.get('MONGO_INITDB_DATABASE')
    DATABASE_URL: str = os.environ.get('MONGODB_URI')

    WORKERS_COUNT: int = os.environ.get('WORKERS_COUNT')
    PORT: int = os.environ.get('PORT')
    RELOAD: bool = os.environ.get('RELOAD')
    HOST: str = os.environ.get('HOST')

    class Config:
        env_file = f'{os.path.dirname(os.path.abspath(__file__))}/app/.env'


#*to run locally replace with
# class Settings(BaseSettings):
#     MONGO_INITDB_DATABASE: str
#     DATABASE_URL: str

#     WORKERS_COUNT: int

#     ...

#     class Config:
#         env_file = './.env'

settings = Settings()