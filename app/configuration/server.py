from fastapi import FastAPI
from app.configuration.routes import __routes__
from app.iternal.events import events

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
        app.on_event("startup")(lambda: events.startup_event(app))
        app.on_event("shutdown")(lambda: events.shutdown_event(app))

    @staticmethod
    def __register_routs(app):
        __routes__.register_routes(app)


    