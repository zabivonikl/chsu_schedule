from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB


class GroupOrProfessorNameHandler(AbstractHandler):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    async def _can_handle(self, event) -> bool:
        self._id_by_professors = await self._chsu_api.get_id_by_professors_list()
        self._id_by_groups = await self._chsu_api.get_id_by_groups_list()
        return event['text'] in {
            **self._id_by_groups,
            **self._id_by_professors
        }

    async def _handle(self, event) -> None:
        await self._database.set_user_data(
            event['from_id'],
            self._chat_platform.get_name(),
            **(
                dict(professor_name=event['text'])
                if event['text'] in self._id_by_professors
                else dict(group_name=event['text'])
            )
        )
        await self._chat_platform.send_message(
            "Данные сохранены.\n",
            [event['from_id']],
            self._keyboard.get_standard_keyboard()
        )
