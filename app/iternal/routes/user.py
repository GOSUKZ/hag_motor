from fastapi import APIRouter, Body, Depends
from ..db.user import addUser, getAllUsers, updateUser, delUser
from ..db.db import client
from ..models.user import User, UpdateUser
from ..serializers.user import userEntity

from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/user", tags=["Users"])


async def get_mongodb_session():
    async with await client.start_session() as session:
        yield session


@router.post("/", response_description="Success")
async def root(user: User = Body(...), session=Depends(get_mongodb_session)):
    user = jsonable_encoder(user)
    user = await addUser(session, user)
    return userEntity(user)


@router.put("/", response_description="Success")
async def root(user: UpdateUser = Body(...), session=Depends(get_mongodb_session)):
    user = jsonable_encoder(user)
    user = await updateUser(session, user)
    return userEntity(user)


@router.delete("/", response_description="Success")
async def root(id: str, session=Depends(get_mongodb_session)):
    user = await delUser(session, id)
    return userEntity(user)


@router.get("/", response_description="Success")
async def root(session=Depends(get_mongodb_session)):
    users_db = await getAllUsers(session)
    users = [userEntity(user) for user in users_db]
    return users
