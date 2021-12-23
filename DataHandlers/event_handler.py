from datetime import timedelta
from re import match

from APIs.MongoDbAPI.mongo_db_exceptions import EmptyResponse as MongoDBEmptyRespException
from DataHandlers.schedule_parser import ScheduleParser


class EventHandler:
    def __init__(self, api, database, chsu_api):
        self._chat_platform = api
        self._database = database
        self._schedule = ScheduleParser()
        self._chsu_api = chsu_api

        self._standard_kb = self._chat_platform.get_standard_keyboard()
        self._start_kb = self._chat_platform.get_start_keyboard()
        self._empty_kb = self._chat_platform.get_empty_keyboard()
        self._canceling_kb = self._chat_platform.get_canceling_keyboard()

        self._id_by_professors = None
        self._id_by_groups = None

        self._current_date = None

    async def handle_event(self, event_obj, date):
        self._id_by_professors = await self._chsu_api.get_id_by_professors_list()
        self._id_by_groups = await self._chsu_api.get_id_by_groups_list()

        self._current_date = date
        from_id = event_obj['from_id']
        text = event_obj['text']

        if text == 'Начать' or text == "/start" or text == "Изменить группу":
            await self._chat_platform.send_message("Кто вы?", [from_id], self._start_kb)
        elif text[0] == ';':
            await self._send_message_to_admins(text[1:], from_id)
        elif text == 'Преподаватель':
            await self._chat_platform.send_message(f"Введите ФИО", [from_id], self._empty_kb)
        elif text == 'Студент':
            await self._chat_platform.send_message(f"Введите номер группы", [from_id], self._empty_kb)
        elif text in self._id_by_groups or text in self._id_by_professors:
            await self._set_user_data(text, from_id)
        elif text == "Расписание на сегодня":
            resp = await self._get_schedule(from_id, f"{self._current_date.strftime('%d.%m.%Y')}")
            await self._chat_platform.send_message_queue(resp, [from_id], self._standard_kb)
        elif text == "Расписание на завтра":
            resp = await self._get_schedule(from_id, f"{(self._current_date + timedelta(days=1)).strftime('%d.%m.%Y')}")
            await self._chat_platform.send_message_queue(resp, [from_id], self._standard_kb)
        elif text == "Расписание на другой день":
            await self._chat_platform.send_message(
                "Введите дату\n"
                "\n"
                "Пример: 08.02 - запрос расписания для конкретного дня\n"
                "31.10-07.11 - запрос расписания для заданного интервала дат",
                [from_id],
                self._canceling_kb
            )
        elif match(r'^(0[1-9]|1\d|2\d|3[0-1])[.](0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1]).(0[1-9]|1[0-2])$', text):
            await self._handle_custom_date(from_id, text.split('-')[0], text.split('-')[1])
        elif match(r'^(0[1-9]|1\d|2\d|3[0-1])[.](0[1-9]|1[0-2])$', text):
            await self._handle_custom_date(from_id, text)
        elif text == "Отмена":
            await self._chat_platform.send_message(f"Действие отменено", [from_id], self._standard_kb)
        elif text == "Рассылка":
            await self._send_mailing_info(from_id)
        elif text == "Отписаться":
            await self._delete_mailing_time(from_id)
        elif match(r'^(0\d|1\d|2[0-3])[:][0-5]\d$', text):
            await self._set_mailing_time(from_id, text)
        else:
            await self._chat_platform.send_message(
                "Такой команды нет. Проверьте правильность ввода.", [from_id], self._standard_kb
            )

    async def _send_message_to_admins(self, message, from_id):
        await self._chat_platform.send_message(
            f"Сообщение в https://vk.com/gim207896794?sel={from_id}: {message}",
            self._chat_platform.get_admins(), self._standard_kb)
        await self._chat_platform.send_message(f"Сообщение отправлено", [from_id], self._standard_kb)

    async def _set_user_data(self, university_id, from_id):
        if university_id in self._id_by_professors:
            await self._database.set_user_data(
                from_id,
                self._chat_platform.get_api_name(),
                professor_name=university_id
            )
        elif university_id in self._id_by_groups:
            await self._database.set_user_data(
                from_id,
                self._chat_platform.get_api_name(),
                group_name=university_id
            )
        await self._chat_platform.send_message("Данные сохранены\n", [from_id], self._standard_kb)

    async def _handle_custom_date(self, from_id, start_date, end_date=None):
        dates = self.__get_full_date(start_date, end_date)
        resp = await self._get_schedule(from_id, dates[0], dates[1])
        await self._chat_platform.send_message_queue(resp, [from_id], self._standard_kb)

    def __get_full_date(self, start_date_string, end_date_string=None):
        start_date = start_date_string.split('-')[0] + f".{self._current_date.year}"
        end_date = None
        if end_date_string:
            if int(end_date_string[3:5]) < int(start_date_string[3:5]):
                end_date = end_date_string + f".{self._current_date.year + 1}"
            else:
                end_date = end_date_string + f".{self._current_date.year}"

        return [start_date, end_date]

    async def _get_schedule(self, from_id, start_date, last_date=None):
        try:
            db_response = await self._database.get_user_data(
                from_id, self._chat_platform.get_api_name(), self._current_date
            )
            if "group_name" in db_response:
                response = await self._chsu_api.get_schedule(
                    university_id=int(self._id_by_groups[db_response["group_name"]]),
                    start_date=start_date,
                    last_date=last_date
                )
                if response:
                    return self._schedule.parse_json("student", response)
                else:
                    return self._schedule.get_empty_response()
            else:
                response = await self._chsu_api.get_schedule(
                    university_id=int(self._id_by_professors[db_response["professor_name"]]),
                    start_date=start_date,
                    last_date=last_date
                )
                if response:
                    return self._schedule.parse_json("professor", response)
                else:
                    return self._schedule.get_empty_response()
        except MongoDBEmptyRespException:
            return [
                "Пользователь не найден. "
                "Пожалуйста, нажмите \"Изменить группу\" и введите номер группы/ФИО преподавателя снова."
            ]

    async def _delete_mailing_time(self, from_id):
        await self._database.update_mailing_time(from_id, self._chat_platform.get_api_name())
        await self._chat_platform.send_message(
            f"Вы отписались от рассылки.",
            [from_id],
            self._standard_kb
        )

    async def _set_mailing_time(self, from_id, text):
        await self._database.update_mailing_time(from_id, self._chat_platform.get_api_name(), text)
        await self._chat_platform.send_message(
            f"Вы подписались на рассылку расписания."
            f" Теперь, ежедневно в {text}, Вы будете получать расписание на следующий день.",
            [from_id],
            self._standard_kb
        )

    async def _send_mailing_info(self, from_id):
        await self._chat_platform.send_message(
            "Введите время рассылки\n"
            "Пример: 08:36\n"
            "\n"
            "Для отписки напишите \"Отписаться\" (соблюдая регистр).",
            [from_id], self._canceling_kb)
