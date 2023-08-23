from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from app.iternal.models.user import RegUser
from app.iternal.log.event_log import log_event

router = APIRouter(
    prefix="/god",
    tags=["God"],
)


# Регистрация новых админов
@router.post('/reg/')
async def post_registration(request: Request, response: Response, payload: RegUser = Body(...)):
    origin = request.headers['origin']
    response.headers.setdefault('Access-Control-Allow-Origin', origin)
    
    try:
        payload = jsonable_encoder(payload)

        session = request.app.state.r_session.protected_session(
            request, response, 1000)

        if len(session) <= 0:
            log_event(request,
                      response,
                      '/god/reg/',
                      payload,
                      'Unauthorized or invalid sesion')  # Log
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        admin_role = int(session.get('role'))

        now = datetime.utcnow()

        # Connect to DB connection
        database = request.app.state.database
        users_colection = database.get_collection("users")

        login = payload.get('login')
        role = payload.get('role')

        if role > admin_role:
            role = admin_role

        company_key = payload.get('company_key')

        filter = {"login": login}
        result = await users_colection.find_one(filter)

        if (result is not None):
            log_event(request,
                      response,
                      '/god/reg/',
                      payload,
                      'Login already exists')  # Log
            # Exception
            return JSONResponse(content={"message": 'Login already exists', "data": 0}, status_code=403)

        payload["role"] = role
        payload["company_key"] = company_key
        payload["created_at"] = now

        payload["password"] = request.app.state.r_session.generate_hashed_key(
            payload["password"])

        await users_colection.insert_one(payload)

        log_event(request,
                  response,
                  '/god/reg/',
                  payload,
                  'Registration successfully')  # Log

        # Success
        return JSONResponse(content={"message": "Registration successfully", "data": 0}, status_code=201)
    except Exception as e:
        log_event(request,
                  response,
                  '/god/reg/',
                  payload,
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
