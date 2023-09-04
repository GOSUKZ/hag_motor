from bson.objectid import ObjectId
from datetime import datetime

from json import dumps

# Define the format of the date and time in the string
# buf_data = dict(data)
# for key, value in data.items():
#     try:
#         if type(value) is str:

#             if model[key] == "datetime":
#                 # if len(value) <= len("2023-01-16 00:00:00"):
#                 #     data[key] = buf_data[key]+'.000000'
#                 buf_data[key] = types[model[key]](buf_data[key], date_format)

#             elif value == "None":
#                 buf_data[key] = None

#             else:
#                 buf_data[key] = types[model[key]](value)
#         else:
#             buf_data[key] = str(value)

#     except:
#         del buf_data[key]
#         print('key: ', key)

# return buf_data

date_format = "%Y-%m-%d %H:%M:%S.%f"

temp_model = {
    "_id": "ObjectId",
    "date": "datetime",
    "place_sending": "str",
    "type": "str",
    "phone": "str",
    "code": "str",
    "description": "str",
    "count": 'int',
    "weight": "float",
    "space": "float",
    "density": "float",
    "place_delivery": "str",
    "packaging": "float",
    "delivery": "float",
    "other": "float",
    "insurance": "int",
    "unit_price": "float",
    "total": "float",
    "arrival_date": "datetime",
    "received_positions": "int",
    "log_colection": "list",
    "created_at": "datetime",
    "updated_at": "datetime"
}

types = {
    "ObjectId": ObjectId,
    "datetime": datetime.strptime,
    "str": str,
    "float": float,
    "int": int,
    "list": list
}


def is_jsonable(x):
    try:
        dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


def is_convertable(s: str):
    try:
        num = int(s)
        return num
    except ValueError:
        pass

    try:
        num = float(s)
        return num
    except ValueError:
        pass

    try:
        id = ObjectId(s)
        return id
    except ValueError:
        pass

    return s


def get_serialize_document(data: dict) -> dict:
    buf_data = dict(data)

    for key, value in buf_data.items():
        if not is_jsonable(value):
            buf_data[key] = str(value)

    if buf_data.get('log_collection') is not None:
        del buf_data['log_collection']

    return buf_data
