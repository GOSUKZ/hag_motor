from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from app.iternal.models.user import RegUser, ChangeUser
from app.iternal.models.company import Company
from app.iternal.db.updatelog import CustomUpdate

from app.iternal.serializers.document import get_serialize_document, is_convertable

from app.iternal.models.document import UpdateDocument

router = APIRouter(
    prefix="/user",
    tags=["User"],
)


# Добавление компании
@router.post('/new_company/')
async def post_create_company(request: Request, response: Response, payload: Company = Body(...)):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

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


# Изменение записи о менеджере
@router.post('/change/')
async def post_manager(request: Request, response: Response, payload: ChangeUser = Body(...)):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

    try:
        session = request.app.state.r_session.protected_session(
            request, response, 99)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid session"}, status_code=401)

        company_key = [session.get("company_key")]
        admin_role = int(session.get('role'))
        admin_login = session.get('login')

        # Connect to DB connection
        database = request.app.state.database
        users_collection = database.get_collection("users")

        filter = {'login': admin_login}
        result = await users_collection.find_one(filter, {'company_key': 1})

        if (result is None):
            # Exception
            return JSONResponse(content={"message": 'Invalid login', "data": 0}, status_code=403)

        company_keys = result['company_key']

        payload = jsonable_encoder(payload)

        login = payload.get("login")

        payload = {k: v for k, v in payload.items() if v is not None}

        if payload.get("password") is not None:
            payload["password"] = request.app.state.r_session.generate_hashed_key(
                payload["password"])

        if payload.get("company_key") is not None:
            payload["company_key"] = [
                v for v in payload["company_key"] if v in company_keys]
            if len(payload["company_key"]) == 0:
                del payload["company_key"]

        update = {'$set': payload}
        filter = {'login': login, 'role': {'$lte': admin_role}}

        myLoggerUpdate = CustomUpdate(users_collection)
        result = await myLoggerUpdate.find_update(filter,
                                                  update,
                                                  admin_login,
                                                  '/user/change/')

        if (result is None):
            # Exception
            return JSONResponse(content={"message": "Document not found"}, status_code=404)

        # Success
        return JSONResponse(content={"message": "Successfully", "data": 0})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "change data error", "error": str(e)}, status_code=500)


# Регистрация менеджера
@router.post('/reg/{manager_type}')
async def post_manager(request: Request, response: Response, manager_type: str, payload: RegUser = Body(...)):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

    try:
        session = request.app.state.r_session.protected_session(
            request, response, 99)

        if manager_type not in ["inside", "outside"]:
            # Exception
            return JSONResponse(content={"message": "Manager type not supported [inside, outside]"}, status_code=403)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid session"}, status_code=401)

        admin_role = int(session.get('role'))

        # Connect to DB connection
        database = request.app.state.database
        users_collection = database.get_collection("users")

        now = datetime.utcnow()

        company_key = [session.get("company_key")]

        payload = jsonable_encoder(payload)

        login = payload.get('login')
        role = payload.get('role')

        if role > admin_role:
            role = admin_role

        filter = {"login": login}
        result = await users_collection.find_one(filter)

        if (result is not None):
            # Exception
            return JSONResponse(content={"message": 'Login already exists', "data": 0}, status_code=403)

        payload["role"] = role
        payload["company_key"] = company_key
        payload["created_at"] = now

        payload["password"] = request.app.state.r_session.generate_hashed_key(
            payload["password"])

        await users_collection.insert_one(payload)

        # Success
        return JSONResponse(content={"message": "Registration successfully", "data": 0}, status_code=201)
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Registration error", "error": str(e)}, status_code=500)
    

# Дерегистрация менеджера
@router.post('/del/{login}')
async def post_del_manager(request: Request, response: Response, login:str):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

    try:
        session = request.app.state.r_session.protected_session(
            request, response, 99)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid session"}, status_code=401)

        # Connect to DB connection
        database = request.app.state.database

        user_colection = database.get_collection("users")

        company_key = [session.get("company_key")]

        filter = {'login':login, 'company_key': {'$in': [company_key]}, 'role': {'$lt': 99}}
        result = await user_colection.find_one(filter)

        if (result is None):
            # Exception
            return JSONResponse(content={"message": 'Login not exists', "data": 0}, status_code=404)

        await user_colection.delete_one(filter)

        # Success
        return JSONResponse(content={"message": "Disintegration successfully", "data": 0}, status_code=200)
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Disintegration error", "error": str(e)}, status_code=500)


# Обнавление данных в записи
@router.post('/put/{document_id}/')
async def post_update_document(request: Request, response: Response, document_id: str, payload: UpdateDocument = Body(...)):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

    try:
        payload = jsonable_encoder(payload)

        session = request.app.state.r_session.protected_session(
            request, response, 99)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid session"}, status_code=401)

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

        update = {'$set': payload}

        myLoggerUpdate = CustomUpdate(data_collection)
        result = await myLoggerUpdate.find_update(filter,
                                                  update,
                                                  login,
                                                  f'user/put/{document_id}')

        if (result is None):
            # Exception
            return JSONResponse(content={"message": "Document not found"}, status_code=404)

        result = get_serialize_document(result)

        # Success
        return JSONResponse(content={"message": "Successfully", "data": [result]})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


# Создание записи
@router.post('/add/')
async def post_add_document(request: Request, response: Response, payload: UpdateDocument = Body(...)):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

    try:
        payload = jsonable_encoder(payload)

        session = request.app.state.r_session.protected_session(
            request, response, 99)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid session"}, status_code=401)

        company_key = session.get("company_key")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_collection = database.get_collection("data")

        # Convert str to datetime if exists reservation name date
        for key, value in payload.items():
            if (value and (key.find('date') >= 0)):
                if (len(value) <= len("2023-01-16 00:00:00")):
                    payload[key] = f"{value}.000000"
                payload[key] = datetime.strptime(
                    payload[key], "%Y-%m-%d %H:%M:%S.%f")

        result = await data_collection.insert_one(payload)
        ducument = await data_collection.find_one({'_id' : result.inserted_id})

        ducument = get_serialize_document(ducument)

        # Success
        return JSONResponse(content={"message": "Successfully", "data": [ducument]})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)


# Возврат по истории
@router.get('/log/{document_id}/{log_id}')
async def get_reverting_doc_history(request: Request, response: Response, document_id: str, log_id: str) -> dict:
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)
    
    try:
        session = request.app.state.r_session.protected_session(request,
                                                                response, 99)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid session"}, status_code=401)

        company_key = session.get("company_key")
        login = session.get("login")

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_collection = database.get_collection("data")

        filter = {'_id': ObjectId(document_id)}

        result = await data_collection.find_one(filter)

        log_collection: list = result.get("log_collection")

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

        if len(document) > 0:
            update = {'$set': jsonable_encoder(document['old_data'])}

            myLoggerUpdate = CustomUpdate(data_collection)

            # # result = await data_collection.find_one_and_update(filter, update)
            result = await myLoggerUpdate.find_update(filter,
                                                      update,
                                                      login,
                                                      f'/log/{document_id}/{log_id}/')

            if (result is None):
                # Exception
                return JSONResponse(content={"message": "Document not found"}, status_code=404)

            result = get_serialize_document(result)

        # Success
        return JSONResponse(content={"message": "Successfully", "data": result})

    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
