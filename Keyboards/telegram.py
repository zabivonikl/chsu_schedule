from Keyboards.abstract_keyboard import Keyboard


class TelegramKeyboard(Keyboard):
    def __init__(self):
        super().__init__()
        self._line_count = 0

    def _add_line(self) -> None:
        self._keyboard['keyboard'].append([])
        self._line_count += 1

    def _add_button(self, text: str, color: str) -> None:
        self._keyboard['keyboard'][self._line_count - 1].append({"text": text})

    def _clear(self) -> None:
        self._line_count = 0
        self._keyboard = {
            'resize_keyboard': True,
            'one_time_keyboard': True,
            'keyboard': [],
            'selective': True
        }
