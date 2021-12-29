from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from Wrappers.AIOHttp.aiohttp import AIOHttpWrapper


class Discord:
    # todo разобраться с вебсокетами и доделать
    def __init__(self, api_token: str, public_token: str, event_loop):
        self._base_url = f"https://discord.com/api/v9/"
        self._http_client = AIOHttpWrapper(event_loop)
        self._custom_ids = {
            'schedule_for_today_btn': 'Расписание на сегодня',
            'schedule_for_tomorrow_btn': 'Расписание на завтра',
            'schedule_for_another_day_btn': 'Расписание на другой день',
            'mailing_btn': 'Рассылка',
            'change_group_btn': 'Изменить группу',
            'professor_btn': 'Преподаватель',
            'student_btn': 'Студент',
            'cancel_btn': 'Отмена'
        }
        self._base_headers = {
            "Content-Type": "application/json",
            "charset": "utf-8",
            "Authorization": f"Bot {api_token}"
        }
        self._verify_key = VerifyKey(bytes.fromhex(public_token))

    async def get_status(self):
        response = await self._http_client.get(self._base_url + "/users/@me", headers=self._base_headers)
        if "id" in response:
            return "working"
        else:
            return response["message"]

    async def is_valid_request(self, request):
        signature = request.headers["X-Signature-Ed25519"]
        timestamp = request.headers["X-Signature-Timestamp"]
        body = await request.text()
        try:
            self._verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
            return True
        except BadSignatureError:
            return False

    def get_button_text(self, custom_id):
        return self._custom_ids[custom_id]

    @staticmethod
    def get_admins():
        raise NotImplementedError()

    @staticmethod
    def get_standard_keyboard():
        raise NotImplementedError()
        kb = VkKeyboard()
        kb.add_line()
        kb.add_text_button("Расписание на сегодня", "primary")
        kb.add_text_button("Расписание на завтра", "secondary")
        kb.add_line()
        kb.add_text_button("Расписание на другой день", "secondary")
        kb.add_line()
        kb.add_text_button("Рассылка", "positive")
        kb.add_text_button("Изменить группу", "negative")
        return kb.get_keyboard()

    @staticmethod
    def get_start_keyboard():
        raise NotImplementedError()
        kb = VkKeyboard()
        kb.add_line()
        kb.add_text_button("Преподаватель", "primary")
        kb.add_text_button("Студент", "primary")
        return kb.get_keyboard()

    @staticmethod
    def get_canceling_keyboard():
        raise NotImplementedError()
        kb = VkKeyboard()
        kb.add_line()
        kb.add_text_button("Отмена", "negative")
        return kb.get_keyboard()

    @staticmethod
    def get_empty_keyboard():
        return None

    @staticmethod
    def get_api_name():
        return "discord"

    async def send_message_queue(self, queue, peer_ids, keyboard):
        for element in queue:
            await self.send_message(element, peer_ids, keyboard)

    async def send_message(self, message, peer_ids, keyboard):
        data = {
            "content": message,
            "components": keyboard
        }
        for peer_id in peer_ids:
            await self._http_client.post(self._base_url + f"/channels/{peer_id}/messages", json=data)
