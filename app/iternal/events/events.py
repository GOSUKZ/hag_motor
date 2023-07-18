from app.iternal.config import settings

DATABASE_URL = settings.DATABASE_URL

from motor.motor_asyncio import AsyncIOMotorClient


def startup_event(app) -> AsyncIOMotorClient:
    app.state.mongodb = AsyncIOMotorClient(DATABASE_URL)
    print("startup_event")
    
def shutdown_event(app):
    app.state.mongodb.close()
    print("shutdown_event")
    
