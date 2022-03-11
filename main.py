import asyncio
import json

from aiohttp import web

import tokens
from APIs.Chsu.client import Chsu
from APIs.Telegram.client import Telegram
from APIs.Vk.client import Vk
from APIs.abstract_messanger import Messanger

from Handlers.Events.admins_message_event import AdminsMessageHandler
from Handlers.Events.another_event import AnotherEventHandler
from Handlers.Events.callback_event import CallbackHandler
from Handlers.Events.cancel_event import CancelHandler
from Handlers.Events.change_group_event import ChangeGroupHandler
from Handlers.Events.check_changes_event import ScheduleChangesHandler
from Handlers.Events.choose_group_event import ChooseGroupHandler
from Handlers.Events.choose_professor_event import ChooseProfessorHandler
from Handlers.Events.double_date_event import DoubleDateHandler
from Handlers.Events.group_or_professor_name_event import GroupOrProfessorNameHandler
from Handlers.Events.mailing_event import MailingHandler
from Handlers.Events.schedule_for_another_day_event import ScheduleForAnotherDayHandler
from Handlers.Events.schedule_for_today_event import ScheduleForTodayHandler
from Handlers.Events.schedule_for_tomorrow_event import ScheduleForTomorrowHandler
from Handlers.Events.set_check_changes_event import SetCheckChangesHandler
from Handlers.Events.settings_event import SettingsHandler
from Handlers.Events.single_date_handler import SingleDateHandler
from Handlers.Events.start_event import StartHandler
from Handlers.Events.time_stamp_event import TimeStampHandler
from Handlers.Events.unset_check_changes import UnsetCheckChangesHandler
from Handlers.Events.unsubscribe_event import UnsubscribeHandler
from Handlers.Events.user_message_event import UserMessageHandler
from Handlers.date_handler import DateHandler

from Handlers.schedule_change_checker import ScheduleChecker

from Wrappers.MongoDb.database import MongoDB

routes = web.RouteTableDef()
event_loop = asyncio.get_event_loop()


@routes.get("/")
async def index(request):
    return web.Response(text=json.dumps({
        "Server": "working",
        "Server datetime:": date_handler.get_current_date_object().strftime("%d.%m.%Y %H:%M:%S.%f"),
        "Server start datetime:": start_time.strftime("%d.%m.%Y %H:%M:%S.%f"),
        "Server uptime:": str(date_handler.get_current_date_object() - start_time),
        f'CHSU API': f'{await chsu_api.get_status()}',
        f'Database': f'{await mongo_db_api.get_status()}',
        f'VK': f'{await vk_api.get_status()}',
        f'Telegram': {
            'is working': await telegram_api.get_status(),
            'is set webhook': await telegram_api.get_webhook() != ""
        },
        f'Mailing': f"{'not ' if mailing.done() else ''}working",
        f'Update checking': checker.get_status()
    }))


@routes.post('/vk/callback/{returnable}')
async def vk_event(request):
    data = await request.json()
    if data["type"] == "confirmation":
        return web.Response(text=request.match_info['returnable'])
    elif data["type"] == "message_event":
        event = {
            'from_id': data['object']['peer_id'],
            'payload': data['object']['payload']['address'],
            'event_id': data['object']["event_id"]
        }
    else:
        event = {
            'from_id': data['object']['message']['from_id'],
            'text': data['object']['message']['text']
        }
    if "X-Retry-Counter" not in request.headers:
        event_loop.create_task(vk_handler.handle_event(event))
    return web.Response(text="ok")


@routes.post('/telegram/callback/fake')
async def telegram_event(request):
    return web.Response(text="ok")


@routes.get('/telegram/webhook/set/fake')
async def set_webhook(request):
    response = await telegram_api.set_webhook(
        f"https://{request.url.host}/telegram/callback/fake"
    )
    return web.Response(status=response['status'], text=response['text'])


