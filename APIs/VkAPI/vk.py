from random import randint

from aiovk import TokenSession, API
from aiovk.drivers import HttpDriver
from aiovk.exceptions import VkAPIError

from APIs.VkAPI.vk_keyboard import VkKeyboard


class Vk:
    def __init__(self, token, event_loop):
        self.__session = TokenSession(access_token=token, driver=HttpDriver(loop=event_loop))
        self.__session.API_VERSION = "5.90"
        self.__api = API(self.__session)

    async def get_status(self):
        try:
            response = await self.__api.status.get(group_id=207896794)
            return response
        except VkAPIError as err:
            if err.error_code == 27:
                return "working"
            return f"Error {err.error_code}: {err.error_msg}"

    @staticmethod
    def get_admins():
        return [447828812, 284737850, 113688146]

    @staticmethod
    def get_standard_keyboard():
        kb = VkKeyboard()
        kb.add_line()
        kb.add_text_button("Расписание на сегодня", "primary")
        kb.add_text_button("Расписание на завтра", "secondary")
        kb.add_line()
        kb.add_text_button("Расписание на другой день", "secondary")
        kb.add_line()
        kb.add_text_button("Рассылка", "positive")
        kb.add_text_button("Изменить группу", "negative")
        return kb.get_keyboard()

    @staticmethod
    def get_start_keyboard():
        kb = VkKeyboard()
        kb.add_line()
        kb.add_text_button("Преподаватель", "primary")
        kb.add_text_button("Студент", "primary")
        return kb.get_keyboard()

    @staticmethod
    def get_canceling_keyboard():
        kb = VkKeyboard()
        kb.add_line()
        kb.add_text_button("Отмена", "negative")
        return kb.get_keyboard()

    @staticmethod
    def get_empty_keyboard():
        return VkKeyboard().get_keyboard()

    @staticmethod
    def get_api_name():
        return "vk"

    async def send_message_queue(self, queue, peer_ids, keyboard):
        for element in queue:
            await self.send_message(element, peer_ids, keyboard)

    async def send_message(self, message, peer_ids, keyboard):
        await self.__api.messages.send(
            message=message,
            peer_ids=peer_ids,
            random_id=randint(0, 4096),
            keyboard=keyboard
        )
