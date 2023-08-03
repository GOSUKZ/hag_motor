from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from app.iternal.models.user import RegUser

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

# TODO: Группировка по полям и типизация данных
# TODO: Изменение !!!


@router.get('/')
async def get_docs(request: Request, response: Response, start: int = 0, end: int = 10) -> dict:
    try:
        if ((start > end) or (start < 0) or (end < 0)):
            # Exception
            return JSONResponse(content={"message": "Start or end out of range"}, status_code=403)

        # Calculate the number of documents to skip
        skip = start

        # Calculate the number of documents to retrieve
        limit = end - start + 1

        session = request.app.state.r_session.protected_session(
            request, response, 99)

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
            for key in document.keys():
                document[key] = str(document[key])
            documents.append(document)

        documents_count = await task

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


@router.get('/{filde_key}/')
async def get_docs_sorted(request: Request, response: Response, start: int = 0, end: int = 10, sorted: int = 1, fild_key: str = '_id') -> dict:
    try:
        if ((start > end) or (start < 0) or (end < 0)):
            # Exception
            return JSONResponse(content={"message": "Start or end out of range"}, status_code=403)

        if ((sorted > 1) or (sorted < -1) or (sorted == 0)):
            # Exception
            return JSONResponse(content={"message": "sorted out of range (1 - ASCENDING, -1 - DESCENDING)"}, status_code=403)

        # Calculate the number of documents to skip
        skip = start

        # Calculate the number of documents to retrieve
        limit = end - start + 1

        session = request.app.state.r_session.protected_session(
            request, response, 99)

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
            for key in document.keys():
                document[key] = str(document[key])
            documents.append(document)

        documents_count = await task

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


@router.get('/{filde_key}/{fild_value}/')
async def get_docs_sorted_grouping(request: Request, response: Response, start: int = 0, end: int = 10, sorted: int = 1, fild_key: str = '_id', fild_value: str = None) -> dict:
    try:
        if ((start > end) or (start < 0) or (end < 0)):
            # Exception
            return JSONResponse(content={"message": "Start or end out of range"}, status_code=403)

        if ((sorted > 1) or (sorted < -1) or (sorted == 0)):
            # Exception
            return JSONResponse(content={"message": "sorted out of range (1 - ASCENDING, -1 - DESCENDING)"}, status_code=403)

        # Calculate the number of documents to skip
        skip = start

        # Calculate the number of documents to retrieve
        limit = end - start + 1

        session = request.app.state.r_session.protected_session(
            request, response, 99)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        documents = []

        task = data_colection.count_documents({})

        cursor = data_colection.find({fild_key: fild_value}).sort(
            fild_key, sorted).skip(skip).limit(limit)
        async for document in cursor:
            for key in document.keys():
                document[key] = str(document[key])
            documents.append(document)

        documents_count = await task

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


@router.post('/{document_id}/')
async def post_update(request: Request, response: Response, document_id: str, payload: dict = Body(...)) -> dict:
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

        filter = {'_id': ObjectId(document_id)}
        update = {'$set': payload}
        result = await data_colection.find_one_and_update(filter, update)

        if (result is None):
            # Exception
            return JSONResponse(content={"message": "Document not found"}, status_code=404)

        for key in result.keys():
            result[key] = str(result[key])

        # Success
        return JSONResponse(content={"message": "Successfully", "data": [result]})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
