from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime
from app.iternal.models.user import RegUser

router = APIRouter(
    prefix="/manager",
    tags=["Manager"],
)


@router.get('/protected')
def get_protected(request: Request, response: Response) -> dict:
    session = request.app.state.r_session.protected_session(request, response, 0)
    print('session: ', session)
    if len(session) > 0:
        return {'message': 'Access granted'}
    else:
        return {'message': 'Access denied'}
