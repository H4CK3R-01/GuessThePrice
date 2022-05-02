"""
script for telegram bot and its functions
"""
__author__ = "Florian Kellermann, Linus Eickhoff, Florian Kaiser"
__date__ = "02.05.2022"
__version__ = "0.0.1"
__license__ = "None"

# main bot at http://t.me/guess_the_price_bot
# debug bot at http://t.me/amazondebug_bot

import logging
import os
import sys

import telebot
from dotenv import load_dotenv
from telebot import types
# from apscheduler.schedulers.background import BackgroundScheduler

# from db import User, session

load_dotenv(dotenv_path='.env')  # load environment variables

BOT_VERSION = "0.0.1"  # version of bot

bot = telebot.TeleBot(os.getenv('BOT_API_KEY'))


@bot.message_handler(commands=['start', 'Start'])
def send_start(message):
    """send start message to user

    Args:
        message (Message): message from telegram user, here /start
    """
    bot.reply_to(message, "Welcome to this amazon prices guesser bot")


telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['help', 'Help'])
def send_help(message):
    """send all commands to user

    Args:
        message (Message): Message from telegram user, here /help

    Returns:
        None: None

    Raises:
        None: None

    """
    bot.reply_to(message, "This is the help message")


@bot.inline_handler(lambda query: query.query == 'text')  # inline prints for debugging
def query_text(inline_query):
    """ Output in the console about current user actions and status of bot
    :type inline_query:
    :param inline_query:

    :raises: none

    :rtype: none
    """
    try:
        r = types.InlineQueryResultArticle('1', 'Result1', types.InputTextMessageContent('hi')) # pylint: disable=invalid-name
        r2 = types.InlineQueryResultArticle('2', 'Result2', types.InputTextMessageContent('hi')) # pylint: disable=invalid-name
        bot.answer_inline_query(inline_query.id, [r, r2])
    except Exception as e: # pylint: disable=broad-except, invalid-name
        print(e)


def main_loop():
    """ Start bot
    :raises: none

    :rtype: none
    """
    bot.infinity_polling()


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)
