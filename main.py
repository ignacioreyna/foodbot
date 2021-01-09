# import os
# import json
# import logging
#
# from flask import Flask, request, make_response, Response
#
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError
# from slack_sdk.signature import SignatureVerifier
#
# from slash_command import Slash
#
# logging.basicConfig(level=logging.DEBUG)
# app = Flask(__name__, )
#
#
# @app.route("/slack/test", methods=["POST"])
# def command():
#     # print('='*30, request.get_data(), request.headers, '='*30)
#     print(verifier)
#     if not verifier.is_valid_request(request.get_data(), request.headers):
#         return make_response("invalid request", 403)
#     info = request.form
#
#     # # send user a response via DM
#     # im_id = slack_client.im_open(user=info["user_id"])["channel"]["id"]
#     # ownerMsg = slack_client.chat_postMessage(
#     #   channel=im_id,
#     #   text=commander.getMessage()
#     # )
#
#     # # send channel a response
#     # response = slack_client.chat_postMessage(
#     #   channel='#{}'.format(info["channel_name"]),
#     #   text=commander.getMessage()
#     # )
#
#     try:
#         response = slack_client.chat_postMessage(
#             channel='#{}'.format(info["channel_name"]),
#             text=commander.get_message()
#         )  # .get()
#     except SlackApiError as e:
#         logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
#         logging.error(e.response)
#         return make_response("", e.response.status_code)
#
#     return make_response("", response.status_code)
#
#
# # Start the Flask server
# if __name__ == "__main__":
#     SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
#     SLACK_SIGNATURE = os.environ['SLACK_SIGNING_SECRET']
#     slack_client = WebClient(SLACK_BOT_TOKEN)
#     verifier = SignatureVerifier(SLACK_SIGNATURE)
#
#     commander = Slash("Hey there! It works.")
#
#     app.run(debug=True)


# import os
# import logging
# from dotenv import load_dotenv
# from flask import Flask
# from slack import WebClient
# from slackeventsapi import SlackEventAdapter
# from bot import Bot
#
# # Load env
# load_dotenv()
# # Create a slack client
# slack_web_client = WebClient(token=os.getenv("SLACK_TOKEN"))
#
# # Get a new CoinBot
# coin_bot = Bot("#food-bot-test")
#
# # Get the onboarding message payload
# message = coin_bot.get_message_payload()
#
# # Post the onboarding message in Slack
# slack_web_client.chat_postMessage(**message)

import os
import logging
from dotenv import load_dotenv
from flask import Flask, request
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from bot import Bot

# Load env
load_dotenv()
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.getenv("SLACK_EVENTS_TOKEN"), "/slack/events", app)

slack_web_client = WebClient(token=os.getenv("SLACK_TOKEN"))
BOT_ID = os.getenv('BOT_ID')


def find_place(channel, kind, radius=700):
    bot = Bot(channel)

    json_msg = bot.get_message_payload(kind, radius)

    slack_web_client.chat_postMessage(**json_msg)


def send_help(channel, bot_id):
    msg_block = {
        "type": "section",
        "text":     {
            "type": "mrkdwn",
            "text": (
                f"""
<@{bot_id}> `comida`: responde un lugar para ir a comer \n
<@{bot_id}> `cafe`: responde un lugar para ir a tomar un cafe \n
<@{bot_id}> `algo rico`: responde un lugar para ir a comer algo dulce \n
<@{bot_id}> `cerveza | after | bar`: responde un lugar para ir a tomar algo \n
<@{bot_id}> `help | ayuda | **cualquier otra cosa**`: muestra este mensaje
                """
            ),
        },
    }

    help_msg = {
        "channel": channel,
        "blocks": [
            msg_block
        ],
    }

    slack_web_client.chat_postMessage(**help_msg)


@slack_events_adapter.on("message")
def message(payload):

    event = payload.get("event", {})

    text = event.get("text")

    if f'<@{BOT_ID}>' in text.upper():
        channel_id = event.get("channel")
        bot = Bot(channel_id)
        if 'comida' in text.lower():
            return find_place(channel_id, 'restaurant')
        elif 'cafe' in text.lower():
            return find_place(channel_id, 'cafe')
        elif 'algo rico' in text.lower():
            return find_place(channel_id, 'bakery')
        elif 'bar' in text.lower() or 'after' in text.lower() or 'cerveza' in text.lower():
            return find_place(channel_id, 'bar', radius=1000)
        else:
            return send_help(channel_id, BOT_ID)


if __name__ == "__main__":
    logger = logging.getLogger()

    logger.setLevel(logging.ERROR)

    logger.addHandler(logging.StreamHandler())

    app.run(host='0.0.0.0', port=3000)
