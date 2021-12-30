from datetime import timedelta, datetime
from re import match

from Wrappers.MongoDb.exceptions import EmptyResponse as MongoDBEmptyRespException


class EventHandler:
    def __init__(self, api, database, chsu_api):
        self._chat_platform = api
        self._database = database
        self._chsu_api = chsu_api
        self._keyboard = None

        self._id_by_professors = None
        self._id_by_groups = None

        self._current_date = None

    async def handle_event(self, event):
        self._current_date = event['time']
        self._id_by_professors = await self._chsu_api.get_id_by_professors_list()
        self._id_by_groups = await self._chsu_api.get_id_by_groups_list()
        self._keyboard = await self._chat_platform.get_keyboard_inst()

        if event['text'] not in ['Начать', "/start"]:
            await self._handle_change_group(event)
        else:
            kb = self._keyboard.get_start_keyboard()
            await self._chat_platform.send_message("Кто вы?", [event['from_id']], kb)

    async def _handle_change_group(self, event):
        if event['text'] != "Изменить группу":
            await self._handle_message_to_admin(event)
        else:
            kb = self._keyboard.get_change_group_keyboard()
            await self._chat_platform.send_message("Кто вы?", [event['from_id']], kb)

    async def _handle_message_to_admin(self, event):
        if event['text'] and event['text'][0] != ';':
            await self._handle_choice_professor(event)
        else:
            kb = self._keyboard.get_standard_keyboard()
            await self._chat_platform.send_message(
                f"Сообщение от пользователя: {event['text'][1:]}\n\n"
                f"Для ответа используйте \"!{event['from_id']}: %сообщение%\".",
                self._chat_platform.get_admins(), kb
            )
            await self._chat_platform.send_message(f"Сообщение отправлено.", [event['from_id']], kb)

    async def _handle_choice_professor(self, event):
        if event['text'] != 'Преподаватель':
            await self._handle_choice_group(event)
        else:
            kb = self._keyboard.get_empty_keyboard()
            await self._chat_platform.send_message(f"Введите ФИО.", [event['from_id']], kb)

    async def _handle_choice_group(self, event):
        if event['text'] != 'Студент':
            await self._handle_schedule_for_another_day(event)
        else:
            kb = self._keyboard.get_empty_keyboard()
            await self._chat_platform.send_message(f"Введите номер группы.", [event['from_id']], kb)

    async def _handle_schedule_for_another_day(self, event):
        if event['text'] != "Расписание на другой день":
            await self._handle_cancel(event)
        else:
            kb = self._keyboard.get_canceling_keyboard()
            text = "Введите дату:\nПример: 08.02 - запрос расписания для конкретного дня.\n" \
                   "31.10-07.11 - запрос расписания для заданного интервала дат."
            await self._chat_platform.send_message(text, [event['from_id']], kb)

    async def _handle_cancel(self, event):
        if event['text'] != "Отмена":
            await self._handle_mailing(event)
        else:
            kb = self._keyboard.get_standard_keyboard()
            await self._chat_platform.send_message(f"Действие отменено.", [event['from_id']], kb)

    async def _handle_mailing(self, event):
        if event['text'] != "Рассылка":
            await self._handle_time_stamp(event)
        else:
            kb = self._keyboard.get_canceling_subscribe_keyboard()
            text = "Введите время рассылки\nПример: 08:36"
            await self._chat_platform.send_message(text, [event['from_id']], kb)

    async def _handle_time_stamp(self, event):
        if not match(r'^(0\d|1\d|2[0-3])[:][0-5]\d$', event['text']):
            await self._handle_unsubscribe(event)
        else:
            await self._database.update_mailing_time(
                event['from_id'], self._chat_platform.get_api_name(), event['text']
            )
            text = f"Вы подписались на рассылку расписания. Теперь, ежедневно в {event['text']}, " \
                   f"Вы будете получать расписание на следующий день."
            kb = self._keyboard.get_standard_keyboard()
            await self._chat_platform.send_message(text, [event['from_id']], kb)

    async def _handle_unsubscribe(self, event):
        if event['text'] != "Отписаться":
            await self._handle_settings(event)
        else:
            await self._database.update_mailing_time(event['from_id'], self._chat_platform.get_api_name())
            kb = self._keyboard.get_standard_keyboard()
            await self._chat_platform.send_message(f"Вы отписались от рассылки.", [event['from_id']], kb)

    async def _handle_settings(self, event):
        if event['text'] != "Настройки":
            await self._handle_subscribe_on_changes(event)
        else:
            kb = self._keyboard.get_settings_keyboard()
            await self._chat_platform.send_message(
                f"Настройки.", [event['from_id']], kb
            )

    async def _handle_subscribe_on_changes(self, event):
        if event['text'] != "Изменения в расписании":
            await self._handle_set_check_changes(event)
        else:
            kb = self._keyboard.get_set_check_changes_keyboard()
            await self._chat_platform.send_message(
                f"Изменения.\n\n"f"Отслеживание изменений - экспериментальная "
                f"функция", [event['from_id']], kb
            )

    async def _handle_set_check_changes(self, event):
        if event['text'] != "Отслеживать изменения":
            await self._handle_set_dont_check_changes(event)
        else:
            await self._database.update_check_changes(event['from_id'], self._chat_platform.get_api_name(), True)
            kb = self._keyboard.get_standard_keyboard()
            await self._chat_platform.send_message(
                f"Теперь ежечасно вам будут приходить уведомления о изменениях "
                f"в расписании, если они будут.", [event['from_id']], kb
            )

    async def _handle_set_dont_check_changes(self, event):
        if event['text'] != "Не отслеживать изменения":
            await self._handle_group_or_professor_name(event)
        else:
            await self._database.update_check_changes(event['from_id'], self._chat_platform.get_api_name())
            kb = self._keyboard.get_standard_keyboard()
            await self._chat_platform.send_message(
                f"Вам больше не будут приходить уведомления о изменениях в расписании,"
                f" однако их всегда можно включить в настройках.", [event['from_id']], kb
            )

    async def _handle_group_or_professor_name(self, event):
        if event['text'] not in {**self._id_by_groups, **self._id_by_professors}:
            await self._handle_double_date(event)
        else:
            if event['text'] in self._id_by_professors:
                await self._database.set_user_data(
                    event['from_id'], self._chat_platform.get_api_name(), professor_name=event['text']
                )
            else:
                await self._database.set_user_data(
                    event['from_id'], self._chat_platform.get_api_name(), group_name=event['text']
                )
            kb = self._keyboard.get_standard_keyboard()
            await self._chat_platform.send_message("Данные сохранены.\n", [event['from_id']], kb)

    async def _handle_double_date(self, event):
        regex = r'^(0[1-9]|1\d|2\d|3[0-1])[.](0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1]).(0[1-9]|1[0-2])$'
        if not match(regex, event['text']):
            await self._handle_date(event)
        else:
            await self._handle_custom_date(event['from_id'], event['text'].split('-')[0], event['text'].split('-')[1])

    async def _handle_date(self, event):
        if not match(r'^(0[1-9]|1\d|2\d|3[0-1])[.](0[1-9]|1[0-2])$', event['text']):
            await self._handle_schedule_for_today(event)
        else:
            await self._handle_custom_date(event['from_id'], event['text'])

    async def _handle_schedule_for_today(self, event):
        if event['text'] != "Расписание на сегодня":
            await self._handle_schedule_for_tomorrow(event)
        else:
            event['text'] = self._current_date.strftime('%d.%m')
            await self._handle_date(event)

    async def _handle_schedule_for_tomorrow(self, event):
        if event['text'] != "Расписание на завтра":
            await self._send_message_from_admin(event)
        else:
            event['text'] = (self._current_date + timedelta(days=1)).strftime('%d.%m')
            await self._handle_date(event)

    async def _send_message_from_admin(self, event):
        if len(event['text']) == 0 or event['text'][0] != "!":
            await self._handle_another_events(event)

        else:
            to_id = int(event['text'].split(':')[0][1:])
            message = event['text'].split(':')[1]
            kb = self._keyboard.get_standard_keyboard()
            await self._chat_platform.send_message(
                f"Сообщение отправлено",
                [event['from_id']], kb
            )
            await self._chat_platform.send_message(
                f"Сообщение от администратора: {message}\n\n"
                f"Для ответа используйте \";\" в начале сообщения.", [to_id], kb
            )

    async def _handle_another_events(self, event):
        kb = self._keyboard.get_standard_keyboard()
        await self._chat_platform.send_message(
            "Такой команды нет. Проверьте правильность ввода.", [event['from_id']], kb
        )

    async def _handle_custom_date(self, from_id, start_date, end_date=None):
        dates = self._get_full_date(start_date, end_date)
        resp = await self._get_schedule(from_id, dates[0], dates[1])
        kb = self._keyboard.get_standard_keyboard()
        await self._chat_platform.send_message_queue(resp, [from_id], kb)

    def _get_full_date(self, initial_date_string, final_date_string=None):
        initial_date = self._parse_date_string(initial_date_string)
        if self._is_date_less_current(initial_date):
            initial_date = self._add_year(initial_date)
        if final_date_string:
            final_date = self._parse_date_string(final_date_string)
            if self._is_final_date_less(final_date, initial_date):
                final_date = self._add_year(final_date)
            return [initial_date.strftime("%d.%m.%Y"), final_date.strftime("%d.%m.%Y")]
        else:
            return [initial_date.strftime("%d.%m.%Y"), None]

    def _parse_date_string(self, string):
        return datetime.strptime(f"{string}.{self._current_date.year}", "%d.%m.%Y")

    def _is_date_less_current(self, date):
        return (date - self._current_date.replace(tzinfo=None)).days < 0 and date.month <= 6

    @staticmethod
    def _is_final_date_less(final_date, initial_date):
        return (final_date - initial_date).days < 0

    @staticmethod
    def _add_year(date):
        return datetime(year=date.year + 1, month=date.month, day=date.day)

    async def _get_schedule(self, from_id, start_date, last_date=None):
        try:
            db_response = await self._database.get_user_data(
                from_id, self._chat_platform.get_api_name(), self._current_date
            )
            university_id = int(
                self._id_by_groups[db_response["group_name"]] if "group_name" in db_response
                else self._id_by_professors[db_response["professor_name"]]
            )
            return await self._chsu_api.get_schedule_list_string(university_id, start_date, last_date)
        except ConnectionError as err:
            kb = self._keyboard.get_standard_keyboard()
            await self._chat_platform.send_message(
                f"У {from_id} произошла ошибка {err}.", self._chat_platform.get_admins(), kb
            )
            return [
                f"Произошла ошибка при запросе расписания: {err}. "
                f"Попробуйте запросить его снова или свяжитесь с администратором."
            ]
        except MongoDBEmptyRespException:
            return [
                "Пользователь не найден. "
                "Пожалуйста, нажмите \"Изменить группу\" и введите номер группы/ФИО преподавателя снова."
            ]
        