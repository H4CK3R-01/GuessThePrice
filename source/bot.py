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
import re
import sys
import datetime as dt
import time

import sqlalchemy
import telebot
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from telebot import types
from random import randrange
from apscheduler.schedulers.background import BackgroundScheduler
import pandas

from db import User, session, Product
from fetcher import *
from db import Score


load_dotenv(dotenv_path='.env')  # load environment variables

BOT_VERSION = "0.0.1"  # version of bot
UPDATE_PRODUCT = "0 1 * * *"

bot = telebot.TeleBot(os.getenv('BOT_API_KEY'))


@bot.message_handler(commands=['start', 'Start'])
def send_start(message):
    """send start message to user

    Args:
        message (Message): message from telegram user, here /start
    """
    bot.send_message(chat_id=int(message.from_user.id), text=("Welcome to the game... \
                                                            \nTo start please set a name for yourself or type cancel to set generated name:"))

    bot.register_next_step_handler(message, start_name_setter)


def start_name_setter(message):
    """Set name for user and send introduction

    Args:
        message (Message): Message to react to
    """
    user_id = int(message.from_user.id)
    user_name = ""

    if str(message.text).lower() == "cancel":  # Set user name to user
        user_name = "User" + str(user_id) # generate user name, user can change it with /changename

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_\-]+$', str(message.text)):
        bot.reply_to(message, "Name has to be alphanumeric (including underscores) and start with a letter")
        return
    
    user_name = str(message.text)

    try:
        user = User(telegram_id=user_id, username=user_name, admin=False)
        session.add(user)
        session.commit()
        bot.reply_to(message, f"Thank you for setting your name {user_name} \
            \nType /gameinfo for information about GuessThePrice \
            \nType /help for an overview of all commands")

    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        bot.reply_to(message, "You are already registered, change name with /changename")


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
                    "/daily make guess for today")
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
    user = session.query(User).filter_by(telegram_id=user_id).first()
    scores = session.query(Score).filter_by(telegram_id=user_id).all()

    if user is not None:
        user_name = user.username  # tbd: get user name by id from db
        user_score = sum(score for score in scores)  # tbd: get user score by adding all scores related to userid
        user_guess = session.query(Score).filter_by(date=dt.datetime.now(), telegram_id=user_id).first().guess or "not guessed today" # tbd: display if user has guessed today and how much
        user_info = (f"Your user info:\n"
                     f"User ID: {user_id}\n"
                     f"Username: {user_name}\n"
                     f"Today's guess: {user_guess}\n"
                     f"Your Score: {user_score}\n")
    else:
        # User not found
        user_info = "User does not exist."

    bot.reply_to(message, user_info, parse_mode='MARKDOWN')


@bot.message_handler(commands=['setAdmin', 'SetAdmin', 'Setadmin', 'setadmin'])
def set_admin(message):
    """set admin status of user

    Args:
        message (Message): Message from telegram user, here /setAdmin

    Returns:
        None: None

    Raises:
        None: None

    """
    user_id = message.from_user.id

    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()

        if not user.admin:
            bot.reply_to(message, "Error: Admin rights are required to change admin rights of users.")
            return

        if user.admin:
            bot.reply_to(message, "Type the telegram_id and boolean of admin attribute like <telegram_id> <value>")
            bot.register_next_step_handler(message, set_admin_handler)

    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        bot.reply_to(message, "Something went wrong.")


def set_admin_handler(message):
    """set admin status of user

    Args: message (Message): Message from telegram user, here /setAdmin

    Returns: None: None

    Raises: None: None

    """
    if not re.match(r'[0-9]* (True|False|true|false)', str(message.text)):
        bot.reply_to(message, "Error: Invalid format. Try again with /setAdmin")
        return

    telegram_id, admin = str(message.text).split(sep=" ")
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user is None:
        bot.reply_to(message, "Error: User with entered telegram id is not registered.")
        return

    try:
        if admin in ("True", "true"):
            user.admin = True

        elif admin in ("False", "false"):
            user.admin = False

        session.commit()
        bot.reply_to(message, f"Admin rights of user {user.username} set to {user.admin}")

    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        bot.reply_to(message, "Something went wrong")


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

    bot.reply_to(message, "type new name (else type \"cancel\"):")
    bot.register_next_step_handler(message, change_name_setter)
    
