from abc import ABC

from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB


class UnsubscribeHandler(AbstractHandler, ABC):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    @staticmethod
    def _can_handle(event) -> bool:
        return event['text'] == "Отписаться"

    async def _handle(self, event) -> None:
        await self._database.set_mailing_time(event['from_id'], self._chat_platform.get_name())
        kb = self._chat_platform.get_keyboard_inst().get_standard_keyboard()
        await self._chat_platform.send_message(f"Вы отписались от рассылки.", [event['from_id']], kb)
