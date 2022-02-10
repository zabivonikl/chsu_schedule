from abc import ABC

from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB


class UserMessageHandler(AbstractHandler, ABC):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    @staticmethod
    def _can_handle(event) -> bool:
        return event['text'] and event['text'][0] == ';'

    async def _handle(self, event) -> None:
        kb = self._chat_platform.get_keyboard_inst().get_standard_keyboard()
        await self._chat_platform.send_message(
            f"Сообщение от пользователя: {event['text'][1:]}\n\n"
            f"Для ответа используйте \"!{event['from_id']}: %сообщение%\".",
            self._chat_platform.get_admins(), kb
        )
        await self._chat_platform.send_message(f"Сообщение отправлено.", [event['from_id']], kb)
