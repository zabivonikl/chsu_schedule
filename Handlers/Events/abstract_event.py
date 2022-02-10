from __future__ import annotations

from abc import ABC

from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.event_interface import Handler
from Wrappers.MongoDb.database import MongoDB


class AbstractHandler(Handler, ABC):
    _next_handler: Handler = None

    def __init__(
            self,
            a: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        self._chat_platform = a
        self._database = db
        self._chsu_api = ch
        self._keyboard = self._chat_platform.get_keyboard_inst()

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler

    async def handle_event(self, event: dict) -> None:
        try:
            if await self._can_handle(event):
                await self._handle(event)
            else:
                await self._next_handler.handle_event(event)
        except Exception as err:
            await self._chat_platform.send_message(
                f"{self.__class__.__name__} : {self.__class__.__base__.__name__}\n\n{event}\n\n{err}",
                self._chat_platform.get_admins(),
                self._chat_platform.get_keyboard_inst().get_standard_keyboard()
            )

    @staticmethod
    async def _can_handle(event) -> bool:
        pass

    async def _handle(self, event) -> None:
        pass
