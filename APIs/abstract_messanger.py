from Keyboards.abstract_keyboard import Keyboard


class Messanger:
    def __init__(self):
        pass

    async def get_status(self) -> str:
        pass

    @staticmethod
    def get_keyboard_inst() -> Keyboard:
        return Keyboard()

    def get_name(self) -> str:
        return self.__class__.__name__.lower()

    @staticmethod
    def get_admins() -> list:
        pass

    async def confirm_event(self, callback_query_id, peer_id = None):
        pass

    async def send_message(self, message: str, peer_ids: list, keyboard: str) -> None:
        pass

    async def send_coords(self, peer_ids: list, lat: int, lon: int, keyboard: str = None):
        pass
