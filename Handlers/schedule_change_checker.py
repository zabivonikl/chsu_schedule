import asyncio
import traceback
from asyncio import AbstractEventLoop

from APIs.Chsu.client import Chsu
from APIs.Chsu.schedule import Schedule
from APIs.Telegram.client import Telegram
from APIs.Vk.client import Vk
from Handlers.date_handler import DateHandler
from Wrappers.MongoDb.database import MongoDB
from Exceptions.empty_response import EmptyResponse


class ScheduleChecker:
    def __init__(
            self,
            vk: Vk,
            telegram: Telegram,
            database: MongoDB,
            chsu_api: Chsu,
            event_loop: AbstractEventLoop
    ):
        self._vk = vk
        self._telegram = telegram
        self._database = database
        self._chsu_api = chsu_api
        self._date_handler = DateHandler()
        self.checking = event_loop.create_task(self._check_updates_process())
        self._is_updated = True

    def get_status(self):
        return 'working' if not self.checking.done() else 'not working'

    async def _check_updates_process(self):
        while True:
            try:
                self._date_handler = DateHandler()
                await self._check_updates()
            except Exception as err:
                print(f"{err.__class__.__name__}: {err}")
                self._is_updated = False
            await asyncio.sleep(1)

    async def _check_updates(self):
        if await self._is_update_time():
            group_list = await self._database.get_groups_list()
            for group in group_list:
                await self._check_and_send_updates_for_group(group)
        self._is_updated = True

    async def _is_update_time(self):
        return \
            self._date_handler.get_current_date_object().second == 0 and \
            self._date_handler.get_current_date_object().hour != 0 and \
            self._date_handler.get_current_date_object().minute % 10 == 0

    async def _check_and_send_updates_for_group(self, group):
        users = await self._database.get_check_changes_members(group)
        response = await self._get_new_schedules(group)
        if not self._is_updated:
            await self._send_responses(users, response)

    async def _get_new_schedules(self, group):
        response = []
        for time in await self._update_group_and_get_changes(group) or []:
            for schedule in await self._chsu_api.get_schedule_list_string(group, time):
                response.append(
                    (f"Обновленное расписание:\n\n{schedule['text']}", schedule['callback_data'])
                )
        return response

    async def _update_group_and_get_changes(self, group_name):
        self._date_handler.parse_interval(days=14)
        try:
            new_hashes = await self._chsu_api.get_schedule_list_hash(group_name, *self._date_handler.get_string())
            group_obj = await self._database.get_group_hashes(group_name)
            await self._database.set_group_hashes(new_hashes, group_name)
            return list(filter(
                lambda x:
                not (
                    x == self._date_handler.get_string()[1] and
                    self._date_handler.get_current_date_object().hour == 0
                ),
                self._get_difference_dates(new_hashes, group_obj)
            ))
        except EmptyResponse as err:
            print(f"{err.__class__.__name__}: {err}")
            return []

    def _get_difference_dates(self, hashes: list, group: dict) -> list:
        return self._get_difference_dates_and_update_hashes(group['hashes'], hashes) if 'hashes' in group else []

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

    async def _send_responses(self, users, response):
        for message in response:
            await self._send_response(
                self._vk,
                list(map(lambda u: u["id"], filter(lambda u: u['platform'] == self._vk.get_name(), users))),
                message
            )
            await self._send_response(
                self._telegram,
                list(map(lambda u: u["id"], filter(lambda u: u['platform'] == self._telegram.get_name(), users))),
                message
            )

    @staticmethod
    async def _send_response(api, users, message):
        await api.send_message(
            message[0],
            users,
            api.get_keyboard_inst().get_geo_request_keyboard(
                message[1],
                list(map(
                    lambda a: Schedule.get_address_code(a),
                    message[1]
                ))
            )
        )
