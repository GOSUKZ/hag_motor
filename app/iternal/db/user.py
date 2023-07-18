from .db import database
from ..models.user import User, UpdateUser;
from bson.objectid import ObjectId

user_colection = database.get_collection("user")

async def addUser(session, user : User):
    user = await user_colection.insert_one(user, session=session)
    user = await user_colection.find_one({"_id": ObjectId(user.inserted_id)}, session=session)
    if user:
        return user

async def getAllUsers(session):
    users = []
    async for user in user_colection.find(session=session):
        users.append(user)
    return users

async def delUser(session, id: str):
    user = await user_colection.find_one({"_id": ObjectId(id)}, session=session)
    if user:
        await user_colection.delete_one({"_id": ObjectId(id)}, session=session)
        return user
    
async def updateUser(session, user: UpdateUser):
    old_user = await user_colection.find_one_and_update({"_id": ObjectId(user.get('id'))}, {"$set": user}, session=session)
    return old_user