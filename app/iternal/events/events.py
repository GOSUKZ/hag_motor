import asyncio
from app.iternal.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from app.iternal.config import settings

DATABASE_URL = settings.DATABASE_URL
MONGO_INITDB_DATABASE = settings.MONGO_INITDB_DATABASE

def startup_event(app) -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(DATABASE_URL)
    client.get_io_loop = asyncio.get_event_loop
    app.state.mongodb = client
    app.state.database = app.state.mongodb[MONGO_INITDB_DATABASE]
    print("startup_event")
    
def shutdown_event(app):
    app.state.mongodb.close()
    print("shutdown_event")
