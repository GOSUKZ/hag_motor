from ..models.user import User, UpdateUser;
from bson.objectid import ObjectId


async def addUser(database, user : User):
    user_colection = database.get_collection("user")
    
    user = await user_colection.insert_one(user)
    user = await user_colection.find_one({"_id": ObjectId(user.inserted_id)})
    if user:
        return user

async def getAllUsers(database):
    user_colection = database.get_collection("user")

    users = []
    async for user in user_colection.find():
        users.append(user)
    return users

async def delUser(database, id: str):
    user_colection = database.get_collection("user")

    user = await user_colection.find_one({"_id": ObjectId(id)})
    if user:
        await user_colection.delete_one({"_id": ObjectId(id)})
        return user
    
async def updateUser(database, user: UpdateUser):
    user_colection = database.get_collection("user")

    old_user = await user_colection.find_one_and_update({"_id": ObjectId(user.get('id'))}, {"$set": user})
    return old_user