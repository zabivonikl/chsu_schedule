from json import dumps


class VkKeyboard:
    def __init__(self) -> None:
        self._line_count = 0
        self._keyboard = None

    def clear(self, one_time: bool = False, inline: bool = False) -> None:
        self._line_count = 0
        self._keyboard = {
            "one_time": one_time,
            "buttons": [],
            "inline": inline
        }

    def add_line(self) -> None:
        self._keyboard['buttons'].append([])
        self._line_count += 1

    def add_button(self, text: str, color: str = "primary") -> None:
        self._keyboard['buttons'][self._line_count - 1].append({
            "action": {
                "type": "text",
                "label": text
            },
            "color": color
        })

    def get_keyboard(self) -> str:
        return dumps(self._keyboard)
