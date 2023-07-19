import uvicorn
from app.iternal.config import settings

WORKERS_COUNT = settings.WORKERS_COUNT
HOST=settings.HOST
PORT=settings.PORT
RELOAD=settings.RELOAD

if __name__ == "__main__":
    uvicorn.run("app.main:server", host=HOST, port=PORT, reload=RELOAD, workers=WORKERS_COUNT)

    #*to run locally replace with and uncomment the file app/__init__.py
    #uvicorn.run("app:create_app", host=HOST, port=PORT, reload=RELOAD, workers=WORKERS_COUNT)