import asyncio
from datetime import timedelta

from Keyboards.keyboards import Keyboards


class ScheduleChecker:
    def __init__(self, vk, telegram, database, chsu_api, event_loop, get_time):
        self._vk = vk
        self._telegram = telegram
        self._database = database
        self._chsu_api = chsu_api
        self._get_time = get_time
        event_loop.create_task(self._daily_updating())
        event_loop.create_task(self._check_updates())

    async def _daily_updating(self):
        while True:
            if await self._is_midnight():
                group_list = await self._database.get_groups_list()
                ids = await self._get_id_list()
                for group in group_list:
                    await self._update_group_and_get_changes(group, ids[group])
            await asyncio.sleep(59 * 60)

    async def _is_midnight(self):
        return self._get_time().hour == 0

    async def _get_id_list(self):
        return {
            **(await self._chsu_api.get_id_by_groups_list()),
            **(await self._chsu_api.get_id_by_professors_list())
        }

    async def _update_group_and_get_changes(self, group_name, group_id):
        start_time = self._get_time().strftime("%d.%m.%Y")
        end_time = (self._get_time(0) + timedelta(days=14, hours=3)).strftime("%d.%m.%Y")
        hash_list = await self._chsu_api.get_schedule_list_hash(group_id, start_time, end_time)
        return await self._database.get_update_schedule_hashes(hash_list, group_name)

    async def _check_updates(self):
        while True:
            if await self._is_beginning_of_the_minute():
                group_list = await self._database.get_groups_list()
                ids = await self._get_id_list()
                for group in group_list:
                    await self._check_and_send_updates_for_group(group, ids[group])
            await asyncio.sleep(1)

    async def _is_beginning_of_the_minute(self):
        return self._get_time().second == 0

    async def _check_and_send_updates_for_group(self, group, group_id):
        users = await self._database.get_check_changes_members(group)
        for user in users:
            response = await self._get_new_schedules(group, group_id)
            kb = Keyboards(user['platform']).get_standard_keyboard()
            if user['platform'] == "vk":
                await self._vk.send_message_queue(response, [user['id']], kb)
            elif user['platform'] == "telegram":
                await self._telegram.send_message_queue(response, [user['id']], kb)

    async def _get_new_schedules(self, group, group_id):
        update_times = await self._update_group_and_get_changes(group, group_id) or []
        response = []
        for update_time in update_times:
            schedule = (await self._chsu_api.get_schedule_list_string(group_id, update_time))
            response += list(map(lambda day: f"Обновлённое расписание:\n\n{day}", schedule))
        return response
