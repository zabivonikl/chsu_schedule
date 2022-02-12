from asyncio import AbstractEventLoop
from random import randint

from aiovk import TokenSession, API
from aiovk.drivers import HttpDriver
from aiovk.exceptions import VkAPIError

from APIs.abstract_messanger import Messanger
from Keyboards.abstract_keyboard import Keyboard
from Keyboards.vk import VkKeyboard


# при переименовании необходимо переопределить get_name()!!!
class Vk(Messanger):
    def __init__(self, token: str, event_loop: AbstractEventLoop) -> None:
        super().__init__()
        session = TokenSession(access_token=token, driver=HttpDriver(loop=event_loop))
        session.API_VERSION = "5.131"
        self._api = API(session)

    async def get_status(self) -> str:
        try:
            response = await self._api.status.get(group_id=207896794)
            return response
        except VkAPIError as err:
            if err.error_code == 27:
                return "working"
            return f"Error {err.error_code}: {err.error_msg}"

    @staticmethod
    def get_admins() -> list:
        return [447828812, 113688146]

    @staticmethod
    def get_keyboard_inst() -> Keyboard:
        return VkKeyboard()

    async def confirm_event(self, callback_query_id: str, peer_id: int = None) -> None:
        await self._api.messages.sendMessageEventAnswer(event_id=callback_query_id, peer_id=peer_id, user_id=peer_id)

    async def send_message(self, message: str, peer_ids: list, keyboard: str) -> None:
        args = dict(message=message, peer_ids=peer_ids, random_id=randint(0, 4096))
        if keyboard:
            args['keyboard'] = keyboard
        await self._api.messages.send(**args)

    async def send_coords(self, peer_ids: list, lat: int, lon: int, keyboard: str = None):
        args = dict(peer_ids=peer_ids, random_id=randint(0, 4096), lat=lat, long=lon)
        if keyboard:
            args['keyboard'] = keyboard
        await self._api.messages.send(**args)
