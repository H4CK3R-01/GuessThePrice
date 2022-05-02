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
    bot.reply_to(message, ( "Welcome to the game...\n"
                            "To start set a name by typing /changename\n"
                            "Type /gameinfo for information about GuessThePrice\n"
                            "Type /help for an overview of all commands\n"))


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
    help_message = ("/me get my user info\n"
                    "/help get this help message\n"
                    "/gameinfo get game info\n"
                    "/scoreboard get scoreboard\n"
                    "/changename change your name\n"
                    "/challenge get todays challenge\n"
                    "/guess make guess for today")
    bot.reply_to(message, help_message, parse_mode='MARKDOWN')


@bot.message_handler(commands=['gameinfo', 'Gameinfo'])
def send_gameinfo(message):
    """send game info to user

    Args:
        message (Message): Message from telegram user, here /gameinfo

    Returns:
        None: None

    Raises:
        None: None

    """
    gameinfo_message = ("GuessThePrice is a game where you have to guess\n"
                        "the price of an amazon product.\n"
                        "Start by setting your name with /changename\n"
                        "You can get a new challenge every day.\n"
                        "You are informed when a new challenge is available.\n"
                        "To see the challenge type /challenge\n"
                        "To guess the price type /guess\n"
                        "At 22:00 pm the scores and answer will be shown\n")
    bot.reply_to(message, gameinfo_message, parse_mode='MARKDOWN')


@bot.message_handler(commands=['me', 'Me'])
def send_user_info(message):
    """send user info to user

    Args:
        message (Message): Message from telegram user, here /me

    Returns:
        None: None

    Raises:
        None: None

    """
    user_id = message.from_user.id
    user_name = "" # tbd: get user name by id from db
    user_score = 0 # tbd: get user score by adding all scores related to userid
    user_guess = 0.0 # tbd: display if user has guessed today and how much
    user_info = (f"Your user info:\n"
                 f"User ID: {user_id}\n"
                 f"Username: {user_name}\n"
                 f"Today's guess: {user_guess}\n"
                 f"Your Score: {user_score}\n")

    bot.reply_to(message, user_info, parse_mode='MARKDOWN')


@bot.message_handler(commands=['scoreboard', 'Scoreboard'])
def send_scoreboard(message):
    """send scoreboard to user

    Args:
        message (Message): Message from telegram user, here /scoreboard

    Returns:
        None: None

    Raises:
        None: None

    """
    bot.reply_to(message, "Scoreboard not implemented yet")


@bot.message_handler(commands=['challenge', 'Challenge'])
def send_challenge(message):
    """send challenge to user

    Args:
        message (Message): Message from telegram user, here /challenge

    Returns:
        None: None

    Raises:
        None: None

    """
    bot.reply_to(message, "Challenge not implemented yet")


@bot.message_handler(commands=['guess', 'Guess'])
def send_guess(message):
    """send guess to user

    Args:
        message (Message): Message from telegram user, here /guess

    Returns:
        None: None

    Raises:
        None: None

    """
    bot.reply_to(message, "Guess not implemented yet")


@bot.message_handler(commands=['changename', 'Changename'])
def change_name(message):
    """change user name

    Args:
        message (Message): Message from telegram user, here /changename

    Returns:
        None: None

    Raises:
        None: None

    """
    bot.reply_to(message, "change name not implemented yet")


# inline prints for debugging
@bot.inline_handler(lambda query: query.query == 'text')
def query_text(inline_query):
    """inline query handler for debugging

    Args:
        inline_query (InlineQuery): inline query from telegram user

    Returns:
        None: None

    Raises:
        None: None
    """
    try:
        r = types.InlineQueryResultArticle('1', 'Result1', types.InputTextMessageContent(
            'hi'))  # pylint: disable=invalid-name
        r2 = types.InlineQueryResultArticle(
            '2', 'Result2', types.InputTextMessageContent('hi'))  # pylint: disable=invalid-name
        bot.answer_inline_query(inline_query.id, [r, r2])
    except Exception as e:  # pylint: disable=broad-except, invalid-name
        print(e)


def main_loop():
    # nur zum ärgern
    """main loop for bot

    Args:
        None: None

    Returns:
        None: None

    Raises:
        None: None
    """
    bot.infinity_polling()


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)
