from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from io import BytesIO
from app.iternal.serializers.document import get_serialize_document
from pymongo import ASCENDING
from app.iternal.models.company import Company


router = APIRouter(
    prefix="/company",
    tags=["Company"]
)


@router.post('/new/')
async def update_company(request: Request, response: Response, payload: Company = Body(...)):
    try:
        payload = jsonable_encoder(payload)

        session = request.app.state.r_session.protected_session(
            request, response, -1, 0)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        login = session.get('login')

        # Connect to DB connection
        database = request.app.state.database
        control_colection = database.get_collection("control_data")
        users_colection = database.get_collection("users")

        company_key: str = payload.get('company_key')

        company_key.replace(' ', '_')

        special_characters = "!@#$%^&*()[]{}|;:,.<>?/~`"
        for char in special_characters:
            if company_key.find(char) != -1:
                # Exception
                return JSONResponse(content={"message": f'Company name should not contain {special_characters}', "data": 0}, status_code=402)

        upload_at = payload.get('upload_at')

        filter = {'company_key': company_key}

        result = await control_colection.find_one(filter)

        if (result is not None):
            # Exception
            return JSONResponse(content={"message": 'Company already exists', "data": 0}, status_code=403)

        filter = {"login": login}
        result = await users_colection.find_one(filter, {'company_key': 1})

        company_keys = result.get('company_key')
        company_keys.append(company_key)
        update = {'$set': {'company_key': company_keys}}

        await users_colection.update_one(filter, update)

        insert = {
            "company_key": company_key,
            "upload_at": upload_at
        }

        await control_colection.insert_one(insert)

        # Success
        return JSONResponse(content={"message": "Create company successfully", "data": company_key}, status_code=201)
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
