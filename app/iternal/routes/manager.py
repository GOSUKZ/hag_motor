from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from app.iternal.models.user import RegUser
from app.iternal.models.document import UpdateDocument, UpdateDocumentManagerO, UpdateDocumentManagerI
from app.iternal.serializers.document import get_serialize_document, is_convertable
from app.iternal.db.updatelog import CustomUpdate


router = APIRouter(
    prefix="/manager",
    tags=["Manager"],
)


@router.post('/{document_id}/')
async def post_update__document(request: Request, response: Response, document_id: str, payload: UpdateDocument = Body(...)):
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

                # # result = await data_collection.find_one_and_update(filter, update)
                result = await myLoggerUpdate.find_update(filter,
                                                          update,
                                                          login,
                                                          f'/manager/{document_id}/')

                if (result is None):
                    # Exception
                    return JSONResponse(content={"message": "Document not found"}, status_code=404)

                result = get_serialize_document(result)

                # Success
                return JSONResponse(content={"message": "Successfully", "data": [result]})
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
                    # Exception
                    return JSONResponse(content={"message": "Document not found"}, status_code=404)

                result = get_serialize_document(result)

                # Success
                return JSONResponse(content={"message": "Successfully", "data": [result]})
            # Success
            return JSONResponse(content={"message": "Successfully", "data": 0})

        # Exception
        return JSONResponse(content={"message": "Unauthorized or invalid session"}, status_code=401)
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
