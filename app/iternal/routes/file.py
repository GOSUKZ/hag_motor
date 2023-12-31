from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from io import BytesIO
from app.iternal.serializers.document import get_serialize_document
from pymongo import ASCENDING
from app.iternal.db.updatelog import CustomUpdate
from app.iternal.models.document import UpdateDocument, UpdateDocumentManagerO, UpdateDocumentManagerI
from app.iternal.log.event_log import log_event

import pandas as pd

import asyncio

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

# TODO: Выгрузка ограничить


# Выгрузка файла
@router.post("/upload/")
async def upload_file(request: Request, response: Response, file: UploadFile = File(...)):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

    session = request.app.state.r_session.protected_session(
        request, response, 1)

    if len(session) <= 0:
        log_event(request,
                  response,
                  '/files/upload/',
                  {},
                  'Unauthorized or invalid sesion')  # Log
        # Exception
        return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

    company_key = session.get("company_key")
    role = int(session.get("role"))

    # Get now data
    now = datetime.utcnow()

    action_extended_id = ObjectId()

    # Read the Excel file using Pandas from the file's content
    content = await file.read()

    control_data = {}

    # Get the control_data
    try:
        # Assuming the file is in .xlsx format.
        control_df = pd.read_excel(
            BytesIO(content), engine="openpyxl", sheet_name="__control_data")

        # Fill the empty with zero values ( df.fillna(0) )
        control_df_filled = control_df.where(pd.notnull(control_df), None)

        # Convert to list
        control_data_list = control_df_filled.to_numpy().tolist()

        # Check if the list
        if len(control_data_list) > 0:

            # limit the reading area
            control_data_list_keys = control_data_list[3:4]
            control_data_list = control_data_list[4:5]

            # Collect data from control_data sheet
            for i in range(0, len(control_data_list_keys)):
                key = control_data_list_keys[i][0]
                data = control_data_list[i][0]
                control_data[key] = data
    except Exception as e:
        print({"message": str(e)})

    # Get the data
    try:
        # Assuming the file is in .xlsx format.
        df = pd.read_excel(BytesIO(content), engine="openpyxl")

        # Fill the empty with zero values ( df.fillna(0) )
        df_filled = df.where(pd.notnull(df), None)
        list_data = df_filled.to_numpy().tolist()  # Convert to list

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        upload_colection = database.get_collection("upload")
        data_colection = database.get_collection("data")

        # Check if the control_data exists
        if (len(control_data) > 0):
            asyncio.create_task(upload_generated_file(data_colection,
                                                      upload_colection,
                                                      now,
                                                      action_extended_id,
                                                      control_data,
                                                      list_data,
                                                      role))
        else:
            asyncio.create_task(upload_external_file(upload_colection,
                                                     now,
                                                     action_extended_id,
                                                     list_data,
                                                     role))

        log_event(request,
                  response,
                  '/files/upload/',
                  {'action_extended_id': str(action_extended_id)},
                  'File pre-upload successfully')  # Log
        # Success
        return JSONResponse(content={"message": "File pre-upload successfully", "data": str(action_extended_id)}, status_code=202)
    except Exception as e:
        log_event(request,
                  response,
                  '/files/upload/',
                  {"error": str(e)},
                  'Upload file error')  # Log
        # Exception
        return JSONResponse(content={"message": "Upload file error", "error": str(e)}, status_code=422)


