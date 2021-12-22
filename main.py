import asyncio
import json
from datetime import datetime, timezone, timedelta

from aiohttp import web

import tokens
from APIs.ChsuAPI.chsu import ChsuApi
from APIs.MongoDbAPI.mongo_db import MongoDB
from APIs.TelegramAPI.telegram import Telegram
from APIs.VkAPI.vk import Vk
from DataHandlers.event_handler import EventHandler

routes = web.RouteTableDef()
event_loop = asyncio.get_event_loop()


def get_time():
    return datetime.now(timezone(timedelta(hours=3.0)))


@routes.get("/")
async def index(request):
    return web.Response(text=json.dumps({
        "Server": "working",
        "Server time:": get_time().strftime("%H:%M"),
        f'CHSU API': f'{await chsu_api.get_status()}',
        f'Database': f'{await mongo_db_api.get_status()}',
        f'VK': f'{await vk_api.get_status()}',
        f'Telegram': {
            'isWorking': await telegram_api.get_status(),
            'isSetWebhook': await telegram_api.get_set_webhook()
        }
    }))


@routes.post('/vk_callback')
async def vk_event(request):
    data = await request.json()
    if data["type"] == "confirmation":
        return web.Response(text="5229efbf")
    if data['object']['message']['from_id'] not in [447828812, 89951785]:
        return web.Response(text="ok")
    event = {
        'from_id': data['object']['message']['from_id'],
        'text': data['object']['message']['text']
    }
    await EventHandler(vk_api, mongo_db_api, chsu_api).handle_event(event, get_time())

    return web.Response(text="ok")


@routes.post('/telegram_callback')
async def telegram_event(request):
    data = await request.json()
    try:
        event = {
            "from_id": data['message']['from']['id'],
            "text": data['message']['text']
        }
        await EventHandler(telegram_api, mongo_db_api, chsu_api).handle_event(event, get_time())
        return web.Response(text="ok")
    except KeyError:
        return web.Response(text="ok")


@routes.post('/discord_callback')
async def discord_event(request):
    data = await request.json()

    return web.Response(text="0d238b23" if data["type"] == "confirmation" else "ok")


async def init_telegram(api):
    await api.set_webhook("https://4079-178-69-250-141.ngrok.io/telegram_callback")
    await api.delete_webhook()


if __name__ == "__main__":
    # init services
    chsu_api = ChsuApi(event_loop)
    mongo_db_api = MongoDB()

    # init messangers
    vk_api = Vk(tokens.VK_API, event_loop)
    telegram_api = Telegram(tokens.TELEGRAM_API, event_loop)
    # event_loop.run_until_complete(init_telegram(telegram_api))

    # init server
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=80, host="localhost", loop=event_loop)
