from random import randint

from aiovk import TokenSession, API
from aiovk.drivers import HttpDriver
from aiovk.exceptions import VkAPIError

from APIs.Vk.keyboard import VkKeyboard


class Vk:
    def __init__(self, token: str, event_loop) -> None:
        self._session = TokenSession(access_token=token, driver=HttpDriver(loop=event_loop))
        self._session.API_VERSION = "5.90"
        self._api = API(self._session)
        self._keyboard = VkKeyboard()

    async def get_status(self) -> str:
        try:
            response = await self._api.status.get(group_id=207896794)
            return response
        except VkAPIError as err:
            if err.error_code == 27:
                return "working"
            return f"Error {err.error_code}: {err.error_msg}"

    @staticmethod
    def get_api_name() -> str:
        return "vk"

    @staticmethod
    def get_admins() -> list:
        return [447828812, 284737850, 113688146]

    def get_standard_keyboard(self) -> str:
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_text_button("Расписание на сегодня", "primary")
        self._keyboard.add_text_button("Расписание на завтра", "secondary")
        self._keyboard.add_line()
        self._keyboard.add_text_button("Расписание на другой день", "secondary")
        self._keyboard.add_line()
        self._keyboard.add_text_button("Рассылка", "positive")
        self._keyboard.add_text_button("Изменить группу", "negative")
        return self._keyboard.get_keyboard()

    def get_start_keyboard(self) -> str:
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_text_button("Преподаватель", "primary")
        self._keyboard.add_text_button("Студент", "primary")
        return self._keyboard.get_keyboard()

    def get_canceling_keyboard(self) -> str:
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_text_button("Отмена", "negative")
        return self._keyboard.get_keyboard()

    def get_empty_keyboard(self):
        self._keyboard.clear()
        self._keyboard.add_line()
        return None

    async def send_message_queue(self, queue: list, peer_ids: list, keyboard: str) -> None:
        for element in queue:
            await self.send_message(element, peer_ids, keyboard)

    async def send_message(self, message: str, peer_ids: list, keyboard: str) -> None:
        if keyboard is not None:
            for peer_id in peer_ids:
                await self._api.messages.send(
                    message=message,
                    peer_ids=peer_id,
                    random_id=randint(0, 4096),
                    keyboard=keyboard
                )
        else:
            for peer_id in peer_ids:
                await self._api.messages.send(
                    message=message,
                    peer_ids=peer_id,
                    random_id=randint(0, 4096)
                )

