from Keyboards.telegram import TelegramKeyboard
from Keyboards.vk import VkKeyboard


class Keyboard:
    def __init__(self, api_name) -> None:
        self._line_count = 0
        if api_name == "vk":
            self._keyboard = VkKeyboard()
        elif api_name == 'telegram':
            self._keyboard = TelegramKeyboard()

    def get_standard_keyboard(self) -> str:
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_button("Расписание на сегодня", "primary")
        self._keyboard.add_button("Расписание на завтра", "primary")
        self._keyboard.add_line()
        self._keyboard.add_button("Расписание на другой день", "secondary")
        self._keyboard.add_line()
        self._keyboard.add_button("Настройки", "negative")
        return self._keyboard.get_keyboard()

    def get_start_keyboard(self) -> str:
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_button("Преподаватель", "primary")
        self._keyboard.add_button("Студент", "primary")
        return self._keyboard.get_keyboard()

    def get_change_group_keyboard(self):
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_button("Преподаватель", "primary")
        self._keyboard.add_button("Студент", "primary")
        self._keyboard.add_line()
        self._keyboard.add_button("Отмена", "negative")
        return self._keyboard.get_keyboard()

    def get_canceling_keyboard(self) -> str:
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_button("Отмена", "negative")
        return self._keyboard.get_keyboard()

    def get_canceling_subscribe_keyboard(self) -> str:
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_button("Отмена", "secondary")
        self._keyboard.add_line()
        self._keyboard.add_button("Отписаться", "negative")
        return self._keyboard.get_keyboard()

    def get_settings_keyboard(self) -> str:
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_button("Рассылка", "positive")
        self._keyboard.add_button("Изменения в расписании", "positive")
        self._keyboard.add_line()
        self._keyboard.add_button("Изменить группу", "negative")
        self._keyboard.add_button("Отмена", "secondary")
        return self._keyboard.get_keyboard()

    def get_set_check_changes_keyboard(self) -> str:
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_button("Отслеживать изменения", "positive")
        self._keyboard.add_button("Не отслеживать изменения", "negative")
        return self._keyboard.get_keyboard()

    @staticmethod
    def get_empty_keyboard():
        return None
