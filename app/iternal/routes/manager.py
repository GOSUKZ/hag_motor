from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from app.iternal.models.user import RegUser
from app.iternal.models.document import UpdateDocument, UpdateDocumentManagerO, UpdateDocumentManagerI
from app.iternal.serializers.document import get_serialize_document, is_convertable
from app.iternal.db.updatelog import CustomUpdate
from app.iternal.log.event_log import log_event


router = APIRouter(
    prefix="/manager",
    tags=["Manager"],
)


# Обнавление данных в записи
@router.post('/{document_id}/')
async def post_update_document(request: Request, response: Response, document_id: str, payload: UpdateDocument = Body(...)):
    try:
        session = request.app.state.r_session.protected_session(request,
                                                                response, 1, 2)
        if len(session) > 0:
            payload = jsonable_encoder(
                UpdateDocumentManagerO.validate(payload))
            company_key = session.get("company_key")
            login = session.get("login")

            # Connect to DB connection
            database = request.app.state.mongodb[company_key]
            data_collection = database.get_collection("data")

            filter = {'_id': ObjectId(document_id)}

            # Convert str to datetime if exists reservation name date
            for key, value in payload.items():
                if (value and (key.find('date') >= 0)):
                    if (len(value) <= len("2023-01-16 00:00:00")):
                        payload[key] = f"{value}.000000"
                    payload[key] = datetime.strptime(
                        payload[key], "%Y-%m-%d %H:%M:%S.%f")

            payload = {k: v for k, v in payload.items() if v is not None and k not in ['_id',
                                                                                       'created_at',
                                                                                       'updated_at']}

            if len(payload) > 0:
                update = {'$set': payload}

                myLoggerUpdate = CustomUpdate(data_collection)
                result = await myLoggerUpdate.find_update(filter,
                                                          update,
                                                          login,
                                                          f'/manager/{document_id}/')

                if (result is None):
                    log_event(request,
                              response,
                              f'/manager/{document_id}/',
                              payload,
                              'Document not found')  # Log
                    # Exception
                    return JSONResponse(content={"message": "Document not found"}, status_code=404)

                result = get_serialize_document(result)

                log_event(request,
                          response,
                          f'/manager/{document_id}/',
                          {'payload': payload, 'result': [result]},
                          'Successfully')  # Log

                # Success
                return JSONResponse(content={"message": "Successfully", "data": [result]})
            log_event(request,
                      response,
                      f'/manager/{document_id}/',
                      {'payload': payload, 'result': []},
                      'Successfully')  # Log
            # Success
            return JSONResponse(content={"message": "Successfully", "data": 0})

        session = request.app.state.r_session.protected_session(request,
                                                                response, 0, 1)
        if len(session) > 0:
            payload = jsonable_encoder(
                UpdateDocumentManagerI.validate(payload))
            company_key = session.get("company_key")
            login = session.get("login")

            # Connect to DB connection
            database = request.app.state.mongodb[company_key]
            data_collection = database.get_collection("data")

            filter = {'_id': ObjectId(document_id)}

            # Convert str to datetime if exists reservation name date
            for key, value in payload.items():
                if (value and (key.find('date') >= 0)):
                    if (len(value) <= len("2023-01-16 00:00:00")):
                        payload[key] = f"{value}.000000"
                    payload[key] = datetime.strptime(
                        payload[key], "%Y-%m-%d %H:%M:%S.%f")

            payload = {k: v for k, v in payload.items() if v is not None and k not in ['_id',
                                                                                       'created_at',
                                                                                       'updated_at']}

            if len(payload) > 0:
                update = {'$set': payload}

                myLoggerUpdate = CustomUpdate(data_collection)

                # # result = await data_collection.find_one_and_update(filter, update)
                result = await myLoggerUpdate.find_update(filter,
                                                          update,
                                                          login,
                                                          f'/manager/{document_id}/')

                if (result is None):
                    log_event(request,
                              response,
                              f'/manager/{document_id}/',
                              payload,
                              'Document not found')  # Log
                    # Exception
                    return JSONResponse(content={"message": "Document not found"}, status_code=404)

                result = get_serialize_document(result)

                log_event(request,
                          response,
                          f'/manager/{document_id}/',
                          {'payload': payload, 'result': [result]},
                          'Successfully')  # Log

                # Success
                return JSONResponse(content={"message": "Successfully", "data": [result]})
            log_event(request,
                      response,
                      f'/manager/{document_id}/',
                      {'payload': payload, 'result': []},
                      'Successfully')  # Log
            # Success
            return JSONResponse(content={"message": "Successfully", "data": 0})

        log_event(request,
                  response,
                  f'/manager/{document_id}/',
                  payload,
                  'Unauthorized or invalid sesion')  # Log

        # Exception
        return JSONResponse(content={"message": "Unauthorized or invalid session"}, status_code=401)
    except Exception as e:

        log_event(request,
                  response,
                  f'/manager/{document_id}/',
                  {'payload': payload, "error": str(e)},
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


# Возврат по истории
@router.get('/log/{document_id}/{log_id}')
async def get_reverting_doc_history(request: Request, response: Response, document_id: str, log_id: str) -> dict:
    try:
        session = request.app.state.r_session.protected_session(request,
                                                                response, 1, 2)

        if len(session) > 0:

            company_key = session.get("company_key")
            login = session.get("login")

            # Connect to DB connection
            database = request.app.state.mongodb[company_key]
            data_collection = database.get_collection("data")

            filter = {'_id': ObjectId(document_id)}

            result = await data_collection.find_one(filter)

            log_collection: list = result.get("log_collection")
            if log_collection is None:
                log_event(request,
                          response,
                          f'/manager/log/{document_id}/{log_id}/',
                          {'document_id': document_id},
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

            if len(document) > 0:
                update = {'$set': jsonable_encoder(
                    UpdateDocumentManagerO.validate(document['old_data']))}

                myLoggerUpdate = CustomUpdate(data_collection)

                # # result = await data_collection.find_one_and_update(filter, update)
                result = await myLoggerUpdate.find_update(filter,
                                                          update,
                                                          login,
                                                          f'/log/{document_id}/{log_id}/')

                if (result is None):
                    log_event(request,
                              response,
                              f'/manager/log/{document_id}/{log_id}/',
                              {'document_id': document_id},
                              'Document not found')  # Log
                    # Exception
                    return JSONResponse(content={"message": "Document not found"}, status_code=404)

                result = get_serialize_document(result)

                log_event(request,
                          response,
                          f'/manager/log/{document_id}/{log_id}/',
                          {'log_collection': document},
                          'Successfully')  # Log

            # Success
            return JSONResponse(content={"message": "Successfully", "data": {'log_collection': document}})

        session = request.app.state.r_session.protected_session(request,
                                                                response, 0, 1)

        if len(session) > 0:

            company_key = session.get("company_key")
            login = session.get("login")

            # Connect to DB connection
            database = request.app.state.mongodb[company_key]
            data_collection = database.get_collection("data")

            filter = {'_id': ObjectId(document_id)}

            result = await data_collection.find_one(filter)

            log_collection: list = result.get("log_collection")
            if log_collection is None:
                log_event(request,
                          response,
                          f'/manager/log/{document_id}/{log_id}/',
                          {'document_id': document_id},
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

            if len(document) > 0:
                update = {'$set': jsonable_encoder(
                    UpdateDocumentManagerI.validate(document['old_data']))}

                myLoggerUpdate = CustomUpdate(data_collection)

                # # result = await data_collection.find_one_and_update(filter, update)
                result = await myLoggerUpdate.find_update(filter,
                                                          update,
                                                          login,
                                                          f'/log/{document_id}/{log_id}/')

                if (result is None):
                    log_event(request,
                              response,
                              f'/manager/log/{document_id}/{log_id}/',
                              {'document_id': document_id},
                              'Document not found')  # Log
                    # Exception
                    return JSONResponse(content={"message": "Document not found"}, status_code=404)

                result = get_serialize_document(result)

            log_event(request,
                      response,
                      f'/manager/log/{document_id}/{log_id}/',
                      result,
                      'Successfully')  # Log

            # Success
            return JSONResponse(content={"message": "Successfully", "data": result})

        log_event(request,
                  response,
                  f'/manager/log/{document_id}/{log_id}/',
                  {'document_id': document_id},
                  'Unauthorized or invalid sesion')  # Log

        # Exception
        return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)
    except Exception as e:
        log_event(request,
                  response,
                  f'/manager/{document_id}/',
                  {'document_id': document_id, "error": str(e)},
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
