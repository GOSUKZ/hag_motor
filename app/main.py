from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configuration.server import Server

app = FastAPI(
    title="Hag",
    version="0.1.9"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie", 'date', 'etag', 'access-control-allow-origin', 'access-control-allow-credentials']
)

@app.get('/')
def index():
    return {"message": 'Hello Wor...MongoDB'}

server = Server(app).get_app() 