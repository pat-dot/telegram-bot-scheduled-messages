#!/usr/bin/env
import os
from os.path import join, dirname
from apscheduler.schedulers.blocking import BlockingScheduler
from utils import send_message
import pymongo
from dotenv import load_dotenv

# Get environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGO_URI = os.environ['MONGO_URI']

# Setting up schdeduler
# Blocking scheduler runs on seperate heroku dyno
sched = BlockingScheduler(timezone="Europe/Berlin")  # probably change timezone

# Initialize database and connect
mongo_client = pymongo.MongoClient(MONGO_URI)
database = mongo_client['fts_bot']
user_db = database['users']

# Get all users from database
users = user_db.find()

# Get auto-messages from each user and schedule messages to be sent at defined times using send function from utils
for user in users:
    if user['auto_message'] == 0:
        continue
    for message in user['message']:
        if message == []:
            break
        hour, minute = message['time'].split(':')
        sched.add_job(send_message, args=[
                      user['chat_id'], message], trigger='cron', day_of_week='mon-sun', hour=hour, minute=minute)


sched.start()
