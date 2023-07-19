from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configuration.server import Server

app = FastAPI(
    title="Карга",
    version="0.0.5"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def index():
    return {"message": 'Hello Wor...MongoDB'}

server = Server(app).get_app()