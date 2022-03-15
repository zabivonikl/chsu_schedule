from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB
from Wrappers.MongoDb.exceptions import EmptyResponse


class GroupOrProfessorNameHandler(AbstractHandler):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    async def _can_handle(self, event) -> bool:
        try:
            return await self._chsu_api.get_user_type(event['text'])
        except EmptyResponse:
            return False

    async def _handle(self, event) -> None:
        await self._database.set_user_data(
            event['from_id'],
            self._chat_platform.get_name(),
            **(
                dict(professor_name=event['text'])
                if await self._chsu_api.get_user_type(event['text']) == "professor"
                else dict(group_name=event['text'])
            )
        )
        await self._chat_platform.send_message(
            "Данные сохранены.\n",
            [event['from_id']],
            self._keyboard.get_standard_keyboard()
        )
