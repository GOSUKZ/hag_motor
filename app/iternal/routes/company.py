from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from app.iternal.serializers.document import get_serialize_document, is_convertable
from app.iternal.log.event_log import log_event


from math import ceil


router = APIRouter(
    prefix="/company",
    tags=["Company"]
)


# Получение документов
@router.get('/find/')
async def get_docs(request: Request, response: Response, page: int = 0, length: int = 10) -> dict:
    try:
        if ((page < 0) or (length < 0)):
            log_event(request,
                      response,
                      '/company/',
                      {'page': page, 'length': length},
                      'Page or length out of range')  # Log
            # Exception
            return JSONResponse(content={"message": "Page or length out of range"}, status_code=403)

        # Calculate the number of documents to skip
        skip = (page * length)

        # Calculate the number of documents to retrieve
        limit = (skip + length) - skip

        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            log_event(request,
                      response,
                      '/company/',
                      {'page': page, 'length': length},
                      'Unauthorized or invalid sesion')  # Log
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

        log_event(request,
                  response,
                  '/company/',
                  {'page': page, 'length': length, "documents": documents,
                   "documents_count": documents_count, "page_count": page_count},
                  'Successfully')  # Log

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count, "page_count": page_count}})
    except Exception as e:
        log_event(request,
                  response,
                  '/company/',
                  {'page': page, 'length': length, "error": str(e)},
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


# Сортировка и получение документов
@router.get('/find/{sort_key}/')
async def get_docs_sorted(request: Request, response: Response, page: int = 0, length: int = 10, sorted: int = 1, sort_key: str = '_id') -> dict:
    try:
        if ((page < 0) or (length < 0)):
            log_event(request,
                      response,
                      f'/company/{sort_key}/',
                      {'page': page, 'length': length, 'sorted': sorted},
                      'Page or length out of range')  # Log
            # Exception
            return JSONResponse(content={"message": "Page or length out of range"}, status_code=403)

        if ((sorted > 1) or (sorted < -1) or (sorted == 0)):
            log_event(request,
                      response,
                      f'/company/{sort_key}/',
                      {'page': page, 'length': length, 'sorted': sorted},
                      'sorted out of range (1 - ASCENDING, -1 - DESCENDING)')  # Log
            # Exception
            return JSONResponse(content={"message": "sorted out of range (1 - ASCENDING, -1 - DESCENDING)"}, status_code=403)

        # Calculate the number of documents to skip
        skip = (page * length)

        # Calculate the number of documents to retrieve
        limit = (skip + length) - skip

        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            log_event(request,
                      response,
                      '/company/',
                      {'page': page, 'length': length, 'sorted': sorted},
                      'Unauthorized or invalid sesion')  # Log
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

        log_event(request,
                  response,
                  f'/company/{sort_key}/',
                  {'page': page, 'length': length, 'sorted': sorted, "documents": documents,
                   "documents_count": documents_count, "page_count": page_count},
                  'Successfully')  # Log

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count, "page_count": page_count}})
    except Exception as e:
        log_event(request,
                  response,
                  f'/company/{sort_key}/',
                  {'page': page, 'length': length,
                   'sorted': sorted, "error": str(e)},
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


# Сортировка, группировка и получение документов
@router.get('/find/{sort_key}/{fild_key}/{fild_value}/')
async def get_docs_sorted_grouping(request: Request, response: Response, page: int = 0, length: int = 10, sorted: int = 1, sort_key: str = '_id', fild_key: str = 'weight', fild_value: str = '10.5') -> dict:
    try:
        if ((page < 0) or (length < 0)):
            log_event(request,
                      response,
                      f'/company/{sort_key}/{fild_key}/{fild_value}/',
                      {'page': page, 'length': length, 'sorted': sorted},
                      'Page or length out of range')  # Log
            # Exception
            return JSONResponse(content={"message": "Page or length out of range"}, status_code=403)

        if ((sorted > 1) or (sorted < -1) or (sorted == 0)):
            log_event(request,
                      response,
                      f'/company/{sort_key}/{fild_key}/{fild_value}/',
                      {'page': page, 'length': length, 'sorted': sorted},
                      'sorted out of range (1 - ASCENDING, -1 - DESCENDING)')  # Log
            # Exception
            return JSONResponse(content={"message": "sorted out of range (1 - ASCENDING, -1 - DESCENDING)"}, status_code=403)

        # Calculate the number of documents to skip
        skip = (page * length)

        # Calculate the number of documents to retrieve
        limit = (skip + length) - skip

        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            log_event(request,
                      response,
                      f'/company/{sort_key}/{fild_key}/{fild_value}/',
                      {'page': page, 'length': length, 'sorted': sorted},
                      'Unauthorized or invalid sesion')  # Log
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
        print('fild_key: fild_value: ', {fild_key: fild_value})

        cursor = data_colection.find({fild_key: fild_value}).sort(sort_key,
                                                                  sorted).skip(skip).limit(limit)
        async for document in cursor:
            documents.append(get_serialize_document(document))

        documents_count = await task

        page_count = ceil(documents_count / length)

        log_event(request,
                  response,
                  f'/company/{sort_key}/{fild_key}/{fild_value}/',
                  {'page': page, 'length': length, 'sorted': sorted, "documents": documents,
                   "documents_count": documents_count, "page_count": page_count},
                  'Successfully')  # Log

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count, "page_count": page_count}})
    except Exception as e:
        log_event(request,
                  response,
                  f'/company/{sort_key}/{fild_key}/{fild_value}/',
                  {'page': page, 'length': length, 'sorted': sorted, 'sort_key': sort_key,
                   'fild_key': fild_key, 'fild_value': fild_value, "error": str(e)},
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


# Получение истории документа
@router.get('/log/{document_id}/')
async def get_doc_history(request: Request, response: Response, document_id: str) -> dict:
    try:
        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            log_event(request,
                      response,
                      f'/company/log/{document_id}/',
                      {'document_id': document_id},
                      'Unauthorized or invalid sesion')  # Log
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
            log_event(request,
                      response,
                      f'/company/log/{document_id}/',
                      {'document_id': document_id},
                      'Log_collection is null')  # Log
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

        log_event(request,
                  response,
                  f'/company/log/{document_id}/',
                  {'document_id': document_id},
                  'Successfully')  # Log

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {'log_collection': log_collection, 'log_count': log_count}})
    except Exception as e:
        log_event(request,
                  response,
                  f'/company/log/{document_id}/',
                  {'document_id': document_id, "error": str(e)},
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


# Получение истории документа
@router.get('/log/{document_id}/{log_id}/')
async def get_doc_history(request: Request, response: Response, document_id: str, log_id: str) -> dict:
    try:
        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            log_event(request,
                      response,
                      f'/company/log/{document_id}/{log_id}',
                      {'document_id': document_id, 'log_id': log_id},
                      'Unauthorized or invalid sesion')  # Log
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        filter = {'_id': ObjectId(document_id)}

        result = await data_colection.find_one(filter)

        log_collection: list = result.get("log_collection")
        if log_collection is None:
            log_event(request,
                      response,
                      f'/company/log/{document_id}/{log_id}',
                      {'document_id': document_id, 'log_id': log_id},
                      'Log_collection is null')  # Log
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

        log_event(request,
                  response,
                  f'/company/log/{document_id}/{log_id}/',
                  {'document_id': document_id, 'log_collection': document},
                  'Successfully')  # Log

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {'log_collection': document}})
    except Exception as e:
        log_event(request,
                  response,
                  f'/company/log/{document_id}/{log_id}/',
                  {'document_id': document_id,
                      'log_id': log_id, "error": str(e)},
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


# Список всех сотрудников
@router.get('/manager/')
async def get_manager_list(request: Request, response: Response):
    try:
        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            log_event(request,
                      response,
                      '/company/manager',
                      {},
                      'Unauthorized or invalid sesion')  # Log
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.database
        user_colection = database.get_collection("users")

        filter = {'company_key': {'$in': [company_key]}, 'role': {'$lt': 1000}}

        documents = []

        cursor = user_colection.find(
            filter, {'login': 1, 'role': 1, 'created_at': 1, 'session_id': 1})
        async for document in cursor:
            documents.append(get_serialize_document(document))

        documents_count = len(documents)

        log_event(request,
                  response,
                  f'/company/manager',
                  {"documents": documents, "documents_count": documents_count},
                  'Successfully')  # Log

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"managers": documents, "managers_count": documents_count}})
    except Exception as e:
        log_event(request,
                  response,
                  f'/company/manager',
                  filter,
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


# Получить сводную таблицу для всех клиентов
@router.get('/pivot/')
async def get_pivot_all(request: Request, response: Response):
    try:
        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            log_event(request,
                      response,
                      '/company/pivot',
                      {},
                      'Unauthorized or invalid sesion')  # Log
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")
        pipeline = [
            {
                "$group": {
                    "_id": "$code",
                    "totalValue": {"$sum": "$total"}
                }
            }
        ]

        documents = []

        # Perform the aggregation
        async for result in data_colection.aggregate(pipeline):
            documents.append(result)

        documents_count = len(documents)

        log_event(request,
                  response,
                  f'/company/pivot',
                  {"documents": documents, "documents_count": documents_count},
                  'Successfully')  # Log

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count}})
    except Exception as e:
        log_event(request,
                  response,
                  f'/company/pivot',
                  pipeline,
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


# Получить сводную таблицу для всех клиентов
@router.get('/pivot/{code}')
async def get_pivot_all(request: Request, response: Response, code: str):
    try:
        session = request.app.state.r_session.protected_session(
            request, response, 0)

        if len(session) <= 0:
            log_event(request,
                      response,
                      '/company/pivot',
                      {},
                      'Unauthorized or invalid sesion')  # Log
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        # Define the aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "code": code  # Only include documents with category
                }
            },
            {
                "$group": {
                    "_id": "$code",
                    "totalValue": {"$sum": "$total"}
                }
            }
        ]

        documents = []

        # Perform the aggregation
        async for result in data_colection.aggregate(pipeline):
            documents.append(result)

        documents_count = len(documents)

        log_event(request,
                  response,
                  f'/company/pivot',
                  {"documents": documents, "documents_count": documents_count},
                  'Successfully')  # Log

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count}})
    except Exception as e:
        log_event(request,
                  response,
                  f'/company/pivot',
                  pipeline,
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
