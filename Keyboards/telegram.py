from json import dumps


class TelegramKeyboard:
    def __init__(self):
        self._line_count = 0
        self._keyboard_markup = None

    def add_line(self):
        self._keyboard_markup['keyboard'].append([])
        self._line_count += 1

    def add_button(self, text, color):
        self._keyboard_markup['keyboard'][self._line_count - 1].append({"text": text})
        return color

    def get_keyboard(self):
        return dumps(self._keyboard_markup)

    def clear(self, resize_keyboard=True, one_time_keyboard=True, selective=False):
        self._line_count = 0
        self._keyboard_markup = {
            'resize_keyboard': resize_keyboard,
            'one_time_keyboard': one_time_keyboard,
            'keyboard': [],
            'selective': selective
        }
