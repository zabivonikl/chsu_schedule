from Keyboards.abstract_keyboard import Keyboard


class TelegramKeyboard(Keyboard):
    def __init__(self):
        super().__init__()
        self._keyboard_type = None

    def _clear(self, inline: bool = False) -> None:
        self._keyboard = {'resize_keyboard': True, 'one_time_keyboard': True, 'selective': True}
        if inline:
            self._keyboard_type = 'inline_keyboard'
        else:
            self._keyboard_type = 'keyboard'
        self._keyboard[self._keyboard_type] = []

    def _add_line(self) -> None:
        self._keyboard[self._keyboard_type].append([])

    def _add_button(self, text: str, color: str) -> None:
        self._keyboard[self._keyboard_type][-1].append({"text": text})

    def _add_payload_button(self, text: str, callback_data: str, color: str) -> None:
        self._keyboard[self._keyboard_type][-1].append({"text": text, "callback_data": callback_data})
