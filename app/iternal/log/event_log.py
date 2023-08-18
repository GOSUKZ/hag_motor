from  datetime import datetime
from fastapi import Request, Response
import asyncio

def log_event(request: Request, response: Response , path: str, data: dict = None, message: str = 'ok') -> asyncio.Task:
    return asyncio.create_task(__log_event_task(request, response, path, data, message))

async def __log_event_task(request: Request , response: Response, path: str, data: dict = None, message: str = 'ok') -> None:
    # Connect to DB connection
    database = request.app.state.database
    api_events_log_colection = database.get_collection("api_events_log_colection")

    session = request.app.state.r_session.protected_session(
        request, response, -1)

    if data is None:
        data = {}

    data_in_db = dict()
    
    data_in_db['path'] = path
    data_in_db['time'] = datetime.now()
    data_in_db['data'] = data
    data_in_db['message'] = message
    data_in_db['session'] = session

    await api_events_log_colection.insert_one(data_in_db)