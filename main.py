import uvicorn

WORKERS_COUNT = 10
HOST='0.0.0.0'
PORT=8000
RELOAD=True

if __name__ == "__main__":
    uvicorn.run("app.main:server", host=HOST, port=PORT, reload=RELOAD, workers=WORKERS_COUNT)

    #*to run locally replace with and uncomment the file app/__init__.py
    #uvicorn.run("app:create_app", host=HOST, port=PORT, reload=RELOAD, workers=WORKERS_COUNT)