# Подтверждение выгрузки
@router.post("/confirm/{id}")
async def confirm_file(request: Request, response: Response, id: str):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

    session = request.app.state.r_session.protected_session(
        request, response, 1)

    if len(session) <= 0:
        log_event(request,
                  response,
                  f'/files/confirm/{id}',
                  {'action_id': str(id)},
                  'Unauthorized or invalid sesion')  # Log
        # Exception
        return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

    company_key = session.get("company_key")
    login = session.get("login")

    try:
        database = request.app.state.mongodb[company_key]
        upload_colection = database.get_collection("upload")
        control_colection = request.app.state.database.get_collection(
            "control_data")

        filter = {'action_id': ObjectId(id)}

        result = await upload_colection.find_one(filter)

        # Check if id exists
        if (result is not None):

            if (result.get('status') != 'ok'):
                log_event(request,
                          response,
                          f'/files/confirm/{id}',
                          {"action_id": str(id),
                           "status": result.get('status')},
                          'File status not ok')  # Log
                # Success
                return JSONResponse(content={"message": "File status not ok", "data": {"action_id": str(id), "status": result.get('status')}}, status_code=400)

            data_for_db = result.get('data')
            control_data = result.get('control')

            data_colection = database.get_collection("data")

            # Check if control_data exists
            if (control_data):
                # Create control timestamp
                upload_at = 0
                export_at = control_data.get("export_at")

                filter = {"company_key": company_key}
                result = await control_colection.find_one(filter)

                # Check if upload_at exists
                if (result is None):
                    insert = {
                        "company_key": company_key,
                        "upload_at": upload_at
                    }

                    await control_colection.insert_one(insert)
                elif (result.get("upload_at") is None):
                    update = {"$set": {"upload_at": upload_at}}

                    await control_colection.update_one(filter, update)
                else:
                    upload_at = result.get("upload_at")

                # Check if conflict
                if (upload_at > export_at):
                    filter = {'action_id': ObjectId(id)}
                    update = {'$set': {"status": "conflict"}}
                    await upload_colection.update_one(filter, update)

                    log_event(request,
                              response,
                              f'/files/confirm/{id}',
                              {"action_id": str(id)},
                              'File confirm conflict')  # Log

                    # Success
                    return JSONResponse(content={"message": "File confirm conflict", "data": str(id)}, status_code=409)

                # List for asincso tasks
                tasks = []

                insert_data = []
                for line in data_for_db:

                    tasks.append(asyncio.create_task(confirm_file_coroutine(line,
                                                                            data_colection,
                                                                            insert_data,
                                                                            login,
                                                                            f'/files/confirm/{id}')))
                # Await all tasks
                await asyncio.gather(*tasks)

                filter = {"company_key": company_key}
                update = {"$set": {"upload_at": export_at}}
                task = control_colection.update_one(filter, update)

                # Check if changes exist
                if (len(insert_data) > 0):
                    await data_colection.insert_many(insert_data)
                await task
            else:
                await data_colection.insert_many(data_for_db)

        filter = {'action_id': ObjectId(id), "status": "ok"}
        result = await upload_colection.delete_one(filter)

        log_event(request,
                  response,
                  f'/files/confirm/{id}',
                  {"action_id": str(id)},
                  'File confirm successfully')  # Log

        # Success
        return JSONResponse(content={"message": "File confirm successfully"}, status_code=202)
    except Exception as e:
        log_event(request,
                  response,
                  f'/files/confirm/{id}',
                  {"action_id": str(id)},
                  'Get documents error')  # Log
        # Exception
        return JSONResponse(content={"message":"File confirm error", 'error': str(e)}, status_code=500)


