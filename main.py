import asyncio
import json
from datetime import datetime, timezone, timedelta

from aiohttp import web

import tokens
from APIs.ChsuAPI.chsu import ChsuApi
from APIs.DiscordAPI.discord import Discord
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
            'isSetWebhook': await telegram_api.get_webhook() != ""
        },
        f'Discord': await discord_api.get_status(),
        f'Mailing': 'working' if mailing.get_name() == 'mailing' else 'not working'
    }))


@routes.post('/vk/callback')
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


@routes.post('/telegram/callback')
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


@routes.get('/telegram/webhook/get')
async def get_webhook(request):
    return web.Response(text=await telegram_api.get_webhook())


@routes.get('/telegram/webhook/set')
async def set_webhook(request):
    if "data" in request.query:
        return web.Response(text=f"ok\n{request.query['data']}")
    if "url" in request.query:
        return web.Response(text='ok' if await telegram_api.set_webhook(request.query['url'] + "/telegram/callback") else "not ok")


@routes.get('/telegram/webhook/remove')
async def delete_webhook(request):
    await telegram_api.delete_webhook()
    return web.Response(text='ok')


@routes.post('/discord/callback')
async def discord_event(request):
    data = await request.json()
    print(data)

    return web.Response(text="ok")


async def mailing():
    while True:
        users = await mongo_db_api.get_mailing_subscribers_by_time(get_time().strftime("%H:%M"))
        for user in users:
            if user[1] == telegram_api.get_api_name():
                await EventHandler(telegram_api, mongo_db_api, chsu_api).handle_event({
                    "from_id": user[0],
                    "text": "Расписание на завтра"
                }, get_time())
            elif user[1] == vk_api.get_api_name():
                await EventHandler(vk_api, mongo_db_api, chsu_api).handle_event({
                    "from_id": user[0],
                    "text": "Расписание на завтра"
                }, get_time())
        await asyncio.sleep(60)


if __name__ == "__main__":
    # init services
    chsu_api = ChsuApi(event_loop)
    mongo_db_api = MongoDB()

    # init messangers
    vk_api = Vk(tokens.VK_API, event_loop)
    telegram_api = Telegram(tokens.TELEGRAM_API, event_loop)
    discord_api = Discord(tokens.DISCORD_API, event_loop)

    # init mailing
    mailing = event_loop.create_task(mailing())
    mailing.set_name("mailing")

    # init server
    app = web.Application()
    app.add_routes(routes)
    # web.run_app(app, port=5050, host="0.0.0.0", loop=event_loop)
    web.run_app(app, port=80, host="localhost", loop=event_loop)
