
class CustomUpdate:
    def __init__(self, collection):
        self.__collection = collection

    def __del__(self):
        pass

    async def update(self, filter, update):
        print("update_one")
        return self.__collection.update_one(filter, update, {'upsert': False})

    async def find_update(self, filter, update):
        print("find_one_and_update")
        old_data = await self.__collection.find_one_and_update(filter, update, {'upsert': False})
        return old_data
