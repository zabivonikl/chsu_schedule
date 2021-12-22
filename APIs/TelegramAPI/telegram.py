from APIs.TelegramAPI.telegram_keyboard import TelegramKeyboard
from Wrappers.AIOHttpWrapper import AIOHttpWrapper


class Telegram:
    def __init__(self, token: str, event_loop):
        self._client = AIOHttpWrapper(event_loop)
        self._bot_link = f"https://api.telegram.org/bot{token}"
        self._keyboard = TelegramKeyboard()

    async def get_status(self):
        return (await self.get_me())['ok']

    async def get_webhook(self):
        data = await self._call_get_method("getWebhookInfo")
        if "result" in data:
            return data["result"]["url"]

    async def get_me(self):
        return await self._call_get_method("getMe")

    @staticmethod
    def get_api_name():
        return "telegram"

    @staticmethod
    def get_admins():
        return [672743407]

    def get_standard_keyboard(self):
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_button("Расписание на сегодня")
        self._keyboard.add_button("Расписание на завтра")
        self._keyboard.add_line()
        self._keyboard.add_button("Расписание на другой день")
        self._keyboard.add_line()
        self._keyboard.add_button("Рассылка")
        self._keyboard.add_button("Изменить группу")
        return self._keyboard.get_keyboard()

    def get_start_keyboard(self):
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_button("Студент")
        self._keyboard.add_button("Преподаватель")
        return self._keyboard.get_keyboard()

    def get_canceling_keyboard(self):
        self._keyboard.clear()
        self._keyboard.add_line()
        self._keyboard.add_button("Отмена")
        return self._keyboard.get_keyboard()

    @staticmethod
    def get_empty_keyboard():
        return None

    async def _call_get_method(self, method_name, params=None):
        try:
            return await self._client.get(f"{self._bot_link}/{method_name}", params=params)
        except Exception as e:
            print(e)

    async def _call_post_method(self, method_name: str, json: dict = None):
        return await self._client.post(f"{self._bot_link}/{method_name}", json=json)

    async def send_message_queue(self, queue, peer_ids, keyboard):
        for element in queue:
            await self.send_message(element, peer_ids, keyboard)

    async def send_message(self, message, peer_ids, keyboard=None):
        for peer_id in peer_ids:
            params = {
                "chat_id": peer_id,
                "text": message,
                "reply_markup": keyboard
            }
            await self._call_get_method("sendMessage", params)

    async def set_webhook(self, url):
        response = await self._call_get_method("setWebhook", {"url": url})
        if response:
            return
        raise ConnectionError("Error of installation webhook")

    async def delete_webhook(self):
        response = await self._call_get_method("deleteWebhook")
        if response:
            return
        raise ConnectionError("Error of installation webhook")
