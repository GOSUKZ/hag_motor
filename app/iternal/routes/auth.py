from fastapi import APIRouter, Body, File, UploadFile, Request
from fastapi.responses import JSONResponse, Response
from bson.objectid import ObjectId
from datetime import datetime
from app.iternal.db.sessiondb import RSessions

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

r_session = RSessions()


@router.post("/login")
async def upload_file(request: Request, response: Response, login: str, password: str):

    # Invalidate previous session if logged in
    session = r_session.get_session(request)
    if len(session) > 0:
        r_session.end_session(request, response)

    if login == "admin" and password == "admin":
        session_data = {'username': login, 'logged_in': 1}
        session_id = r_session.create_session(response, session_data)
        return {'message': 'Login successful', 'session_id': session_id}
    else:
        return {'message': 'Invalid username or password', 'session_id': 0}


@router.post('/logout')
def post_logout(request: Request, response: Response) -> dict:
    r_session.end_session(request, response)
    return {'message': 'Logout successful', 'session_id': 0}


@router.get('/protected')
def get_protected(request: Request, response: Response) -> dict:
    if r_session.protected_session(request, response):
        return {'message': 'Access granted'}
    else:
        return {'message': 'Access denied'}