@routes.post('/telegram/callback')
async def telegram_event(request):
    data = await request.json()
    try:
        if 'message' in data:
            event = {
                "from_id": data['message']['from']['id'],
                "text": data['message']['text'],
            }
        elif 'callback_query' in data:
            event = {
                "from_id": data['callback_query']['from']['id'],
                "payload": data['callback_query']['data'],
                'event_id': data['callback_query']["id"]
            }
        else:
            event = None
        event_loop.create_task(telegram_handler.handle_event(event))
        return web.Response(text="ok")
    except KeyError:
        return web.Response(text="ok")


@routes.get('/telegram/webhook/get')
async def get_webhook(request):
    return web.Response(text=await telegram_api.get_webhook())


@routes.get('/telegram/webhook/set')
async def set_webhook(request):
    response = await telegram_api.set_webhook(
        f"https://{request.url.host}/telegram/callback"
    )
    return web.Response(status=response['status'], text=response['text'])


@routes.get('/telegram/webhook/remove')
async def delete_webhook(request):
    await telegram_api.set_webhook()
    return web.Response(text='ok')


async def mailing():
    while date_handler.get_current_date_object().second != 0:
        await asyncio.sleep(.5)
    print(f'Mailing started at: {date_handler.get_current_date_object().strftime("%d.%m.%Y %H:%M:%S.%f")}')
    while True:
        users = await mongo_db_api.get_mailing_subscribers_by_time(
            date_handler.get_current_date_object().strftime("%H:%M")
        )
        for user in users:
            event = {"from_id": user[0], "text": "Расписание на завтра", 'time': date_handler.get_current_date_object()}
            if user[1] == telegram_api.get_name():
                await telegram_handler.handle_event(event)
            elif user[1] == vk_api.get_name():
                await vk_handler.handle_event(event)
        await asyncio.sleep(60)


def get_responsibility_chain(m: Messanger):
    params = (m, mongo_db_api, chsu_api)
    handler = CallbackHandler(*params)
    handler.set_next(StartHandler(*params)) \
        .set_next(SettingsHandler(*params)) \
        .set_next(CancelHandler(*params)) \
 \
        .set_next(ChangeGroupHandler(*params)) \
        .set_next(ChooseGroupHandler(*params)) \
        .set_next(ChooseProfessorHandler(*params)) \
        .set_next(GroupOrProfessorNameHandler(*params)) \
\
        .set_next(AdminsMessageHandler(*params)) \
        .set_next(UserMessageHandler(*params)) \
\
        .set_next(ScheduleChangesHandler(*params)) \
        .set_next(SetCheckChangesHandler(*params)) \
        .set_next(UnsetCheckChangesHandler(*params)) \
\
        .set_next(ScheduleForAnotherDayHandler(*params)) \
        .set_next(ScheduleForTomorrowHandler(*params)) \
        .set_next(ScheduleForTodayHandler(*params)) \
        .set_next(DoubleDateHandler(*params)) \
        .set_next(SingleDateHandler(*params)) \
\
        .set_next(TimeStampHandler(*params)) \
        .set_next(UnsubscribeHandler(*params)) \
        .set_next(MailingHandler(*params)) \
\
        .set_next(AnotherEventHandler(*params))
    return handler


if __name__ == "__main__":

    # init services
    print("Starting services...")
    chsu_api = Chsu(event_loop)
    mongo_db_api = MongoDB(tokens.MONGO_DB_LOGIN, tokens.MONGO_DB_PASSWORD, tokens.MONGO_DB_NAME)
    date_handler = DateHandler()
    print("Done")

    # init messangers
    print("Starting messangers...")
    vk_api = Vk(tokens.VK_API, event_loop)
    vk_handler = get_responsibility_chain(vk_api)
    telegram_api = Telegram(tokens.TELEGRAM_API, event_loop)
    telegram_handler = get_responsibility_chain(telegram_api)
    print("Done")

    # init mailing
    print("Starting mailing...")
    mailing = event_loop.create_task(mailing())

    print("Starting schedule checker...")
    checker = ScheduleChecker(vk_api, telegram_api, mongo_db_api, chsu_api, event_loop)
    print("Done")

    start_time = date_handler.get_current_date_object()
    print(f"Start time: {start_time.strftime('%d.%m.%Y %H:%M:%S.%f')}")

    # init server
    print("Starting web app...")
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=8080, host="127.0.0.1", loop=event_loop)
