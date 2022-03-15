import asyncio
import hashlib
from asyncio import AbstractEventLoop
from datetime import datetime

from APIs.Chsu.schedule import Schedule
from Wrappers.AIOHttp.aiohttp import AIOHttpWrapper
from Exceptions.empty_response import EmptyResponse


class Chsu:
    def __init__(self, event_loop: AbstractEventLoop):
        self._client = AIOHttpWrapper(event_loop)
        self._base_url = "http://api.chsu.ru/api/"
        self._headers = {
            "Content-Type": "application/json",
            "charset": "utf-8"
        }
        self._login_and_password = {
            "username": "mobil",
            "password": "ds3m#2nn"
        }
        self._id_by_professors = None
        self._id_by_groups = None
        event_loop.create_task(self._updating_token())

    async def _updating_token(self):
        while True:
            self._headers.pop("Authorization", '')
            response = await self._client.post(
                f"{self._base_url}auth/signin",
                self._login_and_password,
                self._headers
            )
            if 'data' in response:
                self._headers["Authorization"] = f'''Bearer {response['data']}'''
                await self._refresh_groups_list()
                await self._refresh_professors_list()
                await asyncio.sleep(59 * 60)
            else:
                print(response)
                await asyncio.sleep(5)

    async def get_status(self):
        response = await self._client.post(f"{self._base_url}auth/signin", self._login_and_password, self._headers)
        if 'description' in response:
            return f"{response['code']}: {response['description']}"
        else:
            return 'working'

    async def get_user_type(self, name: str):
        if name in (await self._get_id_by_professors_list()).keys():
            return "professor"
        elif name in (await self._get_id_by_groups_list()).keys():
            return "student"
        else:
            raise EmptyResponse(f"{name} not in groups/professors list.")

    async def _get_id_by_professors_list(self):
        if self._id_by_professors is None:
            await self._refresh_professors_list()
        return self._id_by_professors

    async def _refresh_professors_list(self):
        teachers = await self._client.get(self._base_url + "/teacher/v1", headers=self._headers)
        self._id_by_professors = {}
        for teacher in teachers:
            self._id_by_professors[teacher["fio"]] = teacher['id']

    async def _get_id_by_groups_list(self):
        if self._id_by_groups is None:
            await self._refresh_groups_list()
        return self._id_by_groups

    async def _refresh_groups_list(self):
        groups = await self._client.get(self._base_url + "/group/v1", headers=self._headers)
        self._id_by_groups = {}
        for group in groups:
            self._id_by_groups[group["title"]] = group['id']

    async def get_schedule_list_hash(self, name: str, start_date: str, last_date: str = None):
        return list(
            map(
                lambda schedule: {
                    "time": datetime.strptime(schedule['text'].split(', ')[1][0:10], "%d.%m.%Y"),
                    "hash": hashlib.sha256(schedule['text'].encode()).hexdigest()
                }, filter(
                    lambda schedule: len(schedule['text'].split(', ')) > 1,
                    await self.get_schedule_list_string(name, start_date, last_date)
                )
            )
        )

    async def get_schedule_list_string(self, name: str, start_date: str, last_date: str = None):
        return Schedule(
            await self.get_user_type(name),
            await self._get_schedule_json(name, start_date, last_date)
        )

    async def _get_schedule_json(self, name: str, start_date: str, last_date: str = None):
        response = await self._client.get(
            f"{self._base_url}/timetable/v1/"
            f"from/{start_date}/"
            f"to/{last_date or start_date}/"
            f"{(await self.get_user_type(name)).replace('student', 'groupId').replace('professor', 'lecturerId')}/"
            f"{await self._get_chsu_id(name)}/",
            headers=self._headers
        )
        if 'description' in response:
            raise ConnectionError(f"{response['code']}: {response['description']}")
        return response

    async def _get_chsu_id(self, name: str):
        return {
            **(await self._get_id_by_groups_list()),
            **(await self._get_id_by_professors_list())
        }[name]
