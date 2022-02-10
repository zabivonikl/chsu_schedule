from re import match

from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB


class TimeStampHandler(AbstractHandler):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    @staticmethod
    async def _can_handle(event) -> bool:
        return match(r'^(0\d|1\d|2[0-3])[:][0-5]\d$', event['text']) is not None

    async def _handle(self, event) -> None:
        await self._database.set_mailing_time(
            event['from_id'], self._chat_platform.get_name(), event['text']
        )
        text = f"Вы подписались на рассылку расписания. Теперь, ежедневно в {event['text']}, " \
               f"Вы будете получать расписание на следующий день."
        kb = self._chat_platform.get_keyboard_inst().get_standard_keyboard()
        await self._chat_platform.send_message(text, [event['from_id']], kb)
