from fastapi import APIRouter, Body, Request
from ..db.user import addUser, getAllUsers, updateUser, delUser
from ..models.user import User, UpdateUser
from ..serializers.user import userEntity
from fastapi.encoders import jsonable_encoder


router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.post("/", response_description="Success")
async def root(request: Request, user : User = Body(...)):
    user = jsonable_encoder(user)
    database = request.app.state.database
    user = await addUser(database, user)
    user = userEntity(user)
    return user

@router.put("/", response_description="Success")
async def root(request: Request, user : UpdateUser = Body(...)):
    user = jsonable_encoder(user)
    database = request.app.state.database
    user = await updateUser(database, user)
    user = userEntity(user)
    return user

@router.delete("/", response_description="Success")
async def root(request: Request, id: str):
    database = request.app.state.database
    user = await delUser(database, id)
    user = userEntity(user)
    return user

@router.get("/", response_description="Success")
async def root(request: Request):
    database = request.app.state.database
    users_db = await getAllUsers(database)
    users = []
    for user in users_db:
        users.append(userEntity(user))
    return users