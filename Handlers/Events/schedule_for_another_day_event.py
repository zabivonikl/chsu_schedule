from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB


class ScheduleForAnotherDayHandler(AbstractHandler):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    @staticmethod
    async def _can_handle(event) -> bool:
        return event['text'] == "Расписание на другой день"

    async def _handle(self, event) -> None:
        kb = self._chat_platform.get_keyboard_inst().get_canceling_keyboard()
        text = "Введите дату:\nПример: 08.02 - запрос расписания для конкретного дня.\n" \
               "31.10-07.11 - запрос расписания для заданного интервала дат."
        await self._chat_platform.send_message(text, [event['from_id']], kb)
