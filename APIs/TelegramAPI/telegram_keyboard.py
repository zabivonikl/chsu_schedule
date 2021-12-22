from json import dumps


class TelegramKeyboard:
    def __init__(self):
        self._line_count = 0
        self._keyboard_markup = None

    def add_line(self):
        self._keyboard_markup['keyboard'].append([])
        self._line_count += 1

    def add_button(self, text):
        self._keyboard_markup['keyboard'][self._line_count - 1].append({"text": text})

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


if __name__ == "__main__":
    kb = TelegramKeyboard()
    kb.add_line()
    kb.add_button("Расписание на сегодня")
    kb.add_button("Расписание на завтра")
    kb.add_line()
    kb.add_button("Расписание на другой день")
    kb.add_line()
    kb.add_button("Изменить группу")
    print(kb.get_keyboard())
    print(dumps({
        'resize_keyboard': True,
        'one_time_keyboard': True,
        'keyboard': [
            [
                {'text': 'Расписание на сегодня'},
                {'text': 'Расписание на завтра'}
            ], [
                {'text': 'Расписание на другой день'}
            ], [
                {'text': 'Изменить группу'}
            ]],
        'selective': False
    }))
    print(kb.get_keyboard() == dumps({
        'resize_keyboard': True,
        'one_time_keyboard': True,
        'keyboard': [
            [
                {'text': 'Расписание на сегодня'},
                {'text': 'Расписание на завтра'}
            ], [
                {'text': 'Расписание на другой день'}
            ], [
                {'text': 'Изменить группу'}
            ]],
        'selective': False
    }))
