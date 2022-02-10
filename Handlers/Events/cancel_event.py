from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB


class CancelHandler(AbstractHandler):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    @staticmethod
    def _can_handle(event) -> bool:
        return event['text'] == "Отмена"

    def _handle(self, event) -> None:
        kb = self._chat_platform.get_keyboard_inst().get_standard_keyboard()
        await self._chat_platform.send_message(f"Действие отменено.", [event['from_id']], kb)
