from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from io import BytesIO
from app.iternal.serializers.document import get_serialize_document, is_convertable
from pymongo import ASCENDING


from math import ceil


router = APIRouter(
    prefix="/company",
    tags=["Company"]
)


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
