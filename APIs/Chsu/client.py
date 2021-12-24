from APIs.Chsu.exceptions import InvalidChsuId, InvalidApiKey
from Wrappers.AIOHttp.aiohttp import AIOHttpWrapper


class Chsu:
    def __init__(self, event_loop):
        self._client = AIOHttpWrapper(event_loop)
        self._base_url = "http://api.chsu.ru/api/"
        self._base_headers = {
            "Content-Type": "application/json",
            "charset": "utf-8"
        }

        self._login_and_password = {
            "username": "mobil",
            "password": "ds3m#2nn"
        }

        self._id_by_professors = None
        self._professors_by_id = None

        self._id_by_groups = None
        self._groups_by_id = None

    async def get_status(self):
        response = await self._client.post(f"{self._base_url}auth/signin", self._login_and_password, self._base_headers)
        return response['error'] or 'working'

    async def get_id_by_professors_list(self):
        if self._id_by_professors is None:
            await self._set_new_token()
            teachers = await self._get_teachers_list()
            self._id_by_professors = {}
            for teacher in teachers:
                self._id_by_professors[teacher["fio"]] = teacher['id']
        return self._id_by_professors

    async def get_professors_by_id_list(self):
        if self._professors_by_id is None:
            await self._set_new_token()
            teachers = await self._get_teachers_list()
            self._professors_by_id = {}
            for teacher in teachers:
                self._professors_by_id[teacher["id"]] = teacher['fio']
        return self._professors_by_id

    async def _get_teachers_list(self):
        return await self._client.get(self._base_url + "/teacher/v1", headers=self._base_headers)

    async def get_id_by_groups_list(self):
        if self._id_by_groups is None:
            await self._set_new_token()
            groups = await self._get_groups_list()
            self._id_by_groups = {}
            for group in groups:
                self._id_by_groups[group["title"]] = group['id']
        return self._id_by_groups

    async def get_groups_by_id_list(self):
        if self._groups_by_id is None:
            await self._set_new_token()
            groups = await self._get_groups_list()
            self._groups_by_id = {}
            for group in groups:
                self._groups_by_id[group["id"]] = group['title']
        return self._groups_by_id

    async def _get_groups_list(self):
        return await self._client.get(self._base_url + "/group/v1", headers=self._base_headers)

    async def get_schedule(self, university_id, start_date, last_date=None):
        await self._set_new_token()
        if university_id in await self.get_groups_by_id_list():
            query = f"/timetable/v1/from/{start_date}/to/{last_date or start_date}/groupId/{university_id}/"
        elif university_id in await self.get_professors_by_id_list():
            query = f"/timetable/v1/from/{start_date}/to/{last_date or start_date}/lecturerId/{university_id}/"
        else:
            raise InvalidChsuId
        return await self._client.get(self._base_url + query, headers=self._base_headers)

    async def _set_new_token(self):
        token = (await self._client.post(
            f"{self._base_url}auth/signin",
            self._login_and_password,
            self._base_headers
        ))['data']
        if token is None:
            raise InvalidApiKey
        self._base_headers["Authorization"] = f'''Bearer {token}'''