@bot.message_handler(commands=['daily', 'Daily'])
def daily_message(message):
    """change user name

    Args:
        message (Message): Message from telegram user, here /changename

    Returns:
        None: None

    Raises:
        None: None

    """
    user_id = int(message.from_user.id)
    
    bot.send_message(chat_id = user_id, text="Welcome to todays challenge!\n"
                                             "As soon as the picture loads\n"
                                             "you will have 35 seconds to send\n"
                                             "your price guess\n")
    
    time.sleep(2)
    
    bot.send_message(chat_id = user_id, text="Lets Go!")
    
    time.sleep(1)
    
    for i in range(3):
        iteration = 3-i
        bot.send_message(chat_id=user_id, text=str(iteration))
        iteration-=1
        time.sleep(1)
    


def change_name_setter(message):
    """change user name

    Args:
        message (Message): Message to react to

    Returns:
        None: None

    Raises:
        None: None

    """

    if str(message.text).lower() == "cancel":  # Set user name to user
        bot.reply_to(message, "Name not changed")
        return

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_\-]+$', str(message.text)):
        bot.reply_to(message, "Name has to be alphanumeric (including underscores) and start with a letter")
        return

    else:
        user_id = int(message.from_user.id)
        user_name = str(message.text)
        try:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            user.username = user_name
            session.commit()
            bot.reply_to(message, f"Your name has been changed to {user_name}")

        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            bot.reply_to(message, "Something went wrong")


@bot.message_handler(commands=['addproduct', 'Addproduct'])
def add_product(message):
    """Add product to database

    Args:
        message (Message): Message from telegram user, here /addproduct

    Returns:
        None: None

    Raises:
        None: None

    """
    user_id = message.from_user.id

    # Check if user is admin
    if not session.query(User).filter_by(telegram_id=user_id).first().admin:
        bot.reply_to(message, "Error: Admin rights are required to add products")
        return

    user_id = int(message.from_user.id)
    bot.send_message(chat_id=user_id, text='Please insert the Amazon product id (i.e. B00XKZYZ2S)')
    bot.register_next_step_handler(message, receive_product_data)  # executes function when user sends message


def receive_product_data(message):
    """ registering new product in the db and fetching it from amazon

    Args:
        message (Message): Message that is being reacted to. Always from add_product because of next_step_handler
    """
    user_id = int(message.from_user.id)
    product_id = str(message.text)

    product_src = fetch_url('https://www.amazon.de/dp/' + product_id)

    title = get_title(product_src)
    image_url = get_image(product_src, get_title(product_src))
    price = get_price(product_src)
    description = get_description(product_src)

    bot.send_message(chat_id=user_id, text=title)
    bot.send_message(chat_id=user_id, text=image_url)
    bot.send_message(chat_id=user_id, text=price)
    bot.send_message(chat_id=user_id, text=description)

    # markup = InlineKeyboardMarkup()
    # markup.row_width = 2
    # markup.add(InlineKeyboardButton("Yes", callback_data="cb_yes"),
    #            InlineKeyboardButton("No", callback_data="cb_no"))
    #
    # bot.send_message(chat_id=user_id, text="Is this the product you want to add?", reply_markup=markup)

    # Insert into database
    try:
        product = Product(
            product_id=product_id,
            title=title,
            image_link=image_url,
            price=price[0],
            currency=price[1],
            description=description
        )
        session.add(product)
        session.commit()

        bot.send_message(chat_id=user_id, text='Successfully added product to database')
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        bot.send_message(chat_id=user_id, text='Product is in database already')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        bot.answer_callback_query(call.id, "Answer is Yes")
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is No")


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
    # nur zum ärgern -> sympathisch :D 
    """main loop for bot

    Args:
        None: None

    Returns:
        None: None

    Raises:
        None: None
    """
    product_split = UPDATE_PRODUCT.split(" ")
    my_scheduler = BackgroundScheduler()
    my_scheduler.add_job(get_todays_product, 'cron'\
                        ,day_of_week = product_split[4]\
                        ,hour= product_split[1]\
                        ,minute = product_split[0]\
                        ,month= product_split[3]\
                        ,day=product_split[2])
    
    bot.infinity_polling()
    
def get_todays_product():
    """Setting product for this day
    """
    print(pandas.DataFrame(session.query(Product.price,Product.image_link).all()))


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)
