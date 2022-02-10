from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Wrappers.MongoDb.database import MongoDB


class AbstractHandler:
    def __init__(
            self,
            a: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        self._next_handler = None

        self._chat_platform = a
        self._database = db
        self._chsu_api = ch
        self._keyboard = self._chat_platform.get_keyboard_inst()

    def set_next(self, handler):
        self._next_handler = handler

    async def handle_event(self, event: dict) -> None:
        if self._can_handle(event):
            await self._handle(event)
        else:
            await self._next_handler.handle_event(event)

    @staticmethod
    def _can_handle(event) -> bool:
        pass

    async def _handle(self, event) -> None:
        pass
