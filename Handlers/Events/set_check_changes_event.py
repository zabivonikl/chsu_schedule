from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB


class SetCheckChangesHandler(AbstractHandler):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    @staticmethod
    def _can_handle(event) -> bool:
        return event['text'] == "Отслеживать изменения"

    def _handle(self, event) -> None:
        await self._database.set_check_changes_member(event['from_id'], self._chat_platform.get_name(), True)
        kb = self._chat_platform.get_keyboard_inst().get_standard_keyboard()
        await self._chat_platform.send_message(
            f"Теперь ежечасно вам будут приходить уведомления о изменениях "
            f"в расписании, если они будут.", [event['from_id']], kb
        )
