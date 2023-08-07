from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from app.iternal.models.user import RegUser

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login")
async def post_login(request: Request, response: Response, payload: RegUser = Body(...)):
    payload = jsonable_encoder(payload)

    # Connect to DB connection
    database = request.app.state.database
    users_colection = database.get_collection("users")

    password = payload.get('password')
    login = payload.get('login')

    filter = {'login': login}
    result = await users_colection.find_one(filter)

    if (result is None):
        # Exception
        return JSONResponse(content={"message": 'Invalid login', "data": 0}, status_code=403)

    hash_password = result.get('password')
    company_keys = result.get('company_key')

    verification = request.app.state.r_session.verify_key(
        password, hash_password)

    if (not verification):
        # Exception
        return JSONResponse(content={"message": 'Invalid password', "data": 0}, status_code=403)

    # Verify login and password
    session_data = {'login': login, 'role': -1}
    session_id = request.app.state.r_session.create_session(request,
                                                            response,
                                                            session_data)

    return {'message': 'Success login', 'data': {"session_id": session_id, "company_keys": company_keys}}


@router.post("/login/{company_key}")
async def post_login(request: Request, response: Response, company_key: str):
    session = request.app.state.r_session.protected_session(
        request, response, -1)

    if len(session) <= 0:
        # Exception
        return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

    # Connect to DB connection
    database = request.app.state.database
    users_colection = database.get_collection("users")

    login = session.get("login")

    filter = {'login': login}
    result = await users_colection.find_one(filter)

    role = result.get("role")
    company_keys = result.get("company_key")

    if (company_key not in company_keys):
        # Exception
        return JSONResponse(content={"message": "Invalid company_key"}, status_code=403)

    # Verify login and password
    session_data = {'login': login, 'role': role, "company_key": company_key}
    session_id = request.app.state.r_session.create_session(request,
                                                            response,
                                                            session_data)

    filter = {'login': login}
    update = {'$set': {'session_id': session_id}}

    users_colection.update_one(filter, update)

    return {'message': 'Success login', 'data': {"session_id": session_id, "company_key": company_key}}


@router.post('/logout')
def post_logout(request: Request, response: Response) -> dict:
    request.app.state.r_session.end_session(request, response)
    return {'message': 'Logout successful', 'data': 0}
