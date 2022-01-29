from Keyboards.abstract_keyboard import Keyboard


class TelegramKeyboard(Keyboard):
    def __init__(self):
        super().__init__()

    def _clear(self) -> None:
        self._keyboard = {'resize_keyboard': True, 'one_time_keyboard': True, 'keyboard': [], 'selective': True}

    def _add_line(self) -> None:
        self._keyboard['keyboard'].append([])

    def _add_button(self, text: str, color: str) -> None:
        self._keyboard['keyboard'][-1].append({"text": text})
