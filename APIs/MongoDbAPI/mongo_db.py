from motor.motor_asyncio import AsyncIOMotorClient

from APIs.MongoDbAPI.mongo_db_exceptions import EmptyResponse


class MongoDB:
    def __init__(self, db_login, db_password, db_name):
        self._client = AsyncIOMotorClient(
            f"mongodb+srv://{db_login}:{db_password}"
            f"@cluster.rfoam.mongodb.net/"
            f"{db_name}?"
            f"retryWrites=true&"
            f"w=majority",
            port=27017,
        )
        self._users_collection = self._client[db_name]["Users"]

    async def get_status(self):
        if (await self._users_collection.find_one({"id": 447828812}))["platform"] == 'vk':
            return "working"
        else:
            return "not working"

    async def get_user_data(self, platform_id, api_name, time):
        last_request = time.strftime("%d.%m.%Y %H:%M:%S")
        bot_user = await self._users_collection.find_one_and_update(
            {
                "id": platform_id,
                "platform": api_name
            }, {
                "$inc": {
                    "request_count": 1
                },
                "$set": {
                    "last_request_time": last_request
                }
            },
            upsert=True
        )
        if bot_user is None:
            raise EmptyResponse
        return {
            "group_name": bot_user["group_name"]
        } if "group_name" in bot_user and bot_user["group_name"] is not None else {
            "professor_name": bot_user["professor_name"]
        }

    async def set_user_data(self, user_id, api_name, group_name=None, professor_name=None):
        await self._users_collection.find_one_and_delete({"id": user_id, "platform": api_name})
        request = {
            "id": user_id,
            "platform": api_name
        }
        if group_name:
            request['group_name'] = group_name
        if professor_name:
            request['professor_name'] = professor_name
        await self._users_collection.insert_one(request)

    async def update_mailing_time(self, user_id, api_name, time=None):
        if time is None:
            update_parameter = {"$unset": {"mailing_time": 1}}
        else:
            update_parameter = {"$set": {"mailing_time": time}}
        await self._users_collection.update_one({
            "id": user_id,
            "platform": api_name,
        }, update_parameter)

    async def get_mailing_subscribers_by_time(self, time):
        subscribers = await self._users_collection.find({"mailing_time": time}).to_list(1000)
        simplified_subscribers = []
        for subscriber in subscribers:
            simplified_subscribers.append([subscriber["id"], subscriber["platform"]])
        return simplified_subscribers
