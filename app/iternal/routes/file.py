from fastapi import APIRouter, Body, File, UploadFile, Request
from fastapi.responses import JSONResponse
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
        df = pd.read_excel(BytesIO(content), engine="openpyxl")  # Assuming the file is in .xlsx format.

        # df_filled_with_zero = df.fillna(0) # Fill the empty with zero values
        # array_data = df_filled_with_zero.to_numpy().tolist() # Convert to array

        # # limit the reading area
        # array_data = array_data[3:-1] # * -1 because we don't read the total and 4 because we don't read header
        # for i in range(len(array_data)):
        #     array_data[i] = array_data[i][:19]

        # title_array = ['Дата', 'Место отправки', 'Вид отправки', 'Телефон клиента', 'Код клиента', 'Описание груза ', 'Количество мест', 'Вес', 'Плотность места', 'плотность', 'Место доставки', 'За упаковку', 'За доставку', 'Разное', 'Страховка', 'Цена за единицу', 'Общая сумма', 'Дата прихода', 'Количество полученных позицый']
        # data_array = array_data[1:]

        # data_for_db = []
        # for i in range(len(data_array)):
        #     line_for_db = {}
        #     for j in range(len(title_array)):
        #         title = str(title_array[j])
        #         line_for_db[title] = data_array[i][j]
        #     data_for_db.append(line_for_db)

        # database = request.app.state.mongodb["Dina_Cargo"]
        # business_colection = database.get_collection("Data_Business_Colection")
    
        # result = await business_colection.insert_one({'data': data_for_db, 'created_at': datetime.now(), 'updated_at': datetime.now()})
        # result = await business_colection.find_one({"_id": ObjectId(result.inserted_id)})

        # print('result: ', result)

        # * Временное решение для отладки
        # with open("log.txt", "w", encoding="utf-8") as f:
        #     for line in array_data:
        #         f.writelines(str(line).replace("\n", "") + "\n")
        
        return JSONResponse(content={"message": "File uploaded successfully"}) # Success
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500) # Exception