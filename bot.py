import os
import requests
from dotenv import load_dotenv
from random import randrange


load_dotenv()


class Bot:
    MSG_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Para eso podemos ir a: \n\n"
            ),
        },
    }

    LATITUDE = os.getenv('LATITUDE')
    LONGITUDE = os.getenv('LONGITUDE')

    def __init__(self, channel):
        self.channel = channel

    def _get_place(self, kind, radius):
        params = {
            'key': os.getenv('GOOGLE_API_KEY'),
            'location': f'{self.LATITUDE},{self.LONGITUDE}',
            'radius': radius,
            'type': kind,
            'opennow': True,
            'language': 'es-419'
        }
        r = requests.get(
            os.getenv('GOOGLE_BASE_SEARCH_URL'),
            params=params
        )
        places = r.json()['results']
        places_names = {f"<{os.getenv('GOOGLE_PLACE_BASE_URL')}{p['place_id']}|{p['name']}>": f"{p['rating']} :star:"
                        for p in sorted(places, key = lambda p: p['rating'], reverse=True)}
        chosen_place_name = list(places_names)[randrange(len(places_names))]

        place_msg = f'{chosen_place_name}: {places_names[chosen_place_name]}'
        return {"type": "section", "text": {"type": "mrkdwn", "text": place_msg}},

    def get_message_payload(self, kind, radius):
        return {
            "channel": self.channel,
            "blocks": [
                self.MSG_BLOCK,
                *self._get_place(kind, radius),
            ],
        }
