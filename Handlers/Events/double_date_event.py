from re import match

from APIs.Chsu.client import Chsu
from APIs.Chsu.schedule import Schedule
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
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

    @staticmethod
    async def _can_handle(event) -> bool:
        return match(
            r'^(0[1-9]|1\d|2\d|3[0-1])[.](0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1]).(0[1-9]|1[0-2])$', event['text']
        ) is not None

    async def _handle(self, event) -> None:
        self._date_handler.parse_date(event['text'])
        await self._handle_request(event['from_id'], self._date_handler.get_string())

    async def _handle_request(self, from_id, date):
        try:
            await self._send_messages([from_id], await self._get_schedule(from_id, *date))
            return
        except ValueError:
            text = "Введена некорректная дата."
        except MongoDBEmptyRespException:
            text = "Пользователь не найден. " \
                   "Пожалуйста, нажмите \"Изменить группу\" и введите номер группы/ФИО преподавателя снова."
        except ConnectionError as err:
            text = f"Произошла ошибка при запросе расписания: {err}. " \
                   f"Попробуйте запросить его снова или свяжитесь с администратором."
        await self._chat_platform.send_message(text, [from_id], self._keyboard.get_standard_keyboard())

    async def _get_schedule(self, from_id, start_date, last_date=None):
        self._id_by_professors = await self._chsu_api.get_id_by_professors_list()
        self._id_by_groups = await self._chsu_api.get_id_by_groups_list()

        db_response = await self._database.get_user_data(
            from_id, self._chat_platform.get_name(), self._date_handler.get_current_date_object()
        )
        university_id = \
            self._id_by_groups[db_response["group_name"]] \
            if "group_name" in db_response \
            else self._id_by_professors[db_response["professor_name"]]
        return await self._chsu_api.get_schedule_list_string(university_id, start_date, last_date)

    async def _send_messages(self, from_id, resp):
        for day in resp:
            await self._send_message(from_id, day)

    async def _send_message(self, from_id, day):
        kb = self._keyboard.get_standard_keyboard()
        addresses = list(set(filter(lambda x: x is not None, day['callback_data'])))
        if len(addresses) > 0:
            address_codes = list(map(lambda a: Schedule.get_address_code(a), addresses))
            kb = self._keyboard.get_geo_request_keyboard(addresses, address_codes)
        await self._chat_platform.send_message(day['text'], [from_id], kb)
