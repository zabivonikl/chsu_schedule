from asyncio import AbstractEventLoop
from random import randint

from aiovk import TokenSession, API
from aiovk.drivers import HttpDriver
from aiovk.exceptions import VkAPIError

from APIs.messanger import Messanger


class Vk(Messanger):
    def __init__(self, token: str, event_loop: AbstractEventLoop) -> None:
        super().__init__()
        self._session = TokenSession(access_token=token, driver=HttpDriver(loop=event_loop))
        self._session.API_VERSION = "5.90"
        self._api = API(self._session)

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
