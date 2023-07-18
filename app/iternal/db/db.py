import motor.motor_asyncio

from app.iternal.config import settings

DATABASE_URL = settings.DATABASE_URL
MONGO_INITDB_DATABASE = settings.MONGO_INITDB_DATABASE

client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
database = client[MONGO_INITDB_DATABASE]