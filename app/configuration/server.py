from fastapi import FastAPI
from app.configuration.routes import __routes__
# from app.iternal.events import events
from app.iternal.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
DATABASE_URL = settings.DATABASE_URL

def startup_event(app) -> AsyncIOMotorClient:
    app.state.mongodb = AsyncIOMotorClient(DATABASE_URL)
    print("startup_event")
    
def shutdown_event(app):
    app.state.mongodb.close()
    print("shutdown_event")

class Server:
    __app: FastAPI

    def __init__(self, app: FastAPI):
        self.__app = app
        self.__register_routs(app)
        self.__register_events(app)


    def get_app(self) -> FastAPI:
        return self.__app

    @staticmethod
    def __register_events(app):
        app.on_event("startup")(lambda: startup_event(app))
        app.on_event("shutdown")(lambda: shutdown_event(app))

    @staticmethod
    def __register_routs(app):
        __routes__.register_routes(app)


    