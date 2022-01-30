import asyncio
from asyncio import AbstractEventLoop
from datetime import timedelta

from APIs.Chsu.client import Chsu
from APIs.Telegram.client import Telegram
from APIs.Vk.client import Vk
from Wrappers.MongoDb.database import MongoDB


class ScheduleChecker:
    def __init__(
            self,
            vk: Vk,
            telegram: Telegram,
            database: MongoDB,
            chsu_api: Chsu,
            event_loop: AbstractEventLoop,
            get_time
    ):
        self._vk = vk
        self._telegram = telegram
        self._database = database
        self._chsu_api = chsu_api
        self._get_time = get_time
        self.updating = event_loop.create_task(self._daily_updating_process())
        self.checking = event_loop.create_task(self._check_updates_process())

    def get_status(self):
        return 'working' if not self.updating.done() and not self.checking.done() else 'not working'

    async def _daily_updating_process(self):
        while True:
            try:
                await self._update_hashes()
            except ConnectionError as err:
                print(err)
            await asyncio.sleep(59)

    async def _update_hashes(self):
        if await self._is_midnight():
            group_list = await self._database.get_groups_list()
            ids = await self._get_id_list()
            for group in group_list:
                await self._update_group_and_get_changes(group, ids[group])

    async def _is_midnight(self):
        return self._get_time().hour == 0 and self._get_time().minute == 0

    async def _get_id_list(self):
        return {
            **(await self._chsu_api.get_id_by_groups_list()),
            **(await self._chsu_api.get_id_by_professors_list())
        }

    async def _update_group_and_get_changes(self, group_name, group_id):
        start_time = self._get_time().strftime("%d.%m.%Y")
        end_time = (self._get_time(0) + timedelta(days=14, hours=3)).strftime("%d.%m.%Y")
        new_hashes = await self._chsu_api.get_schedule_list_hash(group_id, start_time, end_time)
        group_obj = await self._database.get_group_hashes(group_name)
        await self._database.set_group_hashes(new_hashes, group_name)
        response = self._get_difference_dates(new_hashes, group_obj)
        return response

    def _get_difference_dates(self, hashes: list, group: dict) -> list:
        if 'hashes' in group:
            return self._get_difference_dates_and_update_hashes(group['hashes'], hashes)
        else:
            return []

    def _get_difference_dates_and_update_hashes(self, old_hashes: list, new_hashes: list) -> list:
        hashes = self._get_difference(old_hashes, new_hashes)
        objects = self._find_full_objects(hashes, new_hashes)
        return self._get_date_strings(objects)

    def _get_difference(self, old_hashes: list, new_hashes: list) -> list:
        return list(set(self._get_hashes(new_hashes)) - set(self._get_hashes(old_hashes)))

    @staticmethod
    def _get_hashes(dates_and_hashes: list) -> list:
        return list(map(lambda date_and_hash: date_and_hash['hash'], dates_and_hashes))

    @staticmethod
    def _find_full_objects(hashes: list, object_list: list) -> list:
        return list(filter(lambda date_hash: date_hash['hash'] in hashes, object_list))

    @staticmethod
    def _get_date_strings(object_list: list) -> list:
        return list(map(lambda date_and_hash: date_and_hash['time'].strftime("%d.%m.%Y"), object_list))

    async def _check_updates_process(self):
        while True:
            try:
                await self._check_updates()
            except ConnectionError as err:
                print(err)
            await asyncio.sleep(1)

    async def _check_updates(self):
        if await self.is_beginning_of_the_hour():
            group_list = await self._database.get_groups_list()
            ids = await self._get_id_list()
            for group in group_list:
                await self._check_and_send_updates_for_group(group, ids[group])

    async def is_beginning_of_the_hour(self):
        return self._get_time().second == 0 and self._get_time().hour != 0 and self._get_time().minute == 0

    async def _check_and_send_updates_for_group(self, group, group_id):
        users = await self._database.get_check_changes_members(group)
        response = await self._get_new_schedules(group, group_id)
        await self._send_response(users, response)

    async def _get_new_schedules(self, group, group_id):
        update_times = await self._update_group_and_get_changes(group, group_id) or []
        response = []
        for update_time in update_times:
            schedule = (await self._chsu_api.get_schedule_list_string(group_id, update_time))
            response += list(map(lambda day: f"Обновленное расписание:\n\n{day}", schedule))
        return response

    async def _send_response(self, users, response):
        for user in users:
            if user['platform'] == self._vk.get_name():
                api = self._vk
            else:
                api = self._telegram
            await api.send_message_queue(response, [user['id']], api.get_keyboard_inst().get_standard_keyboard())
