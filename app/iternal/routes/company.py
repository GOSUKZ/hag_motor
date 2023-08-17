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


@router.get('/{sort_key}/')
async def get_docs_sorted(request: Request, response: Response, page: int = 0, length: int = 10, sorted: int = 1, sort_key: str = '_id') -> dict:
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

        cursor = data_colection.find({}).sort(sort_key,
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


@router.get('/{sort_key}/{filde_key}/{fild_value}/')
async def get_docs_sorted_grouping(request: Request, response: Response, page: int = 0, length: int = 10, sorted: int = 1, sort_key: str = '_id', fild_key: str = 'weight', fild_value: str = '10.5') -> dict:
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

        cursor = data_colection.find({fild_key: fild_value}).sort(sort_key,
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


@router.get('/log/{document_id}/')
async def get_doc_history(request: Request, response: Response, document_id: str) -> dict:
    try:
        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        filter = {'_id': ObjectId(document_id)}

        result = await data_colection.find_one(filter)

        log_collection = result.get("log_collection")
        if log_collection is None:
            # Exception
            return JSONResponse(content={"message": "Log_collection is null"}, status_code=400)
        

        for log in log_collection:
            old_data = get_serialize_document(log['old_data'])
            new_data = get_serialize_document(log['new_data'])

            log['new_data'] = new_data
            log['old_data'] = old_data

            log['created_at'] = str(log['created_at'])
            log['log_id'] = str(log['log_id'])

            log = jsonable_encoder(log)

        log_count = len(log_collection)

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {'log_collection': log_collection, 'log_count': log_count}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
    

@router.get('/log/{document_id}/{log_id}')
async def get_doc_history(request: Request, response: Response, document_id: str, log_id: str) -> dict:
    try:
        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        filter = {'_id': ObjectId(document_id)}

        result = await data_colection.find_one(filter)

        log_collection : list = result.get("log_collection")
        if log_collection is None:
            # Exception
            return JSONResponse(content={"message": "Log_collection is null"}, status_code=400)
        

        document = dict()     

        for log in log_collection:
            if (log['log_id'] == ObjectId(log_id)):
                old_data = get_serialize_document(log['old_data'])
                new_data = get_serialize_document(log['new_data'])

                log['new_data'] = new_data
                log['old_data'] = old_data

                log['created_at'] = str(log['created_at'])
                log['log_id'] = str(log['log_id'])

                document = jsonable_encoder(log)

                break

        




        # Success
        return JSONResponse(content={"message": "Successfully", "data": {'log_collection': document}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
    

