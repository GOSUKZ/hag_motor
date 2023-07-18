from fastapi import APIRouter, Body, Request
from ..db.user import addUser, getAllUsers, updateUser, delUser
# from ..db.db import client
from ..models.user import User, UpdateUser
from ..serializers.user import userEntity

from fastapi.encoders import jsonable_encoder

# import motor.motor_asyncio

from app.iternal.config import settings

# DATABASE_URL = settings.DATABASE_URL
MONGO_INITDB_DATABASE = settings.MONGO_INITDB_DATABASE

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.post("/", response_description="Success")
async def root(request: Request, user : User = Body(...)):
    user = jsonable_encoder(user)
    # client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
    database = request.app.state.mongodb[MONGO_INITDB_DATABASE]
    user = await addUser(database, user)
    user = userEntity(user)
    return user

@router.put("/", response_description="Success")
async def root(request: Request, user : UpdateUser = Body(...)):
    user = jsonable_encoder(user)
    # client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
    database = request.app.state.mongodb[MONGO_INITDB_DATABASE]
    user = await updateUser(database, user)
    user = userEntity(user)
    return user

@router.delete("/", response_description="Success")
async def root(request: Request, id: str):
    # client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
    database = request.app.state.mongodb[MONGO_INITDB_DATABASE]
    user = await delUser(database, id)
    user = userEntity(user)
    return user

@router.get("/", response_description="Success")
async def root(request: Request):
    # client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
    database = request.app.state.mongodb[MONGO_INITDB_DATABASE]
    users_db = await getAllUsers(database)
    users = []
    for user in users_db:
        users.append(userEntity(user))
    return users