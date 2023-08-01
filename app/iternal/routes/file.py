from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import JSONResponse, Response
from bson.objectid import ObjectId
from datetime import datetime
from io import BytesIO

import pandas as pd

import asyncio

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@router.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
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
        database = request.app.state.mongodb["Dina_Cargo"]
        upload_colection = database.get_collection("upload")
        data_colection = database.get_collection("data")

        # Check if the control_data exists
        if (len(control_data) > 0):

            task = asyncio.create_task(upload_generated_file(
                data_colection, upload_colection, now, action_extended_id, control_data, list_data))

        else:
            task = asyncio.create_task(upload_external_file(
                upload_colection, now, action_extended_id, list_data))

        print("Success point")
        # Success
        return JSONResponse(content={"message": "File pre-upload successfully", "data": str(action_extended_id)}, status_code=202)
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": str(e)}, status_code=422)


@router.post("/confirm/{id}")
async def confirm_file(request: Request, id: str):
    try:
        database = request.app.state.mongodb["Dina_Cargo"]
        upload_colection = database.get_collection("upload")
        control_colection = request.app.state.database.get_collection(
            "control_data")

        filter = {'action_id': ObjectId(id)}

        result = await upload_colection.find_one(filter)

        # Check if id exists
        if (result is not None):
            data_for_db = result.get('data')
            control_data = result.get('control')

            data_colection = database.get_collection("data")

            # Check if control_data exists
            if (control_data):
                # Create control timestamp
                upload_at = 0
                export_at = control_data.get("export_at")

                filter = {"company_key": "Dina_Cargo"}
                result = await control_colection.find_one(filter)

                # Check if upload_at exists
                if (result is None):
                    insert = {
                        "company_key": "Dina_Cargo",
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
                    result = await upload_colection.find_one_and_update(filter, update)

                    # Success
                    return JSONResponse(content={"message": "File confirm conflict", "data": str(result['action_id'])}, status_code=409)

                insert_data = []
                for line in data_for_db:

                    data = dict(line)
                    del data['_id']

                    # Check if line contains _id field
                    if (line.get('_id') is not None):
                        filter = {'_id': ObjectId(line['_id'])}
                        update = {"$set": data}
                        result = await data_colection.find_one_and_update(filter, update)

                        # Check if product exists
                        if (result is None):
                            insert_data.append(data)
                    else:
                        # if line not contains _id field
                        insert_data.append(data)

                # Check if changes exist
                if (len(insert_data) > 0):
                    result = await data_colection.insert_many(insert_data)

                filter = {"company_key": "Dina_Cargo"}
                update = {"$set": {"upload_at": export_at}}
                result = await control_colection.update_one(filter, update)

            else:
                result = await data_colection.insert_many(data_for_db)

        filter = {'action_id': ObjectId(id), "status": "ok"}
        result = await upload_colection.delete_one(filter)

        # Success
        return JSONResponse(content={"message": "File confirm successfully"}, status_code=202)
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": str(e)}, status_code=500)


@router.get("/export_excel/")
async def export_excel(request: Request):
    # Get now data
    now = datetime.utcnow()

    try:
        database = request.app.state.mongodb["Dina_Cargo"]
        upload_colection = database.get_collection("data")

        result = await upload_colection.find({}).to_list(None)

        for i in range(0, len(result)):
            del result[i]["created_at"]
            del result[i]["updated_at"]
            result[i]["_"] = ""

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
        file_name = "exported_data.xlsx"
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


@router.get("/conflict/{id}")
async def conflict(request: Request, id: str):
    try:
        database = request.app.state.mongodb["Dina_Cargo"]
        upload_colection = database.get_collection("upload")
        data_colection = database.get_collection("data")

        filter = {'action_id': ObjectId(id), "status": "conflict"}
        result = await upload_colection.find_one(filter)

        new_data = result.get("data")
        for data in new_data:
            del data["updated_at"]
            for key in data.keys():
                data[key] = str(data.get(key))
        curren_data = []

        for data in new_data:
            filter = {'_id': ObjectId(data.get("_id"))}
            result = await data_colection.find_one(filter)
            if result is not None:
                del result["updated_at"]
                del result["created_at"]

                for key in result.keys():
                    result[key] = str(result.get(key))
                curren_data.append(result)

        # Success
        return JSONResponse(content={"message": "File conflict objects", "data": {"new_data": new_data, "curren_data": curren_data}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": str(e)}, status_code=404)


@router.get("/conflict/{id}/{object_id}")
async def conflict(request: Request, id: str, object_id: str):
    try:
        database = request.app.state.mongodb["Dina_Cargo"]
        upload_colection = database.get_collection("upload")
        data_colection = database.get_collection("data")

        filter = {'action_id': ObjectId(id), "status": "conflict"}
        result = await upload_colection.find_one(filter)

        data_buf = result.get("data")
        new_data = []
        for data in data_buf:
            if (data['_id'] == object_id):
                del data["updated_at"]
                for key in data.keys():
                    data[key] = str(data.get(key))
                new_data.append(data)

        curren_data = []

        for data in new_data:
            filter = {'_id': ObjectId(data.get("_id"))}
            result = await data_colection.find_one(filter)
            if result is not None:
                del result["updated_at"]
                del result["created_at"]

                for key in result.keys():
                    result[key] = str(result.get(key))
                curren_data.append(result)

        # Success
        return JSONResponse(content={"message": "File conflict objects", "data": {"new_data": new_data, "curren_data": curren_data}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": str(e)}, status_code=404)


@router.get("/conflict/{id}/{object_id}/{action}")
async def conflict(request: Request, id: str, object_id: str, action: str):
    try:
        if action not in ["new", "current"]:
            raise Exception("action not supported [new, current]")

        database = request.app.state.mongodb["Dina_Cargo"]
        upload_colection = database.get_collection("upload")
        data_colection = database.get_collection("data")

        filter = {'action_id': ObjectId(id), "status": "conflict"}
        result = await upload_colection.find_one(filter)

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
        return JSONResponse(content={"message": "Not Faund conflict", "error": str(e)}, status_code=404)


# Functions for async upload files on background
async def upload_generated_file(data_colection, upload_colection, now, action_extended_id, control_data, list_data):
    print("start Function")
    # limit the reading area
    list_data = list_data[4:]
    for i in range(len(list_data)):
        list_data[i] = list_data[i][:20]

    title_list = ['_id', 'Дата', 'Место отправки', 'Вид отправки', 'Телефон клиента', 'Код клиента', 'Описание груза ', 'Количество мест', 'Вес', 'Плотность места', 'Плотность',
                  'Место доставки', 'За упаковку', 'За доставку', 'Разное', 'Страховка', 'Цена за единицу', 'Общая сумма', 'Дата прихода', 'Количество полученных позицый']

    data_list = []
    for i in range(len(list_data)):
        line_for_db = {}
        for j in range(len(title_list)):
            title = str(title_list[j])
            line_for_db[title] = list_data[i][j]
        data_list.append(line_for_db)

    data_buf_list = []

    for line in data_list:
        buf_data = dict(line)
        # Check if id field is exist and valid
        if (ObjectId.is_valid(line['_id'])):
            filter = {"_id": ObjectId(line['_id'])}
            result = await data_colection.find_one(filter)
            # Check if product is exist
            if (result is not None):
                # Calculate the number of modified fields and check it
                sum_chenges = sum(
                    1 for key, value in buf_data.items() if result.get(key) != value) - 1

                if sum_chenges > 0:
                    buf_data["updated_at"] = now
                    data_buf_list.append(buf_data)
            else:
                # If product not in connection
                del buf_data["_id"]
                buf_data["created_at"] = now
                buf_data["updated_at"] = now
                data_buf_list.append(buf_data)
        else:
            # If add new product
            del buf_data["_id"]
            buf_data["created_at"] = now
            buf_data["updated_at"] = now
            data_buf_list.append(buf_data)

    # Check if changes exist
    if (len(data_buf_list) > 0):
        data_for_db = dict()
        data_for_db["action_id"] = action_extended_id
        data_for_db["created_at"] = now
        data_for_db["control"] = control_data
        data_for_db["data"] = data_buf_list
        data_for_db["status"] = "ok"

        # * Есть вопросы, но пойдёт
        result = await upload_colection.insert_one(data_for_db)
    print("Success Function")


async def upload_external_file(upload_colection, now, action_extended_id, list_data):
    print("start Function")
    # limit the reading area
    # * -1 because we don't read the total and 4 because we don't read header
    list_data = list_data[4:-1]
    for i in range(len(list_data)):
        list_data[i] = list_data[i][:19]

    title_list = ['Дата', 'Место отправки', 'Вид отправки', 'Телефон клиента', 'Код клиента', 'Описание груза ', 'Количество мест', 'Вес', 'Плотность места', 'Плотность',
                  'Место доставки', 'За упаковку', 'За доставку', 'Разное', 'Страховка', 'Цена за единицу', 'Общая сумма', 'Дата прихода', 'Количество полученных позицый']

    data_list = []
    for i in range(len(list_data[1:])):
        line_for_db = {}
        for j in range(len(title_list)):
            title = str(title_list[j])
            line_for_db[title] = list_data[i][j]
        line_for_db["created_at"] = now
        line_for_db["updated_at"] = now
        data_list.append(line_for_db)

    if (len(data_list) > 0):
        data_for_db = dict()
        data_for_db["action_id"] = action_extended_id
        data_for_db["created_at"] = now
        data_for_db["data"] = data_list
        data_for_db["status"] = "ok"

        # * Есть вопросы, но пойдёт
        result = await upload_colection.insert_one(data_for_db)
    print("Success Function")
# ----------------------------------------------
