#!/usr/bin/env
import sys
import os
from os.path import join, dirname
import logging
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import pymongo
from utils import restart
from dotenv import load_dotenv

# Get environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Telegrm Bot Token
BOT_TOKEN = os.environ['BOT_TOKEN']
# Heroku App Name
APP_NAME = os.environ['APP_NAME']
# Mongo URI when using MongoDB
MONGO_URI = os.environ['MONGO_URI']

# Telegram webhook uses port 8443
PORT = int(os.environ.get('PORT', '8443'))

# Set up constants for telegram conversation
NEW_USER = 1
USER, DELETE, DEACTIVATE, ACTIVATE, DEL_MESS, CONFIG, TIME, MESSAGE = range(8)

# Intialize Mongo Client and connect to database
mongo_client = pymongo.MongoClient(MONGO_URI)
database = mongo_client['fts_bot']
user_db = database['users']
admin_db = database['admin']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s (%(lineno)d): %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG,
                    handlers=[
                        logging.StreamHandler(sys.stdout)
                    ])

logger = logging.getLogger(__name__)

# Function to register new users and add them to the database when start command is sent


def reg_user(update, context):

    confirmation_message = ', you have sucessfully been registered!'

    user = user_db.find_one({"user_id": update.message.from_user.id})

    if user == None:
        new_user = {'user_id': update.message.from_user.id,
                    'chat_id': update.message.chat_id,
                    'first_name': update.message.from_user.first_name,
                    'last_name': update.message.from_user.last_name,
                    'message': [],
                    'auto_message': 0,
                    'date': datetime.datetime.utcnow()}
        inserted = user_db.insert_one(new_user)
        user = user_db.find_one({"_id": inserted.inserted_id})
        update.message.reply_text(
            'Hey ' + user['first_name'] + ' ' + confirmation_message)

    return user

# Welcome message when a new user joins the group - starting conversation to register new user


def new_group(update, context):

    welcome_message = 'Hello, do you want to receive regular messages?'

    keyboard = [
        [InlineKeyboardButton('Ja', callback_data='yes')],
        [InlineKeyboardButton('Nein', callback_data='no')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.message.chat.id, text=welcome_message,
                             reply_markup=reply_markup)

    return NEW_USER

# Conversation function to register new user to database


def new_user(update, context):

    confirmation_message = ', you have sucessfully been registered!'
    decline_message = 'No problem, if you like to use this service later you can type /start at any time.'

    query = update.callback_query
    query.answer()

    if query.data == 'yes':
        user = user_db.find_one({"user_id": query.from_user.id})

        if user == None:
            new_user = {'user_id': query.from_user.id,
                        'chat_id': query.message.chat.id,
                        'first_name': query.from_user.first_name,
                        'last_name': query.from_user.last_name,
                        'message': [],
                        'auto_message': 0,
                        'date': datetime.datetime.utcnow()}
            inserted = user_db.insert_one(new_user)
            user = user_db.find_one({"_id": inserted.inserted_id})
            context.bot.send_message(chat_id=query.message.chat.id, text='Hey ' +
                                     user['first_name'] + ' ' + confirmation_message)

        return ConversationHandler.END

    elif query.data == 'no':
        context.bot.send_message(chat_id=query.message.chat.id,
                                 text=decline_message)
        return ConversationHandler.END


# Function to register new administrators and add them to the database


def reg_admin(update, context):
    confirmation_message = 'you have successfully been registered as an administrator!'

    user = admin_db.find_one({"user_id": update.message.from_user.id})

    if user == None:
        new_user = {'user_id': update.message.from_user.id,
                    'chat_id': update.message.chat_id,
                    'first_name': update.message.from_user.first_name,
                    'last_name': update.message.from_user.last_name,
                    'date': datetime.datetime.utcnow()}
        inserted = admin_db.insert_one(new_user)
        user = admin_db.find_one({"_id": inserted.inserted_id})
        update.message.reply_text(
            'Hey ' + user['first_name'] + ' ' + confirmation_message)

    return user

# conversation function to list possible options to administrator (delete user, add new messages etc.)


def task(update, context):

    admin = admin_db.find_one({"user_id": update.message.from_user.id})

    if admin == None:
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton('Delete user', callback_data='delete')],
        [InlineKeyboardButton(
            'Deactivate auto-messages', callback_data='deactivate')],
        [InlineKeyboardButton('Activate auto-messages',
                              callback_data='activate')],
        [InlineKeyboardButton(
            'Add message', callback_data='config')],
        [InlineKeyboardButton(
            'Delete messages', callback_data='del_mess')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("What would you like to do?",
                              reply_markup=reply_markup)

    return USER

# Get user from database and proceed to the respective action function


def get_user(update, context):
    """Set user configuration"""

    query = update.callback_query
    query.answer()

    keyboard = []

    users = user_db.find()

    for user in users:
        name = user['first_name'] + ' ' + user['last_name']
        keyboard.append([InlineKeyboardButton(
            name, callback_data=user['user_id'])])

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=query.message.chat.id,
                             text="Choose user:", reply_markup=reply_markup)

    if query.data == 'delete':
        return DELETE
    elif query.data == 'deactivate':
        return DEACTIVATE
    elif query.data == 'activate':
        return ACTIVATE
    elif query.data == 'del_mess':
        return DEL_MESS
    elif query.data == 'config':
        return CONFIG

    return ConversationHandler.END

# Delete user from database and send confirmation message


