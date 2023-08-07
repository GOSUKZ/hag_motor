from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from io import BytesIO
from app.iternal.serializers.document import get_serialize_document, is_convertable
from pymongo import ASCENDING
from app.iternal.models.company import Company


from math import ceil


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


@router.get('/')
async def get_docs(request: Request, response: Response, page: int = 0, length: int = 10) -> dict:
    try:
        if ((page < 0) or (length < 0)):
            # Exception
            return JSONResponse(content={"message": "Page or length out of range"}, status_code=403)

        # Calculate the number of documents to skip
        skip = (page * length)

        # Calculate the number of documents to retrieve
        limit = (skip + length) - skip

        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        documents = []

        task = data_colection.count_documents({})

        cursor = data_colection.find().skip(skip).limit(limit)
        async for document in cursor:
            document = get_serialize_document(document)
            documents.append(document)

        documents_count = await task

        page_count = ceil(documents_count / length)

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count, "page_count": page_count}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


@router.get('/{filde_key}/')
async def get_docs_sorted(request: Request, response: Response, page: int = 0, length: int = 10, sorted: int = 1, fild_key: str = '_id') -> dict:
    try:
        if ((page < 0) or (length < 0)):
            # Exception
            return JSONResponse(content={"message": "Page or length out of range"}, status_code=403)

        if ((sorted > 1) or (sorted < -1) or (sorted == 0)):
            # Exception
            return JSONResponse(content={"message": "sorted out of range (1 - ASCENDING, -1 - DESCENDING)"}, status_code=403)

        # Calculate the number of documents to skip
        skip = (page * length)

        # Calculate the number of documents to retrieve
        limit = (skip + length) - skip

        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        documents = []

        task = data_colection.count_documents({})

        cursor = data_colection.find({}).sort(
            fild_key, sorted).skip(skip).limit(limit)
        async for document in cursor:
            documents.append(get_serialize_document(document))

        documents_count = await task

        page_count = ceil(documents_count / length)

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count, "page_count": page_count}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


@router.get('/{filde_key}/{fild_value}/')
async def get_docs_sorted_grouping(request: Request, response: Response, page: int = 0, length: int = 10, sorted: int = 1, fild_key: str = '_id', fild_value: str = None) -> dict:
    try:
        if ((page < 0) or (length < 0)):
            # Exception
            return JSONResponse(content={"message": "Page or length out of range"}, status_code=403)

        if ((sorted > 1) or (sorted < -1) or (sorted == 0)):
            # Exception
            return JSONResponse(content={"message": "sorted out of range (1 - ASCENDING, -1 - DESCENDING)"}, status_code=403)

        # Calculate the number of documents to skip
        skip = (page * length)

        # Calculate the number of documents to retrieve
        limit = (skip + length) - skip

        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        documents = []

        if (fild_key.find('date') >= 0):
            if (len(fild_value) <= len("2023-01-16 00:00:00")):
                print('fild_value: ', fild_value)
                fild_value = f"{fild_value}.000000"
            fild_value = datetime.strptime(fild_value, "%Y-%m-%d %H:%M:%S.%f")
        else:
            fild_value = is_convertable(fild_value)

        task = data_colection.count_documents({fild_key: fild_value})

        cursor = data_colection.find({fild_key: fild_value}).sort(fild_key,
                                                                  sorted).skip(skip).limit(limit)
        async for document in cursor:
            documents.append(get_serialize_document(document))

        documents_count = await task

        page_count = ceil(documents_count / length)

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count, "page_count": page_count}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
