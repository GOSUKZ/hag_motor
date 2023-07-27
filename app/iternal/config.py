from pydantic import BaseSettings
from os import environ, path


class Settings(BaseSettings):
    MONGO_INITDB_DATABASE: str = environ.get('MONGO_INITDB_DATABASE')
    DATABASE_URL: str = environ.get('MONGODB_URI')

    REDIS_HOST: str = environ.get('REDIS_HOST')
    REDIS_PORT: int = environ.get('REDIS_PORT')
    REDIS_PASS: str = environ.get('REDIS_PASS')

    WORKERS_COUNT: int = environ.get('WORKERS_COUNT')
    PORT: int = environ.get('PORT')
    RELOAD: bool = environ.get('RELOAD')
    HOST: str = environ.get('HOST')

    class Config:
        env_file = f'{path.dirname(path.abspath(__file__))}/app/.env'


#*to run locally replace with
# class Settings(BaseSettings):
#     MONGO_INITDB_DATABASE: str
#     DATABASE_URL: str

#     WORKERS_COUNT: int

#     ...

#     class Config:
#         env_file = './.env'

settings = Settings()