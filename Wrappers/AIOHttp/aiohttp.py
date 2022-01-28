from asyncio import AbstractEventLoop

import aiohttp


class AIOHttpWrapper:
    def __init__(self, event_loop: AbstractEventLoop):
        self._session = aiohttp.ClientSession(
            loop=event_loop
        )

    def get_client(self):
        return self._session

    async def post(self, url: str, json: dict = None, headers: dict = None):
        async with self._session.post(url=url, json=json, headers=headers) as response:
            return await response.json()

    async def get(self, url: str, headers: dict = None, params: dict = None):
        async with self._session.get(url=url, headers=headers, params=params) as response:
            return await response.json()
