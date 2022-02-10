from abc import ABC

from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.date_handler import DateHandler
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB


class ScheduleForTomorrowHandler(AbstractHandler, ABC):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)
        self._date_handler = DateHandler()

    @staticmethod
    def _can_handle(event) -> bool:
        return event['text'] == "Расписание на завтра"

    async def _handle(self, event) -> None:
        self._date_handler.parse_tomorrow_word()
        event['text'] = self._date_handler.get_string()[0]
        await self._next_handler.handle_event(event)
