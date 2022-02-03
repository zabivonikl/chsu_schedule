import asyncio
import hashlib
from asyncio import AbstractEventLoop
from datetime import datetime
from re import match

from APIs.Chsu.schedule import Schedule
from Wrappers.AIOHttp.aiohttp import AIOHttpWrapper


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
            if "Authorization" in self._headers:
                self._headers.pop("Authorization")
            response = await self._client.post(
                f"{self._base_url}auth/signin",
                self._login_and_password,
                self._headers
            )
            if 'data' in response:
                self._headers["Authorization"] = f'''Bearer {response['data']}'''
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

    async def get_id_by_professors_list(self):
        if self._id_by_professors is None:
            teachers = await self._client.get(self._base_url + "/teacher/v1", headers=self._headers)
            self._id_by_professors = {}
            for teacher in teachers:
                self._id_by_professors[teacher["fio"]] = teacher['id']
        return self._id_by_professors

    async def get_id_by_groups_list(self):
        if self._id_by_groups is None:
            groups = await self._client.get(self._base_url + "/group/v1", headers=self._headers)
            self._id_by_groups = {}
            for group in groups:
                self._id_by_groups[group["title"]] = group['id']
        return self._id_by_groups

    async def get_user_type(self, chsu_id: str):
        return "student" if chsu_id in (await self.get_id_by_groups_list()).values() else "professor"

    async def get_schedule_list_hash(self, university_id: str, start_date: str, last_date: str = None):
        response = []
        schedules = await self.get_schedule_list_string(university_id, start_date, last_date)
        for schedule in schedules:
            if not match(r'\d{2}.\d{2}.\d{4}', schedule.split(', ')[1][0:10]):
                print(schedule.split(', ')[1][0:10])
            else:
                response.append({
                    "time": datetime.strptime(schedule.split(', ')[1][0:10], "%d.%m.%Y"),
                    "hash": hashlib.sha256(schedule.encode()).hexdigest()
                })
        return response

    async def get_schedule_list_string(self, university_id: str, start_date: str, last_date: str = None):
        return Schedule(
            await self.get_user_type(university_id),
            await self._get_schedule_json(university_id, start_date, last_date)
        )

    async def _get_schedule_json(self, university_id: str, start_date: str, last_date: str = None):
        user_type = "groupId" if await self.get_user_type(university_id) == "student" else "lecturerId"
        query = f"/timetable/v1/from/{start_date}/to/{last_date or start_date}/{user_type}/{university_id}/"
        response = await self._client.get(self._base_url + query, headers=self._headers)
        if 'description' in response:
            raise ConnectionError(f"{response['code']}: {response['description']}")
        return response
