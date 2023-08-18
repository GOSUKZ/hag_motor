from asyncio import get_event_loop
from app.iternal.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from app.iternal.db.sessiondb import RSessions
from pymongo import DESCENDING, ASCENDING

DATABASE_URL = settings.DATABASE_URL
MONGO_INITDB_DATABASE = settings.MONGO_INITDB_DATABASE


def startup_event(app) -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(DATABASE_URL)
    client.get_io_loop = get_event_loop

    app.state.mongodb = client
    app.state.database = app.state.mongodb[MONGO_INITDB_DATABASE]

    try:
        control_data_colection = app.state.database.get_collection("control_data")
        control_data_colection.create_index([("company_key", DESCENDING)], unique=True)
    except:
        pass
    try:
        users_colection = app.state.database.get_collection("users")
        users_colection.create_index([("login", ASCENDING)], unique=True)
    except:
        pass
    try:
        api_events_log_colection = app.state.database.get_collection("api_events_log_colection")
        api_events_log_colection.create_index("time", expireAfterSeconds=30*60*60*24)
    except:
        pass

    app.state.r_session: RSessions = RSessions()

    print("startup_event")


def shutdown_event(app):
    app.state.mongodb.close()
    print("shutdown_event")
 