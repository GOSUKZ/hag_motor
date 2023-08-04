from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from app.iternal.models.user import RegUser

router = APIRouter(
    prefix="/god",
    tags=["God"],
)


@router.post('/reg/')
async def post_registration(request: Request, response: Response, payload: RegUser = Body(...)):
    try:
        session = request.app.state.r_session.protected_session(
            request, response, 1000)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        admin_role = int(session.get('role'))

        payload = jsonable_encoder(payload)

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
            # Exception
            return JSONResponse(content={"message": 'Login already exists', "data": 0}, status_code=403)

        payload["role"] = role
        payload["company_key"] = company_key
        payload["created_at"] = now

        payload["password"] = request.app.state.r_session.generate_hashed_key(
            payload["password"])

        await users_colection.insert_one(payload)

        # Success
        return JSONResponse(content={"message": "Registration successfully", "data": 0}, status_code=201)
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
