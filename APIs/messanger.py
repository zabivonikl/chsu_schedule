from Keyboards.keyboard import Keyboard


class Messanger:
    def __init__(self):
        pass

    async def get_status(self) -> str:
        pass

    def get_keyboard_inst(self) -> Keyboard:
        return Keyboard(self.get_name())

    @staticmethod
    def get_name() -> str:
        pass

    @staticmethod
    def get_admins() -> list:
        pass

    async def send_message_queue(self, queue: list, peer_ids: list, keyboard: str) -> None:
        for element in queue:
            await self.send_message(element, peer_ids, keyboard)

    async def send_message(self, message: str, peer_ids: list, keyboard: str) -> None:
        pass
