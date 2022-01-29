from json import dumps

from Keyboards.keyboard import Keyboard


class TelegramKeyboard(Keyboard):
    def __init__(self):
        super().__init__()
        self._line_count = 0
        self._keyboard_markup = None

    def _add_line(self) -> None:
        self._keyboard_markup['keyboard'].append([])
        self._line_count += 1

    def _add_button(self, text: str, color: str) -> None:
        self._keyboard_markup['keyboard'][self._line_count - 1].append({"text": text})

    def _get_keyboard(self) -> str:
        return dumps(self._keyboard_markup)

    def _clear(self) -> None:
        self._line_count = 0
        self._keyboard_markup = {
            'resize_keyboard': True,
            'one_time_keyboard': True,
            'keyboard': [],
            'selective': True
        }
