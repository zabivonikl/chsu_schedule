from asyncio import AbstractEventLoop

from APIs.abstract_messanger import Messanger
from Keyboards.abstract_keyboard import Keyboard
from Keyboards.telegram import TelegramKeyboard
from Wrappers.AIOHttp.aiohttp import AIOHttpWrapper


# при переименовании необходимо переопределить get_name()!!!
class Telegram(Messanger):
    def __init__(self, token: str, event_loop: AbstractEventLoop):
        super().__init__()
        self._client = AIOHttpWrapper(event_loop)
        self._bot_link = f"https://api.telegram.org/bot{token}"

    async def get_status(self):
        return (await self._call_get_method("getMe"))['ok']

    @staticmethod
    def get_admins():
        return [672743407]

    @staticmethod
    def get_keyboard_inst() -> Keyboard:
        return TelegramKeyboard()

    async def confirm_event(self, callback_query_id, peer_id=None):
        await self._call_get_method("answerCallbackQuery", {"callback_query_id": callback_query_id})

    async def send_message(self, message: str, peer_ids: list, keyboard: str = None):
        for peer_id in peer_ids:
            params = {"chat_id": peer_id, "text": message}
            if keyboard is not None:
                params["reply_markup"] = keyboard
            await self._call_get_method("sendMessage", params)

    async def send_coords(self, peer_ids: list, lat: int, lon: int, keyboard: str = None):
        for peer_id in peer_ids:
            params = {"chat_id": peer_id, "latitude": lat, "longitude": lon}
            if keyboard is not None:
                params["reply_markup"] = keyboard
            await self._call_get_method("sendLocation", params)

    async def get_webhook(self):
        data = await self._call_get_method("getWebhookInfo")
        if "result" in data:
            return data["result"]["url"]

    async def set_webhook(self, url: str = None):
        if url:
            response = await self._call_get_method("setWebhook", {"url": url})
        else:
            response = await self._call_get_method("deleteWebhook")
        if response["ok"]:
            return {"status": 200, "text": url}
        else:
            return {"status": response['error_code'], "text": f"{response['description']}\nUrl: {url}"}

    async def _call_get_method(self, method_name: str, params: dict = None):
        try:
            return await self._client.get(f"{self._bot_link}/{method_name}", params=params)
        except Exception as e:
            print(e)

    async def _call_post_method(self, method_name: str, json: dict = None):
        return await self._client.post(f"{self._bot_link}/{method_name}", json=json)
