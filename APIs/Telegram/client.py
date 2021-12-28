from Wrappers.AIOHttp.aiohttp import AIOHttpWrapper


class Telegram:
    def __init__(self, token: str, event_loop):
        self._client = AIOHttpWrapper(event_loop)
        self._bot_link = f"https://api.telegram.org/bot{token}"

    async def get_status(self):
        return (await self._call_get_method("getMe"))['ok']

    @staticmethod
    def get_api_name():
        return "telegram"

    @staticmethod
    def get_admins():
        return [672743407]

    async def send_message_queue(self, queue, peer_ids, keyboard):
        for element in queue:
            await self.send_message(element, peer_ids, keyboard)

    async def send_message(self, message, peer_ids, keyboard=None):
        for peer_id in peer_ids:
            params = {
                "chat_id": peer_id,
                "text": message,
            }
            if keyboard is not None:
                params["reply_markup"] = keyboard
            await self._call_get_method("sendMessage", params)

    async def get_webhook(self):
        data = await self._call_get_method("getWebhookInfo")
        if "result" in data:
            return data["result"]["url"]

    async def set_webhook(self, url):
        response = await self._call_get_method("setWebhook", {"url": url})
        if response["ok"]:
            return {"status": 200, "text": url}
        else:
            return {"status": response['error_code'], "text": f"{response['description']}\nUrl: {url}"}

    async def delete_webhook(self):
        response = await self._call_get_method("deleteWebhook")
        if response:
            return
        raise ConnectionError("Error of installation webhook")

    async def _call_get_method(self, method_name, params=None):
        try:
            return await self._client.get(f"{self._bot_link}/{method_name}", params=params)
        except Exception as e:
            print(e)

    async def _call_post_method(self, method_name: str, json: dict = None):
        return await self._client.post(f"{self._bot_link}/{method_name}", json=json)
