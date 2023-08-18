from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from app.iternal.models.user import RegUser, LoginUser
from app.iternal.log.event_log import log_event

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# Предварительная авторизация пользователя
@router.post("/login")
async def post_login(request: Request, response: Response, payload: LoginUser = Body(...)):
    payload = jsonable_encoder(payload)

    # Connect to DB connection
    database = request.app.state.database
    users_colection = database.get_collection("users")

    password = payload.get('password')
    login = payload.get('login')

    filter = {'login': login}
    result = await users_colection.find_one(filter)

    # User not in db
    if (result is None):
        log_event(request,
                  response,
                  '/auth/login',
                  payload,
                  'Invalid login')  # Log
        # Exception
        return JSONResponse(content={"message": 'Invalid login', "data": 0}, status_code=403)

    hash_password = result.get('password')
    company_keys = result.get('company_key')

    verification = request.app.state.r_session.verify_key(
        password, hash_password)

    # Pass not valid
    if (not verification):
        log_event(request,
                  response,
                  '/auth/login',
                  payload,
                  'Invalid password')  # Log
        # Exception
        return JSONResponse(content={"message": 'Invalid password', "data": 0}, status_code=403)

    # Verify login and password
    session_data = {'login': login, 'role': -1}
    session_id = request.app.state.r_session.create_session(request,
                                                            response,
                                                            session_data)
    log_event(request,
              response,
              '/auth/login',
              {"session_id": session_id,
                  "company_keys": company_keys, 'payload': payload},
              'Success login')  # Log
    return {'message': 'Success login', 'data': {"session_id": session_id, "company_keys": company_keys}}


# Авторизация пользователя
@router.post("/login/{company_key}")
async def post_login(request: Request, response: Response, company_key: str):
    session = request.app.state.r_session.protected_session(
        request, response, -1)

    if len(session) <= 0:
        log_event(request,
                  response,
                  f'/auth/login/{company_key}',
                  session,
                  'Unauthorized or invalid sesion')  # Log
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
        log_event(request,
                  response,
                  f'/auth/login/{company_key}',
                  {'company_key': company_key},
                  'Invalid company_key')  # Log
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

    log_event(request,
              response,
              f'/auth/login/{company_key}',
              {"session_id": session_id, "company_key": company_key, 'session': session},
              'Success login')  # Log
    return {'message': 'Success login', 'data': {"session_id": session_id, "company_key": company_key}}


# Выход
@router.post('/logout')
async def post_logout(request: Request, response: Response) -> dict:
    await log_event(request,
                    response,
                    '/auth/logout',
                    {},
                    'Logout successful')  # Log
    request.app.state.r_session.end_session(request, response)
    return {'message': 'Logout successful', 'data': 0}
