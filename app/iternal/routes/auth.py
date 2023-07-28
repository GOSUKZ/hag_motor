from fastapi import APIRouter, Body, File, UploadFile, Request
from fastapi.responses import JSONResponse, Response
from bson.objectid import ObjectId
from datetime import datetime

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login")
async def post_login(request: Request, response: Response, login: str, password: str):
    # Verify login and password
    # TODO: hash password
    if login == "admin" and password == "admin":
        session_data = {'username': login}
        session_id = request.app.state.r_session.create_session(request, response, session_data)
        return {'message': 'Login successful', 'session_id': session_id}
    else:
        return {'message': 'Invalid username or password', 'session_id': 0}


@router.post('/logout')
def post_logout(request: Request, response: Response) -> dict:
    request.app.state.r_session.end_session(request, response)
    return {'message': 'Logout successful', 'session_id': 0}


@router.get('/protected')
def get_protected(request: Request, response: Response) -> dict:
    session = request.app.state.r_session.protected_session(request, response)
    if len(session) > 0:
        return {'message': 'Access granted'}
    else:
        return {'message': 'Access denied'}
