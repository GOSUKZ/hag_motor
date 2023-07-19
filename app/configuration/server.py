from fastapi import FastAPI
from app.configuration.routes import __routes__
from app.iternal.events import events
from app.iternal.config import settings

DATABASE_URL = settings.DATABASE_URL

class Server:
    __app: FastAPI

    def __init__(self, app: FastAPI):
        self.__app = app
        self.__register_routs(app)
        self.__register_events(app)
        # startup_event(app) # *if the startup_event does not fire, uncomment it


    def get_app(self) -> FastAPI:
        return self.__app

    @staticmethod
    def __register_events(app):
        app.on_event("startup")(lambda: events.startup_event(app))
        app.on_event("shutdown")(lambda: events.shutdown_event(app))

    @staticmethod
    def __register_routs(app):
        __routes__.register_routes(app)


    