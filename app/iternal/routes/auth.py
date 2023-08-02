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
async def post_login(request: Request, response: Response, login: str, password: str):
    # Connect to DB connection
    database = request.app.state.mongodb["Dina_Cargo"]
    users_colection = database.get_collection("users")

    filter = {'login': login}
    result = await users_colection.find_one(filter)

    if (result is None):
        # Exception
        return JSONResponse(content={"message": 'Invalid login', "data": 0}, status_code=403)
    
    hash_password = result.get('password')
    role = result.get('role')
    company_key = result.get('company_key')
    
    verification = request.app.state.r_session.verify_key(password, hash_password)

    if (not verification):
        # Exception
        return JSONResponse(content={"message": 'Invalid password', "data": 0}, status_code=403)
    
    # Verify login and password
    # TODO: hash password
    session_data = {'username': login, 'role': role, 'company_key': company_key}
    session_id = request.app.state.r_session.create_session(request, response, session_data)
    return {'message': 'Login successful', 'session_id': session_id}


@router.post('/logout')
def post_logout(request: Request, response: Response) -> dict:
    request.app.state.r_session.end_session(request, response)
    return {'message': 'Logout successful', 'session_id': 0}


@router.get('/protected')
def get_protected(request: Request, response: Response) -> dict:
    session = request.app.state.r_session.protected_session(request, response)
    print('session: ', session)
    if len(session) > 0:
        return {'message': 'Access granted'}
    else:
        return {'message': 'Access denied'}
    

@router.post('/restricted/')
async def post_restricted(request: Request, payload: RegUser = Body(...)):
    payload = jsonable_encoder(payload)

    now = datetime.utcnow()

    # Connect to DB connection
    database = request.app.state.mongodb["Dina_Cargo"]
    users_colection = database.get_collection("users")

    payload["role"] = 1
    payload["company_key"] = "Dina_Cargo"
    payload["created_at"] = now

    payload["password"] = request.app.state.r_session.generate_hashed_key(payload["password"])

    await users_colection.insert_one(payload)

    print('payload: ', payload)

