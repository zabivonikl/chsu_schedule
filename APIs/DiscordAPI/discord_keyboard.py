from json import dumps


class DiscordKeyboard:
    def __init__(self, one_time=False):
        self._line_count = 0

        self._keyboard = []

    def add_line(self):
        self._keyboard['buttons'].append([])
        self._line_count += 1

    def add_text_button(self, text: str, color: str = "primary"):
        self._keyboard['buttons'][self._line_count - 1].append({
            "action": {
                "type": "text",
                "label": text
            },
            "color": color
        })

    def get_keyboard(self):
        return dumps(self._keyboard)
