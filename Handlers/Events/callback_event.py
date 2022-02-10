from APIs.Chsu.client import Chsu
from APIs.abstract_messanger import Messanger
from Handlers.Events.abstract_event import AbstractHandler
from Wrappers.MongoDb.database import MongoDB


class CallbackHandler(AbstractHandler):
    def __init__(
            self,
            m: Messanger = None,
            db: MongoDB = None,
            ch: Chsu = None
    ):
        super().__init__(m, db, ch)

    @staticmethod
    async def _can_handle(event) -> bool:
        return 'payload' in event

    async def _handle(self, event) -> None:
        buildings = {
            'Советский, 8': (59.12047482336482, 37.93102001811573),
            'Победы, 12': (59.133350120818704, 37.90253587101461),
            'М.Горького, 14': (59.12470566799802, 37.92012233131044),
            'Дзержинского, 30': (59.12339489869266, 37.9275337655467),
            'Луначарского, 5А': (59.123787062658394, 37.92074409709377),
            'Советский, 10': (59.120723715241255, 37.92954511882637),
            'Советский, 25': (59.122360077173084, 37.92928885012067),
            'Труда, 3': (59.11757126831587, 37.92001688361389),
            'Чкалова, 31А': (59.12975151805174, 37.87396552737589)
        }
        await self._chat_platform.confirm_event(event['event_id'], event['from_id'])
        await self._chat_platform.send_coords([event['from_id']], *list(buildings.values())[int(event['payload'])])
