from fastapi.responses import StreamingResponse
import io
from fastapi import APIRouter, Body, File, UploadFile, Request
from fastapi.responses import JSONResponse, Response
from bson.objectid import ObjectId
from datetime import datetime
from io import BytesIO

import pandas as pd

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@router.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        # Read the Excel file using Pandas from the file's content
        content = await file.read()
        # Assuming the file is in .xlsx format.
        df = pd.read_excel(BytesIO(content), engine="openpyxl")

        df_filled_with_zero = df.fillna(0)  # Fill the empty with zero values
        array_data = df_filled_with_zero.to_numpy().tolist()  # Convert to array

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
            line_for_db["created_at"] = datetime.now()
            line_for_db["updated_at"] = datetime.now()
            data_for_db.append(line_for_db)

        database = request.app.state.mongodb["Dina_Cargo"]
        business_colection = database.get_collection("Data_Business_Colection")

        result = await business_colection.insert_many(data_for_db)

        # * Временное решение для отладки
        # with open("log.txt", "w", encoding="utf-8") as f:
        #     for line in array_data:
        #         f.writelines(str(line).replace("\n", "") + "\n")

        # Success
        return JSONResponse(content={"message": "File uploaded successfully"})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": str(e)}, status_code=500)


@router.get("/export_excel/")
async def export_excel(request: Request):
    try:
        database = request.app.state.mongodb["Dina_Cargo"]
        business_colection = database.get_collection("Data_Business_Colection")

        result = await business_colection.find({}).to_list(None)

        for i in range(0, len(result)):
            del result[i]["_id"]
            del result[i]["created_at"]
            del result[i]["updated_at"]
            result[i]["_"] = ""
            # for res in result[i].keys():
            #     result[i][res] = str(result[i][res])

        # Create a DataFrame from the data
        df = pd.DataFrame(result)
        # Create an Excel writer using BytesIO
        excel_writer = BytesIO()
        # Write the DataFrame to the Excel file
        df.to_excel(excel_writer, index=False, startrow=3,
                    header="Dina_Cargo", engine="openpyxl")
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
        business_colection = database.get_collection("Data_Business_Colection")

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
        business_colection = database.get_collection("Data_Business_Colection")

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
