from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from app.iternal.models.user import RegUser

router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.get('/')
async def get_docs(request: Request, response: Response, start: int = 0, end: int = 10) -> dict:
    try:
        if ((start > end) or (start < 0) or (end < 0)):
            # Exception
            return JSONResponse(content={"message": "Start or end out of range"}, status_code=403)
        
        # Calculate the number of documents to skip
        skip = start

        # Calculate the number of documents to retrieve
        limit = end - start + 1

        session = request.app.state.r_session.protected_session(
            request, response, 99)

        if len(session) <= 0:
            # Exception
            return JSONResponse(content={"message": "Unauthorized or invalid sesion"}, status_code=401)

        company_key = session.get("company_key")

        #.sort('i', -1)

        # Connect to DB connection
        database = request.app.state.mongodb[company_key]
        data_colection = database.get_collection("data")

        documents = []

        task = data_colection.count_documents({})

        cursor = data_colection.find().skip(skip).limit(limit)
        async for document in cursor:
            for key in document.keys():
                document[key] = str(document[key])
            documents.append(document)

        documents_count = await task

        # Success
        return JSONResponse(content={"message": "Successfully", "data": {"documents": documents, "documents_count": documents_count}})
    except Exception as e:
        # Exception
        return JSONResponse(content={"message": "Get documents error", "error": str(e)}, status_code=500)
