from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from app.iternal.models.user import RegUser
from app.iternal.db.updatelog import CustomUpdate

from app.iternal.serializers.document import get_serialize_document, is_convertable

from app.iternal.models.document import UpdateDocument

router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.post('/{document_id}/')
async def post_update(request: Request, response: Response, document_id: str, payload: UpdateDocument = Body(...)) -> dict:
    try:
        payload = jsonable_encoder(payload)

        session = request.app.state.r_session.protected_session(
            request, response, 99)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        myLoggerUpdate = CustomUpdate(data_colection)

        filter = {'_id': ObjectId(document_id)}

        # Convert str to datetime if exists reservation name date
        for key, value in payload.items():
            if (value and (key.find('date') >= 0)):
                if (len(value) <= len("2023-01-16 00:00:00")):
                    payload[key] = f"{value}.000000"
                payload[key] = datetime.strptime(
                    payload[key], "%Y-%m-%d %H:%M:%S.%f")

        payload = {k: v for k, v in payload.items() if v is not None and k in [
            '_id', 'created_at', 'updated_at']}

        update = {'$set': payload}

        # result = await data_colection.find_one_and_update(filter, update)
        result = await myLoggerUpdate.find_update(filter, update)

        if (result is None):
            # Exception
            return JSONResponse(content={"message": "Document not found"}, status_code=404)

        result = get_serialize_document(result)

        # Success
        return JSONResponse(content={"message": "Successfully", "data": [result]})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


@router.post('/add_manager/{manager_type}')
async def post_manager(request: Request, response: Response, manager_type: str, payload: RegUser = Body(...)):
    try:
        session = request.app.state.r_session.protected_session(
            request, response, 99)

        if manager_type not in ["inside", "outside"]:
            # Exception
            return JSONResponse(content={"message": "Manager type not supported [inside, outside]"}, status_code=403)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        # Connect to DB connection
        database = request.app.state.database
        users_colection = database.get_collection("users")

        now = datetime.utcnow()

        company_key = [session.get("company_key")]

        payload = jsonable_encoder(payload)

        login = payload.get('login')
        role = payload.get('role')

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
