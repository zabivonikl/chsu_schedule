from re import match

from APIs.Chsu.client import Chsu
from APIs.Chsu.schedule import Schedule
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Handlers.date_handler import DateHandler
from Wrappers.MongoDb.database import MongoDB
from Wrappers.MongoDb.exceptions import EmptyResponse as MongoDBEmptyRespException


class DoubleDateHandler(AbstractHandler):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)
        self._date_handler = DateHandler()

    @staticmethod
    async def _can_handle(event) -> bool:
        return match(
            r'^(0[1-9]|1\d|2\d|3[0-1])[.](0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1]).(0[1-9]|1[0-2])$', event['text']
        ) is not None

    async def _handle(self, event) -> None:
        self._date_handler.parse_double_date(event['text'])
        await self._send_schedule(
            [event['from_id']], await self._get_schedule(event['from_id'], *self._date_handler.get_string())
        )

    async def _get_schedule(self, from_id, start_date, last_date=None):
        self._id_by_professors = await self._chsu_api.get_id_by_professors_list()
        self._id_by_groups = await self._chsu_api.get_id_by_groups_list()

        try:
            db_response = await self._database.get_user_data(
                from_id, self._chat_platform.get_name(), self._date_handler.get_current_date_object()
            )
            university_id = self._id_by_groups[db_response["group_name"]] if "group_name" in db_response \
                else self._id_by_professors[db_response["professor_name"]]
            return await self._chsu_api.get_schedule_list_string(university_id, start_date, last_date)
        except ConnectionError as err:
            return [
                f"Произошла ошибка при запросе расписания: {err}. "
                f"Попробуйте запросить его снова или свяжитесь с администратором."
            ]
        except MongoDBEmptyRespException:
            return [
                "Пользователь не найден. "
                "Пожалуйста, нажмите \"Изменить группу\" и введите номер группы/ФИО преподавателя снова."
            ]

    async def _send_schedule(self, from_id, resp):
        for day in resp:
            addresses = list(set(filter(lambda x: x is not None, day['callback_data'])))
            if len(addresses) > 0:
                address_codes = list(map(lambda a: Schedule.get_address_code(a), addresses))
                kb = self._keyboard.get_geo_request_keyboard(addresses, address_codes)
            else:
                kb = self._keyboard.get_standard_keyboard()
            await self._chat_platform.send_message(day['text'], [from_id], kb)
