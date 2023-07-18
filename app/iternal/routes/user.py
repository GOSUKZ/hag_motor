from fastapi import APIRouter, Body
from ..db.user import addUser, getAllUsers, updateUser, delUser
from ..db.db import client
from ..models.user import User, UpdateUser
from ..serializers.user import userEntity

from fastapi.encoders import jsonable_encoder


router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.post("/", response_description="Success")
async def root(user : User = Body(...)):
    # Use "await" for start_session, but not for start_transaction.
    async with await client.start_session() as s:
        user = await addUser(s, user)
        user = userEntity(user)
    return user

@router.put("/", response_description="Success")
async def root(user : UpdateUser = Body(...)):
    user = jsonable_encoder(user)
    # Use "await" for start_session, but not for start_transaction.
    async with await client.start_session() as s:
        user = await updateUser(s, user)
        user = userEntity(user)
    return user

@router.delete("/", response_description="Success")
async def root(id: str):
    # Use "await" for start_session, but not for start_transaction.
    async with await client.start_session() as s:
        user = await delUser(s, id)
        user = userEntity(user)
    return user

@router.get("/", response_description="Success")
async def root():
    # Use "await" for start_session, but not for start_transaction.
    async with await client.start_session() as s:
        users_db = await getAllUsers(s)
        users = []
        for user in users_db:
            users.append(userEntity(user))
    return users