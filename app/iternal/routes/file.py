from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import JSONResponse, Response
from bson.objectid import ObjectId
from datetime import datetime
from io import BytesIO

import pandas as pd

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


async def verification_upload_time(database, control_data, company_key: str) -> bool:
    control_data_colection = database.get_collection("control_data")

    upload_at = datetime.now().timestamp()
    export_at = control_data.get("export_at")

    filter = {"company_key": company_key}
    result = await control_data_colection.find_one(filter)
    if not result:
        if export_at:
            control_data_colection.insert_one(
                {"company_key": company_key, "upload_at": export_at})
            upload_at = export_at
        else:
            control_data_colection.insert_one(
                {"company_key": company_key, "upload_at": upload_at})
    else:
        upload_at = result.get("upload_at")

    if export_at and upload_at <= export_at:
        update = {"$set": {"upload_at": export_at}}
        result = await control_data_colection.find_one_and_update(filter, update)

        return True
    return False


@router.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    # Read the Excel file using Pandas from the file's content
    content = await file.read()

    control_data = {}

    try:
        # Assuming the file is in .xlsx format.
        control_data_df = pd.read_excel(
            BytesIO(content), engine="openpyxl", sheet_name="__control_data")

        # Fill the empty with zero values ( df.fillna(0) )
        control_data_df_filled_with_zero = control_data_df.where(
            pd.notnull(control_data_df), None)

        # Convert to array
        control_data_array_data = control_data_df_filled_with_zero.to_numpy().tolist()

        # Check if the array
        if len(control_data_array_data) > 0:

            # limit the reading area
            control_data_array_keys = control_data_array_data[3:4]
            control_data_array_data = control_data_array_data[4:5]

            # Collect data from control_data sheet
            for i in range(0, len(control_data_array_keys)):
                key = control_data_array_keys[i][0]
                data = control_data_array_data[i][0]
                control_data[key] = data

    except Exception as e:
        print({"message": str(e)})

    now = datetime.now()

    try:
        # Assuming the file is in .xlsx format.
        df = pd.read_excel(BytesIO(content), engine="openpyxl")

        # Fill the empty with zero values ( df.fillna(0) )
        df_filled_with_zero = df.where(pd.notnull(df), None)
        array_data = df_filled_with_zero.to_numpy().tolist()  # Convert to array

        if not len(control_data) > 0:
            # limit the reading area
            # * -1 because we don't read the total and 4 because we don't read header
            array_data = array_data[3:-1]
            for i in range(len(array_data)):
                array_data[i] = array_data[i][:19]

            title_array = ['Дата', 'Место отправки', 'Вид отправки', 'Телефон клиента', 'Код клиента', 'Описание груза ', 'Количество мест', 'Вес', 'Плотность места', 'Плотность',
                           'Место доставки', 'За упаковку', 'За доставку', 'Разное', 'Страховка', 'Цена за единицу', 'Общая сумма', 'Дата прихода', 'Количество полученных позицый']
            data_array = array_data[1:]

            data_for_db = []
            for i in range(len(data_array)):
                line_for_db = {}
                for j in range(len(title_array)):
                    title = str(title_array[j])
                    line_for_db[title] = data_array[i][j]
                line_for_db["created_at"] = now
                line_for_db["updated_at"] = now
                data_for_db.append(line_for_db)

            database = request.app.state.mongodb["Dina_Cargo"]
            business_colection = database.get_collection("data")

            result = await business_colection.insert_many(data_for_db)

        else:
            # limit the reading area
            array_data = array_data[3:]
            for i in range(len(array_data)):
                array_data[i] = array_data[i][:20]

            title_array = ['_id', 'Дата', 'Место отправки', 'Вид отправки', 'Телефон клиента', 'Код клиента', 'Описание груза ', 'Количество мест', 'Вес', 'Плотность места', 'Плотность',
                           'Место доставки', 'За упаковку', 'За доставку', 'Разное', 'Страховка', 'Цена за единицу', 'Общая сумма', 'Дата прихода', 'Количество полученных позицый']
            data_array = array_data[1:]

            data_for_db = []
            for i in range(len(data_array)):
                line_for_db = {}
                for j in range(len(title_array)):
                    title = str(title_array[j])
                    line_for_db[title] = data_array[i][j]
                data_for_db.append(line_for_db)

            database = request.app.state.mongodb["Dina_Cargo"]
            business_colection = database.get_collection("data")

            if await verification_upload_time(request.app.state.database, control_data, "Dina_Cargo"):
                for line in data_for_db:
                    filter = {"_id": ObjectId(line['_id'])}

                    buf_data = line
                    del buf_data['_id']
                    buf_data["updated_at"] = now
                    update = {"$set": buf_data}

                    result = await business_colection.find_one_and_update(filter, update)
                    if not result:
                        buf_data["created_at"] = now
                        buf_data["updated_at"] = now
                        result = await business_colection.insert_one(buf_data)
                        print("create", result.inserted_id)
                    else:
                        # Calculate the number of modified fields
                        num_modified_fields = (
                            sum(1 for key, value in update["$set"].items() if result.get(key) != value) - 1)
                        if num_modified_fields > 0:
                            print("update", result.get('_id'), "count", num_modified_fields)
            else:
                print("Error")

        # Success
        return JSONResponse(content={"message": "File uploaded successfully"})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": str(e)}, status_code=500)


@router.get("/export_excel/")
async def export_excel(request: Request):
    try:
        database = request.app.state.mongodb["Dina_Cargo"]
        business_colection = database.get_collection("data")

        result = await business_colection.find({}).to_list(None)

        for i in range(0, len(result)):
            # del result[i]["_id"]
            del result[i]["created_at"]
            del result[i]["updated_at"]
            result[i]["_"] = ""

        # Create a DataFrame from the data
        df = pd.DataFrame(result)
        df2 = pd.DataFrame({"export_at": [datetime.utcnow().timestamp()]})

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
        print('e: ', e)
        # Exception
        return JSONResponse(content={"message": f"Не найден, обновление не выполнено."}, status_code=500)


@router.post("/put/")
async def upload_file(request: Request):
    try:
        database = request.app.state.mongodb["Dina_Cargo"]
        business_colection = database.get_collection("data")

        filter = {"_id": ObjectId("64bfaaf84582a086bb484b11")}
        update = {"$set": {"Вес": 100}}

        # result = await business_colection.update_one(filter, update)
        result = await business_colection.update_one(filter, update)

        # Success
        return JSONResponse(content={"message": f"Успешно обновлен."})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": f"Не найден, обновление не выполнено."}, status_code=500)


@router.post("/get/")
async def upload_file(request: Request):
    try:
        database = request.app.state.mongodb["Dina_Cargo"]
        business_colection = database.get_collection("data")

        filter = {"_id": ObjectId("64bfaaf84582a086bb484b11")}

        result = await business_colection.find({}).to_list(None)

        for res in result[0].keys():
            result[0][res] = str(result[0][res])

        # Success
        return JSONResponse(content={"message": f"Успешно обновлен.", "result": result[0]})
    except Exception as e:
        print('e: ', e)
        # Exception
        return JSONResponse(content={"message": f"Не найден, обновление не выполнено."}, status_code=500)
