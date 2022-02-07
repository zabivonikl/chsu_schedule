from json import dumps


class Keyboard:
    def __init__(self) -> None:
        self._keyboard = None

    def get_standard_keyboard(self) -> str:
        self._clear()
        self._add_line()
        self._add_button("Расписание на сегодня", "primary")
        self._add_button("Расписание на завтра", "primary")
        self._add_line()
        self._add_button("Расписание на другой день", "secondary")
        self._add_line()
        self._add_button("Настройки", "negative")
        return self._get_keyboard()

    def get_start_keyboard(self) -> str:
        self._clear()
        self._add_line()
        self._add_button("Преподаватель", "primary")
        self._add_button("Студент", "primary")
        return self._get_keyboard()

    def get_change_group_keyboard(self):
        self._clear()
        self._add_line()
        self._add_button("Преподаватель", "primary")
        self._add_button("Студент", "primary")
        self._add_line()
        self._add_button("Отмена", "negative")
        return self._get_keyboard()

    def get_canceling_keyboard(self) -> str:
        self._clear()
        self._add_line()
        self._add_button("Отмена", "negative")
        return self._get_keyboard()

    def get_canceling_subscribe_keyboard(self) -> str:
        self._clear()
        self._add_line()
        self._add_button("Отмена", "secondary")
        self._add_line()
        self._add_button("Отписаться", "negative")
        return self._get_keyboard()

    def get_settings_keyboard(self) -> str:
        self._clear()
        self._add_line()
        self._add_button("Рассылка", "positive")
        self._add_button("Изменения в расписании", "positive")
        self._add_line()
        self._add_button("Изменить группу", "negative")
        self._add_button("Отмена", "secondary")
        return self._get_keyboard()

    def get_set_check_changes_keyboard(self) -> str:
        self._clear()
        self._add_line()
        self._add_button("Отслеживать изменения", "positive")
        self._add_button("Не отслеживать изменения", "negative")
        return self._get_keyboard()

    def get_geo_request_keyboard(self, text: list, payloads: list):
        self._clear(True)
        for index in range(len(text)):
            if text[index]:
                self._add_line()
                self._add_payload_button(text[index], payloads[index], "primary")
        return self._get_keyboard()

    @staticmethod
    def get_empty_keyboard():
        return None

    def _clear(self, inline: bool = False) -> None:
        pass

    def _add_line(self) -> None:
        pass

    def _add_button(self, text: str, color: str) -> None:
        pass

    def _add_payload_button(self, text: str, callback_data: str, color: str) -> None:
        pass

    def _get_keyboard(self) -> str:
        return dumps(self._keyboard)
