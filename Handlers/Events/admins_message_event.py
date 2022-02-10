from abc import ABC

from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB


class AdminsMessageHandler(AbstractHandler, ABC):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    @staticmethod
    def _can_handle(event) -> bool:
        return len(event['text']) != 0 and event['text'][0] == "!"

    async def _handle(self, event) -> None:
        to_id = int(event['text'].split(':')[0][1:])
        message = event['text'].split(':')[1]
        kb = self._chat_platform.get_keyboard_inst().get_standard_keyboard()
        await self._chat_platform.send_message(
            f"Сообщение отправлено",
            [event['from_id']], kb
        )
        await self._chat_platform.send_message(
            f"Сообщение от администратора: {message}\n\n"
            f"Для ответа используйте \";\" в начале сообщения.", [to_id], kb
        )
