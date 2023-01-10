import base64
import os
from os.path import join, dirname
from telegram import Bot
import requests
from dotenv import load_dotenv

# Get environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Telegrm Bot Token
BOT_TOKEN = os.environ['BOT_TOKEN']
# Heroku App Name and API Token
APP_NAME = os.environ['APP_NAME']
HEROKU_API_TOKEN = os.environ['HEROKU_API_TOKEN']

# Initialize Bot
coach_bot = Bot(BOT_TOKEN)

# Function encodes string to base64


def encode64(text):

    if not type(text) == str:
        return

    text = text.encode('ascii')
    bytes = base64.b64encode(text)

    return bytes

# Base64 to string


def decode64(bytes):

    text = base64.b64decode(bytes).decode('ascii')

    return text

# Bot sends message according to message type (text, video etc.)


def send_message(chat_id, message):

    if not message['media']:
        coach_bot.send_message(chat_id=chat_id,
                               text=message['text'])
    elif message['media_type'] == 'video':
        if message['text']:
            coach_bot.send_video(
                chat_id=chat_id, video=message['media'], caption=message['text'])
        else:
            coach_bot.send_video(chat_id=chat_id, video=message['media'])
    elif message['media_type'] == 'photo':
        if message['text']:
            coach_bot.send_photo(
                chat_id=chat_id, photo=message['media'], caption=message['text'])
        else:
            coach_bot.send_photo(chat_id=chat_id, photo=message['media'])
    elif message['media_type'] == 'voice':
        coach_bot.send_voice(chat_id=chat_id, voice=message['media'])
    elif message['media_type'] == 'file':
        coach_bot.send_document(chat_id=chat_id, document=message['media'])

# Restart scheduler (clock dyno) to update auto-messages (when auto messages have been added or removed)


def restart():
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/vnd.heroku+json; version=3',
               'Authorization': 'Bearer '+HEROKU_API_TOKEN}
    url = 'https://api.heroku.com/apps/'+APP_NAME+'/dynos/clock'

    response = requests.delete(url, headers=headers)

    return response
