from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configuration.server import Server

app = FastAPI(
    title="MaestroAPI",
    version="0.7.5"
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
    return {"message": 'Hello World'}

server = Server(app).get_app()