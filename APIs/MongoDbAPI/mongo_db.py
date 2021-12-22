from motor.motor_asyncio import AsyncIOMotorClient

from APIs.MongoDbAPI.mongo_db_exceptions import EmptyResponse
from tokens import MONGO_DB_LOGIN, MONGO_DB_PASSWORD, MONGO_DB_NAME


class MongoDB:
    def __init__(self):
        self._client = AsyncIOMotorClient(
            f"mongodb+srv://{MONGO_DB_LOGIN}:{MONGO_DB_PASSWORD}"
            f"@cluster.rfoam.mongodb.net/"
            f"{MONGO_DB_NAME}?"
            f"retryWrites=true&"
            f"w=majority",
            port=27017,
        )
        self._users_collection = self._client[MONGO_DB_NAME]["Users"]

    async def get_status(self):
        if (await self._users_collection.find_one({"id": 447828812}))["platform"] == 'vk':
            return "working"
        else:
            return "not working"

    async def get_user_data(self, platform_id, api_name):
        bot_user = await self._users_collection.find_one({"id": platform_id, "platform": api_name})
        if bot_user is None:
            raise EmptyResponse
        return {
            "group_name": bot_user["group_name"],
            "professor_name": bot_user["professor_name"]
        }

    async def set_user_data(self, user_id, api_name,
                      group_name=None, mailing_time=None, professor_name=None):
        await self._users_collection.find_one_and_delete({"id": user_id, "platform": api_name})
        await self._users_collection.insert_one({
            "id": user_id,
            "platform": api_name,
            "mailing_time": mailing_time,
            "group_name": group_name,
            "professor_name": professor_name
        })

    async def update_mailing_time(self, user_id, api_name, time=None):
        await self._users_collection.update_one({
            "id": user_id,
            "platform": api_name,
        }, {
            "$set": {
                "mailing_time": time
            }
        })

    async def get_mailing_subscribers_by_time(self, time):
        subscribers = await self._users_collection.find({"mailing_time": time})
        simplified_subscribers = []
        for subscriber in subscribers:
            simplified_subscribers.append([subscriber["id"], subscriber["platform"]])
        return simplified_subscribers