# Скачивание файла
@router.get("/export_excel/")
async def export_excel(request: Request, response: Response):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

    session = request.app.state.r_session.protected_session(
        request, response, 1)

    if len(session) <= 0:
        # Exception
        return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

    company_key = session.get("company_key")

    # Get now data
    now = datetime.utcnow()

    try:
        database = request.app.state.mongodb[company_key]
        upload_colection = database.get_collection("upload")
        upload_colection.create_index([("action_id", ASCENDING)], unique=True)
        upload_colection.create_index("created_at", expireAfterSeconds=5*60)
    except Exception as e:
        pass

    try:
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        result = await data_colection.find({}).to_list(None)

        # total = {'count': 0, 'weight': 0, 'space': 0, 'density': 0, 'packaging': 0,
        #          'delivery': 0, 'other': 0, 'insurance': 0, 'unit_price': 0, 'total': 0}

        total = {}

        for i in range(0, len(result)):
            if result[i].get("created_at"):
                del result[i]["created_at"]
            if result[i].get("updated_at"):
                del result[i]["updated_at"]
            if result[i].get("log_collection") is not None:
                del result[i]["log_collection"]
            result[i]["_"] = ""

            buf_result = get_serialize_document(result[i])

            for key in buf_result.keys():
                if ((buf_result[key] is not None) and (type(buf_result[key]) != str)):
                    if total.get(key):
                        total[key] = sum([total[key], buf_result[key]])
                    else:
                        total[key] = buf_result[key]

        result.append(total)

        # Create a DataFrame from the data
        df = pd.DataFrame(result)
        df2 = pd.DataFrame({"export_at": [now.timestamp()]})

        # Create an Excel writer using BytesIO
        excel_writer = BytesIO()

        # Write the DataFrames to separate sheets in the Excel file
        with pd.ExcelWriter(excel_writer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="data",
                        index=False, startrow=4, header="data")
            df2.to_excel(writer, sheet_name="__control_data",
                         index=False, startrow=4, header="__control_data")

        # Set the file's name
        file_name = f"exported_data_{company_key}.xlsx"
        # Prepare the response headers
        response_headers = {
            "Content-Disposition": f"attachment; filename={file_name}",
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        # Get the bytes content of the Excel file
        excel_content = excel_writer.getvalue()
        # Close the Excel writer
        excel_writer.close()

        # Return the Excel file as a response
        return Response(content=excel_content, headers=response_headers)
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": str(e)}, status_code=500)


# Работа с конфликтами ------------------------
@router.get("/conflict/{conflict_id}")
async def get_all_conflict_id(request: Request, response: Response, conflict_id: str):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

    session = request.app.state.r_session.protected_session(
        request, response, 1)

    if len(session) <= 0:
        # Exception
        return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

    company_key = session.get("company_key")

    now = datetime.utcnow()

    try:
        database = request.app.state.mongodb[company_key]
        upload_colection = database.get_collection("upload")

        filter = {'action_id': ObjectId(conflict_id), "status": "conflict"}
        result = await upload_colection.find_one(filter, {'data': 1})

        if (result is None):
            # Exception
            return JSONResponse(content={"message": "File not found"}, status_code=404)

        data_db = result.get("data")

        data_insert = []
        data_update = []
        conflict_ids = []
        action_id = 0
        for data in data_db:
            id = data.get("_id")
            if (id is not None):
                data_update.append(data)
            else:
                data_insert.append(data)

        if len(data_insert) > 0:
            if len(data_update) > 0:
                update = {'$set': {'data': data_update}}
                task = upload_colection.update_one(filter, update)
            else:
                task = upload_colection.delete_one(filter)

            action_id = ObjectId()
            insert = {
                'action_id': action_id,
                'data': data_insert,
                'created_at': now,
                'status': 'ok'
            }
            action_id = str(action_id)
            await upload_colection.insert_one(insert)
            await task

        for data in data_update:
            id = data.get("_id")
            conflict_ids.append(str(id))

        # Success
        return JSONResponse(content={"message": "File conflict objects", "data": {"new_action_id": action_id, "old_action_id": conflict_id, "conflict_id": conflict_ids}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": str(e)}, status_code=500)


@router.get("/conflict/{id}/{object_id}")
async def get_conflict_by_id(request: Request, response: Response, id: str, object_id: str):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)

    session = request.app.state.r_session.protected_session(
        request, response, 1)

    if len(session) <= 0:
        # Exception
        return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

    company_key = session.get("company_key")

    try:
        database = request.app.state.mongodb[company_key]
        upload_colection = database.get_collection("upload")
        data_colection = database.get_collection("data")

        filter = {'action_id': ObjectId(id), "status": "conflict"}
        result = await upload_colection.find_one(filter)

        if (result is None):
            # Exception
            return JSONResponse(content={"message": "File not found"}, status_code=404)

        data_buf = result.get("data")
        new_data = []
        for data in data_buf:
            if (data['_id'] == object_id):
                del data["updated_at"]
                new_data.append(get_serialize_document(data))

        curren_data = []

        for data in new_data:
            filter = {'_id': ObjectId(data.get("_id"))}
            result = await data_colection.find_one(filter)
            if result is not None:
                del result["updated_at"]
                del result["created_at"]
                curren_data.append(get_serialize_document(result))

        # Success
        return JSONResponse(content={"message": "File conflict objects", "data": {"new_data": new_data, "curren_data": curren_data}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": str(e)}, status_code=500)


@router.get("/conflict/{id}/{object_id}/{action}")
async def resolved_conflict(request: Request, response: Response, id: str, object_id: str, action: str):
    origin = request.headers.get('origin')
    if (origin) :
        response.headers.setdefault('Access-Control-Allow-Origin', origin)
    
    session = request.app.state.r_session.protected_session(
        request, response, 1)

    if len(session) <= 0:
        # Exception
        return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

    company_key = session.get("company_key")

    try:
        if action not in ["new", "current"]:
            # Exception
            return JSONResponse(content={"message": "action not supported [new, current]"}, status_code=403)

        database = request.app.state.mongodb[company_key]
        upload_colection = database.get_collection("upload")
        data_colection = database.get_collection("data")

        filter = {'action_id': ObjectId(id), "status": "conflict"}
        result = await upload_colection.find_one(filter)

        if (result is None):
            # Exception
            return JSONResponse(content={"message": "File not found"}, status_code=404)

        data_buf = result.get("data")
        new_data = []

        if action == "new":

            i = 0
            while i < len(data_buf):
                if (data_buf[i]['_id'] == object_id):
                    new_data.append(data_buf[i])
                    data_buf = list(data_buf[:i] + data_buf[i+1:])
                i = i + 1

            for data in new_data:
                filter = {'_id': ObjectId(data.get("_id"))}
                del data['_id']
                update = {'$set': data}
                result = await data_colection.find_one_and_update(filter, update)

        if action == "current":
            i = 0
            while i < len(data_buf):
                if (data_buf[i]['_id'] == object_id):
                    data_buf = list(data_buf[:i] + data_buf[i+1:])
                i = i + 1

        if len(data_buf) > 0:
            filter = {'action_id': ObjectId(id), "status": "conflict"}
            update = {'$set': {"data": data_buf}}
            result = await upload_colection.find_one_and_update(filter, update)
        else:
            filter = {'action_id': ObjectId(id), "status": "conflict"}
            result = await upload_colection.delete_one(filter)

        # Success
        return JSONResponse(content={"message": f"File conflict resolved by action {action}", "data": 0}, status_code=201)
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Not Faund conflict", "error": str(e)}, status_code=500)
# ----------------------------------------------


# Functions for async upload files on background
async def upload_generated_file(data_colection, upload_colection, now, action_extended_id, control_data, list_data, role):
    data_for_db = dict()
    data_for_db["action_id"] = action_extended_id
    data_for_db["created_at"] = now
    data_for_db["data"] = []
    data_for_db["status"] = "in progress"
    task = upload_colection.insert_one(data_for_db)

    # limit the reading area
    # * -1 because we don't read the total and 4 because we don't read header
    list_data = list_data[4:-1]
    for i in range(len(list_data)):
        list_data[i] = list_data[i][:20]

    title_list = ['_id', 'date', 'place_sending', 'type', 'phone', 'code', 'description', 'count', 'weight', 'space', 'density',
                  'place_delivery', 'packaging', 'delivery', 'other', 'insurance', 'unit_price', 'total', 'arrival_date', 'received_positions']

    data_list = []
    for i in range(len(list_data)):
        line_for_db = {}
        for j in range(len(title_list)):
            title = str(title_list[j])
            line_for_db[title] = list_data[i][j]
        data_list.append(line_for_db)

    data_buf_list = []

    # List for asincso tasks
    tasks = []

    for line in data_list:
        # print('line: ', get_serialize_document(line))
        buf = jsonable_encoder(UpdateDocumentManagerO.validate(
            get_serialize_document(line)))
        # print('buf: ', buf)
        tasks.append(asyncio.create_task(upload_generated_file_coroutine(data_colection,
                                                                         line,
                                                                         now,
                                                                         data_buf_list,
                                                                         role)))

    # Await all tasks
    await asyncio.gather(*tasks)
    await task

    # Check if changes exist
    if (len(data_buf_list) > 0):
        data_for_db = dict()
        data_for_db["data"] = data_buf_list
        data_for_db["control"] = control_data
        data_for_db["status"] = "ok"
        data_for_db = {'$set': data_for_db}
    else:
        data_for_db = dict()
        data_for_db["control"] = control_data
        data_for_db["status"] = "no changes"
        data_for_db = {'$set': data_for_db}

    await upload_colection.update_one({"action_id": action_extended_id}, data_for_db)


async def upload_external_file(upload_colection, now, action_extended_id, list_data, role):
    print("start Function")
    data_for_db = dict()
    data_for_db["action_id"] = action_extended_id
    data_for_db["created_at"] = now
    data_for_db["data"] = []
    data_for_db["status"] = "in progress"
    task = upload_colection.insert_one(data_for_db)

    # limit the reading area
    # * -1 because we don't read the total and 4 because we don't read header
    list_data = list_data[3:-1]
    for i in range(len(list_data)):
        list_data[i] = list_data[i][:19]

    title_list = ['date', 'place_sending', 'type', 'phone', 'code', 'description', 'count', 'weight', 'space', 'density',
                  'place_delivery', 'packaging', 'delivery', 'other', 'insurance', 'unit_price', 'total', 'arrival_date', 'received_positions']

    data_list = []
    for i in range(1, len(list_data)):
        line_for_db = {}
        for j in range(len(title_list)):
            title = str(title_list[j])
            line_for_db[title] = list_data[i][j]

        if role == 1:
            line_for_db = dict(UpdateDocument.validate(get_serialize_document(
                UpdateDocumentManagerO.validate(get_serialize_document(line_for_db)))))

        line_for_db["created_at"] = now
        line_for_db["updated_at"] = now
        data_list.append(line_for_db)

    await task

    if (len(data_list) > 0):
        data_for_db = dict()
        data_for_db["data"] = data_list
        data_for_db["status"] = "ok"
        data_for_db = {'$set': data_for_db}
    else:
        data_for_db = dict()
        data_for_db["status"] = "no changes"
        data_for_db = {'$set': data_for_db}

    await upload_colection.update_one({"action_id": action_extended_id}, data_for_db)
    print("Success Function")


async def upload_generated_file_coroutine(data_colection, line, now, data_buf_list, role):
    buf_data = dict(line)

    # Check if id field is exist and valid
    if (ObjectId.is_valid(line['_id'])):
        filter = {"_id": ObjectId(line['_id'])}
        result = await data_colection.find_one(filter)
        # Check if product is exist
        if (result is not None):
            # Calculate the number of modified fields and check it
            sum_chenges = sum(
                1 for key, value in buf_data.items() if (result.get(key) != value and result.get(key) != None)) - 1

            if sum_chenges > 0:
                buf_data["updated_at"] = now
                data_buf_list.append(buf_data)

            return
        return
    # If product not in collection add new product
    del buf_data["_id"]
    buf_data["created_at"] = now
    buf_data["updated_at"] = now
    data_buf_list.append(buf_data)


async def confirm_file_coroutine(line, data_colection, insert_data, login, additional):
    data = dict(line)

    # Check if line contains _id field
    if (line.get('_id') is not None):
        filter = {'_id': ObjectId(line['_id'])}

        del data['_id']

        update = {"$set": data}
        result = await data_colection.find_one_and_update(filter, update)
        myLoggerUpdate = CustomUpdate(data_colection)
        result = await myLoggerUpdate.find_update(filter,
                                                  update,
                                                  login,
                                                  additional)

        # Check if product exists
        if (result is None):
            insert_data.append(data)
    else:
        # if line not contains _id field
        insert_data.append(data)
# ----------------------------------------------
