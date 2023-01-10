import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
import logging

# caffeine.py can be triggered from a third party heroku scheduler every X minutes in order to send a GET request
# This prevents the dynos from going idle

# Get environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Telegram Bot Token
BOT_TOKEN = os.environ['BOT_TOKEN']
# Heroku App Name
APP_NAME = os.environ['APP_NAME']

url = "https://" + APP_NAME + ".herokuapp.com/" + BOT_TOKEN

# Send request to heroku app to prevent idle mode
requests.get(url)

logging.info('caffeine.py GET request')
