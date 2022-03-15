from motor.motor_asyncio import AsyncIOMotorClient

from Exceptions.empty_response import EmptyResponse


class MongoDB:
    def __init__(self, db_login: str, db_password: str, db_name: str):
        client = AsyncIOMotorClient(
            f"mongodb+srv://{db_login}:{db_password}"
            f"@cluster.rfoam.mongodb.net/"
            f"{db_name}?"
            f"retryWrites=true&"
            f"w=majority",
            port=27017,
        )
        self._users_collection = client[db_name]["Users"]
        self._groups_collection = client[db_name]["Groups"]

    async def get_status(self):
        if (await self._users_collection.find_one({"id": 447828812}))["platform"] == 'vk':
            return "working"
        else:
            return "not working"

    async def get_user_data(self, platform_id, api_name, time=None):
        bot_user = await self._users_collection.find_one_and_update({
            "id": platform_id, "platform": api_name},
            {
                "$push": {"requests_time": {"$each": [time]}},
                "$unset": {"last_request_time": 1}
            }, upsert=True)
        if bot_user is None or not ("group_name" in bot_user or "professor_name" in bot_user):
            raise EmptyResponse
        return {
            "group_name": bot_user["group_name"]
        } if "group_name" in bot_user and bot_user["group_name"] is not None else {
            "professor_name": bot_user["professor_name"]
        }

    async def set_user_data(self, user_id, api_name, group_name=None, professor_name=None):
        await self.set_check_changes_member(user_id, api_name, False)
        await self._users_collection.find_one_and_delete({"id": user_id, "platform": api_name})
        request = {"id": user_id, "platform": api_name}
        if group_name:
            request['group_name'] = group_name
        elif professor_name:
            request['professor_name'] = professor_name
        await self._users_collection.insert_one(request)

    async def get_mailing_subscribers_by_time(self, time: str) -> list:
        cursor = self._users_collection.find({"mailing_time": time})
        subscribers = await self._parse_response(cursor)
        return list(map(lambda subscriber: [subscriber["id"], subscriber["platform"]], subscribers))

    async def set_mailing_time(self, user_id, api_name, time=None):
        if time is None:
            update_parameter = {"$unset": {"mailing_time": 1}}
        else:
            update_parameter = {"$set": {"mailing_time": time}}
        await self._users_collection.update_one({
            "id": user_id,
            "platform": api_name,
        }, update_parameter)

    @staticmethod
    async def _parse_response(cursor):
        response_list = []
        while await cursor.fetch_next:
            response = cursor.next_object()
            response_list.append(response)
        return response_list

    async def get_groups_list(self) -> list:
        cursor = self._groups_collection.find()
        groups = await self._parse_response(cursor)
        return list(map(lambda group_obj: group_obj['name'], groups))

    async def get_check_changes_members(self, group: str) -> list:
        return (await self._groups_collection.find_one({"name": group}))['users']

    async def set_check_changes_member(self, user_id: int, api_name: str, check_changes=False) -> None:
        user_data = await self._users_collection.find_one({"id": user_id, "platform": api_name})
        if user_data is None or not ("group_name" in user_data or "professor_name" in user_data):
            return
        user_id = user_data["id"]
        chat_platform = user_data["platform"]
        request = {"users": {"id": user_id, "platform": chat_platform}}
        find_params = {"name": user_data['group_name'] if "group_name" in user_data else user_data['professor_name']}

        if check_changes:
            await self._groups_collection.find_one_and_update(find_params, {"$addToSet": request}, upsert=True)
        else:
            resp = await self._groups_collection.find_one_and_update(find_params, {"$pull": request}, upsert=True)
            if self._is_group_empty(resp, user_id, chat_platform):
                self._groups_collection.delete_one(find_params)

    def _is_group_empty(self, resp, user_id, chat_platform):
        return not resp or (
                resp and (self._is_last_user(resp, user_id, chat_platform)) or ("name" in resp and "users" not in resp)
        )

    @staticmethod
    def _is_last_user(resp, user_id, user_chat_platform) -> bool:
        return 'users' in resp and \
               len(resp['users']) == 1 and \
               resp['users'][0]['id'] == user_id and \
               resp['users'][0]['platform'] == user_chat_platform

    async def get_group_hashes(self, group_name: str):
        find_parameter = {"name": group_name}
        return await self._groups_collection.find_one(find_parameter)

    async def set_group_hashes(self, hashes: list, group_name: str):
        await self._groups_collection.update_one({"name": group_name}, {"$set": {"hashes": hashes}})
