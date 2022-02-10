from abc import ABC
from re import match

from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.double_date_event import DoubleDateHandler
from Wrappers.MongoDb.database import MongoDB


class SingleDateHandler(DoubleDateHandler, ABC):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    @staticmethod
    def _can_handle(event) -> bool:
        return match(
            r'^(0[1-9]|1\d|2\d|3[0-1])[.](0[1-9]|1[0-2])$', event['text']
        ) is not None

    async def _handle(self, event) -> None:
        self._date_handler.parse_single_date(event['text'])
        await self._send_schedule(
            [event['from_id']], await self._get_schedule(event['from_id'], *self._date_handler.get_string())
        )
