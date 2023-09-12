import asyncio
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import ReturnDocument


class CustomUpdate:
    def __init__(self, collection):
        self.__collection = collection

    def __del__(self):
        pass

    async def __log_coroutine(self, filter, old_data, login, additional, now):
        try:
            new_data = await self.__collection.find_one(filter)
            log_collection = list()

            old_data = dict(old_data)
            new_data = dict(new_data)

            if old_data.get('log_collection') is not None:
                log_collection = list(old_data.get('log_collection'))
                del old_data['log_collection']
                del new_data['log_collection']

            update_log = {
                'log_id': ObjectId(),
                'old_data': old_data,
                'new_data': new_data,
                'created_at': now,
                'login': login,
                'additional': additional
            }

            if len(log_collection) > 4:
                log_collection.pop(0)

            log_collection.append(update_log)

            update = {'$set': {'log_collection': log_collection}}

            await self.__collection.update_one(filter, update)
        except:
            pass

    async def __find_update_task(self, filter, update, login, additional, return_after=False):
        now = datetime.utcnow()
        update['$set']['updated_at'] = now

        if update['$set'].get('_id') is not None:
            print('update: ', update)
            print('filter: ', filter)
            del update['$set']['_id']

        return_document = ReturnDocument.BEFORE
        if (return_after):
            return_document = ReturnDocument.AFTER

        old_data = await self.__collection.find_one_and_update(filter, update, return_document=return_document, upsert=False)
        if old_data is not None:
            asyncio.create_task(self.__log_coroutine(filter,
                                                     old_data,
                                                     login,
                                                     additional,
                                                     now))
        return old_data

    async def find_update(self, filter, update, login='', additional='', return_after=False):
        task = asyncio.create_task(self.__find_update_task(filter,
                                                           update,
                                                           login,
                                                           additional,
                                                           return_after))
        return await task
