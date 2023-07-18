def userEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "description": user["description"],
        "price": user["price"],
        "tax": user["tax"]
    }