def delete(update, context):
    """Delete user from database"""

    query = update.callback_query
    query.answer()
    user_id = int(query.data)

    user_db.delete_one({"user_id": user_id})

    restart()

    context.bot.send_message(chat_id=query.message.chat.id,
                             text='User has been deleted.')

    return ConversationHandler.END

# Deactivate auto-messages and send confirmation message


def deactivate(update, context):
    """Deactivate messages for the user"""
    query = update.callback_query
    query.answer()
    user_id = int(query.data)
    user_db.update_one({'user_id': user_id}, {
                       '$set': {'auto_message': 0}}, upsert=False)

    # Restart scheduler and update auto-messages
    restart()

    context.bot.send_message(chat_id=query.message.chat.id,
                             text='Auto-messages for this user have been deactivated.')

    return ConversationHandler.END

# Activate auto-messages


def activate(update, context):
    """Activate messages for the user"""
    query = update.callback_query
    query.answer()
    user_id = int(query.data)
    user_db.update_one({'user_id': user_id}, {
                       '$set': {'auto_message': 1}}, upsert=False)

    # Restart scheduler and update auto-messages
    restart()

    context.bot.send_message(chat_id=query.message.chat.id,
                             text='Auto-messages for this user have been activated.')

    return ConversationHandler.END


def del_mess(update, context):
    """Delete messages for the user"""
    query = update.callback_query
    query.answer()
    user_id = int(query.data)
    user_db.update_one({'user_id': user_id}, {
                       '$set': {'message': []}}, upsert=False)

    # Restart scheduler and update auto-messages
    restart()

    context.bot.send_message(chat_id=query.message.chat.id,
                             text='Auto-messages for this user have been deleted.')

    return ConversationHandler.END


def config(update, context):
    """Get parameters for auto-message"""

    query = update.callback_query
    query.answer()
    user_id = int(query.data)
    context.user_data["user_id"] = user_id

    context.bot.send_message(chat_id=query.message.chat.id,
                             text='Please define the time for the auto-message (00:00 - 23:59): ')

    return TIME


def time(update, context):
    """Get time for auto-message"""

    t = update.message.text
    context.user_data["time"] = t

    if len(t) > 5:
        update.message.reply_text(
            "Please use the following time-format: HH:MM (e.g. 23:59).")
        return TIME

    context.bot.send_message(chat_id=update.message.chat.id,
                             text='Please send the message for the user (text, file, video, audio, image): ')

    return MESSAGE


def message(update, context):
    """Get message (text, video, audio, image) for auto-message"""
    user_id = context.user_data["user_id"]
    time = context.user_data["time"]

    mess = {'text': '',
            'media': '',
            'media_type': '',
            'time': time}

    if update.message.video:
        if update.message.caption:
            mess['text'] = update.message.caption
        else:
            mess['text'] = ''
        mess['media'] = update.message.video.file_id
        mess['media_type'] = 'video'

    elif update.message.photo:
        if update.message.caption:
            mess['text'] = update.message.caption
        else:
            mess['text'] = ''
        mess['media'] = update.message.photo[-1].file_id
        mess['media_type'] = 'photo'

    elif update.message.voice:
        mess['media'] = update.message.voice.file_id
        mess['media_type'] = 'voice'
        mess['text'] = ''

    elif update.message.document:
        mess['media'] = update.message.document.file_id
        mess['media_type'] = 'file'
        mess['text'] = ''

    elif update.message.text:
        mess['media'] = ''
        mess['media_type'] = ''
        mess['text'] = update.message.text

    else:
        context.bot.send_message(chat_id=update.message.chat.id,
                                 text='Oops, something went wrong! The message could not be processed.')

    user = user_db.find_one({'user_id': user_id})
    user_mess = user['message']
    user_mess.append(mess)

    user_db.update_one({'user_id': user_id}, {
                       '$set': {'auto_message': 1, 'message': user_mess}}, upsert=False)

    restart()

    context.bot.send_message(chat_id=update.message.chat.id,
                             text='Changes have been saved.')

    return ConversationHandler.END


def cancel(update, context):
    """End conversation"""
    return ConversationHandler.END

# /echo -> test function


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text('echo echo')

# error callback


def error(update, context):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, context.error)
    return


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # react to commands
    dp.add_handler(CommandHandler("start", reg_user))
    dp.add_handler(CommandHandler("echo", echo))
    # To register as an admin you have to use the passphrase /admin_8753
    # This can be changed to a conversation with password request and even encryption in the future but depends on security requirements
    # this is the "passphrase" to register as an admin
    dp.add_handler(CommandHandler("admin_8753", reg_admin))

    # react to new group
    conv_handler_group = ConversationHandler(
        entry_points=[MessageHandler(
            Filters.status_update.new_chat_members, new_group)],
        states={
            NEW_USER: [CallbackQueryHandler(new_user)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dp.add_handler(conv_handler_group)

    # user config conversation handler
    conv_handler_config = ConversationHandler(
        entry_points=[CommandHandler("config_user", task)],
        states={
            USER: [CallbackQueryHandler(get_user)],
            DELETE: [CallbackQueryHandler(delete)],
            DEACTIVATE: [CallbackQueryHandler(deactivate)],
            ACTIVATE: [CallbackQueryHandler(activate)],
            DEL_MESS: [CallbackQueryHandler(del_mess)],
            CONFIG: [CallbackQueryHandler(config)],
            TIME: [MessageHandler(Filters.text, time)],
            MESSAGE: [MessageHandler(Filters.update, message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(conv_handler_config)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=BOT_TOKEN,
                          webhook_url="https://" + APP_NAME + ".herokuapp.com/" + BOT_TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
