from Keyboards.abstract_keyboard import Keyboard


class VkKeyboard(Keyboard):
    def __init__(self) -> None:
        super().__init__()

    def _clear(self, inline: bool = False) -> None:
        self._keyboard = {"one_time": False, "buttons": [], "inline": inline}

    def _add_line(self) -> None:
        self._keyboard['buttons'].append([])

    def _add_button(self, text: str, color: str) -> None:
        self._keyboard['buttons'][-1].append({"action": {"type": "text", "label": text}, "color": color})

    def _add_payload_button(self, text: str, callback_data: str, color: str) -> None:
        self._keyboard['buttons'][-1].append({
            "action": {
                "type": "callback",
                "label": text,
                "payload": {"address": callback_data}
            },
            "color": color
        })
