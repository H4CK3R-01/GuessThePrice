"""
script for telegram bot and its functions
"""
__author__ = "Florian Kellermann, Linus Eickhoff, Florian Kaiser"
__date__ = "02.05.2022"
__version__ = "0.4.7"
__license__ = "None"

# main bot at http://t.me/guess_the_price_bot
# debug bot at http://t.me/amazondebug_bot

import logging
import os
import re
import sys
import datetime as dt
import time
from xml.dom.pulldom import START_DOCUMENT
from fuzzywuzzy import fuzz

import sqlalchemy
import telebot
from dotenv import load_dotenv
from telebot import types

from db import User, session, Product, Score
from fetcher import *
import helper_functions as hf
import scoring


load_dotenv(dotenv_path='.env')  # load environment variables

BOT_VERSION = "1.0.0"  # version of bot

START_DAY = dt.time(8, 0, 0)
END_DAY = dt.time(22, 0, 0)

bot = telebot.TeleBot(os.getenv('BOT_API_KEY'))

@bot.message_handler(commands=['version', 'Version'])
def send_version(message):
    """ Sending program version
    Args:
        message (Message): Message to react to in this case /version
    """
    bot.reply_to(message, "the current bot version is " + BOT_VERSION)

@bot.message_handler(commands=['start', 'Start'])
def send_start(message):
    """send start message to user

    Args:
        message (Message): message from telegram user, here /start

    Returns:
        None: None

    Raises:
        None: None

    Test:
        type /start as command in telegram as an unregistered user and check if bot responds with start message and waits for name
        type /start as command in telegram as a registered user and check if bot responds with informing user about being already registered

    """
    if message.from_user.id in session.query(User.telegram_id).all():
        bot.reply_to(message, "You are already registered. Type /changename to change your name or /help for an overview of all commands")
        return

    bot.send_message(chat_id=int(message.from_user.id), text=("Welcome to the game... \
                                                            \nTo start please set a name for yourself or type cancel to set generated name:"))

    bot.register_next_step_handler(message, start_name_setter)


def start_name_setter(message):
    """Set name for user and send introduction

    Args:
        message (Message): Message to react to

    Returns:
        None: None

    Raises:
        None: None

    Test:
        check Regex pattern with incorrect patterns and test if these patterns are denied
        check Regex pattern with correct patterns and test if these patterns are accepted
        check if username is set in database after typing correct name
    """
    user_id = int(message.from_user.id)
    user_name = ""

    if str(message.text).lower() == "cancel":  # Set user name to user
        user_name = "User" + str(user_id) # generate user name, user can change it with /changename

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9\-]+$', str(message.text)): # regex pattern for username: has to start with a letter, can contain letters, numbers and hyphen
        bot.reply_to(message, "Name has to be alphanumeric (including -) and start with a letter")
        return

    user_name = str(message.text)

    try:
        user = User(telegram_id=user_id, username=user_name, admin=False)
        session.add(user) # add user to database
        session.commit() # commit changes to database
        bot.reply_to(message, f"Thank you for setting your name {user_name} \
            \nType /gameinfo for information about GuessThePrice \
            \nType /help for an overview of all commands")

    except sqlalchemy.exc.IntegrityError:
        session.rollback() # rollback changes
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

    Test:
        type /help as command in telegram and check if bot responds with help message
        type /Help <text> as command in telegram and check if bot responds with help message, ignoring the text in message after command
    """
    help_message = ("/me get my user info\n"
                    "/help get this help message\n"
                    "/gameinfo get game info\n"
                    "/scoreboard get scoreboard\n"
                    "/changename change your name\n"
                    "/daily get todays challenge\n"
                    "/setAdmin set admin status of user (ADMIN)\n"
                    "/addproduct add product for further challenges (ADMIN)\n"
                    "/users get all users (ADMIN)\n")
    bot.reply_to(message, help_message)


@bot.message_handler(commands=['gameinfo', 'Gameinfo'])
def send_gameinfo(message):
    """send game info to user

    Args:
        message (Message): Message from telegram user, here /gameinfo

    Returns:
        None: None

    Raises:
        None: None

    Test:
        type /gameinfo or /Gameinfo as command in telegram and check if bot responds with game info message
        type /gameInfo as command in telegramand check if bot responds with unknown command message

    """
    gameinfo_message = ("GuessThePrice is a game where you have to guess\n"
                        "the price of an amazon product.\n"
                        "Start by setting your name with /changename\n"
                        "You can get a new challenge every day.\n"
                        "You are informed when a new challenge is available.\n"
                        "To see the challenge type /daily\n"
                        "At 10pm the correct answer will be shown\n"
                        "See /scoreboard to see how you perform")
    bot.reply_to(message, gameinfo_message)


@bot.message_handler(commands=['me', 'Me'])
def send_user_info(message):
    """send user info to user

    Args:
        message (Message): Message from telegram user, here /me

    Returns:
        None: None

    Raises:
        None: None

    Test:
        type /me as command in telegram as an registered User and check if bot responds with user info message
        type /me as command in telegram as an unregistered User and check if bot responds with User does not exist message


    """
    user_id = message.from_user.id
    user = session.query(User).filter(User.telegram_id==user_id).first() # get user from database, only one user per telegram id exists
    user_scores = session.query(Score).filter(Score.telegram_id==user_id).all() # get today's score object for user

    today_score = None
    today_guess = None

    for score in user_scores:
        if score.date.date() == dt.datetime.now().date(): # check if today's score is already in database
            today_score = score.score
            today_guess = score.guess

    if today_guess is None:
        today_guess = "No guess today"
    else:
        today_guess = str(today_guess) + "€"

    if today_score is None:
        today_score = "No score today"

    if today_score is not None and today_guess is not None:
        all_time_score = sum(score.score for score in user_scores)
    else:
        all_time_score = "No score yet"


    if user is not None: # if user is registered
        user_name = user.username
        user_info = (f"Your user info:\n"
                     f"User ID: {user_id}\n"
                     f"Username: {user_name}\n"
                     f"Today's guess: {today_guess}\n"
                     f"Today's Score: {today_score}\n"
                     f"All time Score: {all_time_score}")

    else: # if user is not registered
        # User not found
        user_info = "User does not exist.\nDo /start to register"

    bot.reply_to(message, user_info)


@bot.message_handler(commands=['users', 'Users'])
def send_users(message):
    """send user info to user

    Args: (Message): Message from telegram user, here /users

    Returns:
        None: None

    Raises:
        None: None

    Test:
        type /users as command in telegram as an registered Admin and check if bot responds with user info messages
        type /users as command in telegram as an an registered User where Admin = False and check if bot responds with "Admin rights are required to see all users" message
        type /users as command in telegram as an an unregistered User and check if bot responds with "Admin rights are required to see all users" message

    """
    user_id = message.from_user.id

    # check if user exists
    user = session.query(User).filter(User.telegram_id==user_id).first()
    if not user or user is None: # should never happen, /start is required to chat, but just in case
        bot.reply_to(message, "Error: You are not registered, please register with /start")
        return

    # Check if user is admin
    if not session.query(User).filter(User.telegram_id==user_id).first().admin: # if user is not admin
        bot.reply_to(message, "Error: Admin rights are required to see all users.")
        return

    users = session.query(User).all()

    if len(users) == 0:
        bot.reply_to(message, "No users registered.")

    for user in users:
        user_info = (f"Telegram ID: {user.telegram_id}\n"
                        f"Username: {user.username}\n"
                        f"Admin: {user.admin}\n")
        bot.reply_to(message, user_info)



@bot.message_handler(commands=['setAdmin', 'SetAdmin', 'Setadmin', 'setadmin'])
def set_admin(message):
    """set admin status of user

    Args:
        message (Message): Message from telegram user, here /setAdmin

    Returns:
        None: None

    Raises:
        None: None

    Test:
        type /setAdmin as command in telegram as an registered Admin and check if bot requests id and boolean for changing admin status
        type /setAdmin as command in telegram as an an registered User where Admin = False in db and check if bot responds with "Admin rights are required to change admin status" message
        type /setAdmin as command in telegram as an an unregistered User and check if bot responds with "Admin rights are required to change admin status" message

    """
    user_id = message.from_user.id

    try:

        user = session.query(User).filter(User.telegram_id==user_id).first()

        if not user.admin: # admin is a boolean
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

    Args:
        message (Message): Message from telegram user, here /setAdmin

    Returns:
        None: None

    Raises:
        None: None

    Test:
        type in correct regex pattern and check if bot sets admin status of user correctly
        type in wrong regex pattern and check if bot responds with Invalid format message
        test with incorrect user id and check if bot responds with User not registered message

    """
    if not re.match(r'[0-9]* (True|False|true|false)', str(message.text)):
        bot.reply_to(message, "Error: Invalid format. Try again with /setAdmin")
        return

    telegram_id, admin = str(message.text).split(sep=" ")
    user = session.query(User).filter(User.telegram_id==telegram_id).first() # get user from database, only one user per telegram id exists

    if user is None or not user:
        bot.reply_to(message, "Error: User with entered telegram id is not registered.")
        return

    try:
        if admin in ("True", "true"):
            user.admin = True

        elif admin in ("False", "false"):
            user.admin = False

        session.commit() # commit changes to database
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

    Test:
        type /scoreboard as command in telegram and check if bot responds with scoreboard with correct info and formatting
        test with db with no Users and check if bot responds with "No users registered" message


    """
    alltime_board = []
    weekly_board = []

    users = session.query(User).all()

    if users is None:
        bot.reply_to(message, "No users registered.")
        return

    # generate alltime scoreboard
    for user in users:
        telegram_id = user.telegram_id
        user_scores = session.query(Score).filter(Score.telegram_id==telegram_id).all() # get all scores of user

        if user_scores is None:
            continue

        alltime_score = sum(score.score for score in user_scores) # sum all scores of user
        alltime_board.append((user.username, alltime_score)) # append to alltime scoreboard

    # generate weekly scoreboard
    for user in users:
        telegram_id = user.telegram_id
        print(session.query(Score).all())
        all_user_scores = session.query(Score).filter(Score.telegram_id==telegram_id).all() # get all user scores
        user_scores = None # initialize variable

        if all_user_scores is not None:
            user_scores = [score for score in all_user_scores if score.date.date().isocalendar().week==dt.date.today().isocalendar().week] # get user scores for today

        if user_scores is None:
            continue

        weekly_score = sum(score.score for score in user_scores)
        weekly_board.append((user.username, weekly_score))

    # sort scoreboards
    alltime_board.sort(key=lambda x: x[1], reverse=True)
    weekly_board.sort(key=lambda x: x[1], reverse=True)

    str_alltime_board = "*Scoreboard (AllTime)*:\n"
    str_weekly_board = "*Scoreboard (Weekly)*:\n"

    for user in alltime_board:
        str_alltime_board += f"\n{user[1]} _({user[0]})_"

    if len(alltime_board) == 0:
        bot.reply_to(message, str_alltime_board + "\nNo users have scored yet.", parse_mode='MARKDOWN')

    else:
        bot.reply_to(message, str_alltime_board, parse_mode='MARKDOWN')

    for user in weekly_board:
        str_weekly_board += f"\n{user[1]} _({user[0]})_"

    if len(weekly_board) == 0:
        bot.reply_to(message, str_weekly_board + "\nNo users have scored yet.", parse_mode='MARKDOWN')

    else:
        bot.reply_to(message, str_weekly_board, parse_mode='MARKDOWN')


@bot.message_handler(commands=['changename', 'Changename'])
def change_name(message):
    """change user name

    Args:
        message (Message): Message from telegram user, here /changename

    Returns:
        None: None

    Raises:
        None: None

    Test:
        type /changename as command in telegram and check if bot sends change name request message
        type /Changename as command in telegram and check if bot sends change name request message
    """

    bot.reply_to(message, "type new name (else type \"cancel\"):")
    bot.register_next_step_handler(message, change_name_setter) # register next step handler, send message and take users answer as input for change_name_setter


def change_name_setter(message):
    """change user name

    Args:
        message (Message): Message to react to

    Returns:
        None: None

    Raises:
        None: None

    Test:
        type in correct regex pattern and check if bot changes user name correctly, also in db
        type in wrong regex pattern and check if bot responds with Invalid format message
        type cancel and check that name is not changed in db and bot responds with "Name not changed" message

    """

    if str(message.text).lower() == "cancel":  # Set user name to user
        bot.reply_to(message, "Name not changed")
        return

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9\-]+$', str(message.text)): # same pattern as in /start
        bot.reply_to(message, "Name has to be alphanumeric (including -) and start with a letter")
        return

    else:
        user_id = int(message.from_user.id)
        user_name = str(message.text)
        try:
            user = session.query(User).filter(User.telegram_id==user_id).first()
            user.username = user_name
            session.commit()
            bot.reply_to(message, f"Your name has been changed to {user_name}")

        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            bot.reply_to(message, "Something went wrong")


def time_in_range(start, end, current):
    """ Check if current time is in range of start and end

    Args:
        start (datetime): start time
        end (datetime): end time
        current (datetime): current time

    Returns:
        bool: True if current time is in range of start and end, False otherwise

    """
    return start <= current <= end

def find_todays_product_from_db():
    """Find todays product from db based on todays_product
    """
    product = None
    for element in session.query(Product).all():
        if element.todays_product:
            product = element
            break
    return product

@bot.message_handler(commands=['daily', 'Daily'])
def daily_message(message):
    """send daily challenge

    Args:
        message (Message): Message from telegram user, here /daily

    Returns:
        None: None

    Raises:
        None: None

    Test:
        type /daily as command in telegram and check if bot sends daily challenge message
        type /daily again for message that you already played today and your guess

    """
    user_id = int(message.from_user.id)

    current = dt.datetime.now().time()

    if not time_in_range(START_DAY, END_DAY, current):
        bot.send_message(chat_id=user_id, text="Currently there is no challenge.\n\n"
                                               "Times are 8am to 10pm.")
        return


    # Check if user already guessed today by date, time and user_id
    all_scores_user = session.query(Score).filter(
        Score.telegram_id==user_id
        ).all()

    for element in all_scores_user:
        if element.date.date() == dt.datetime.now().date():
            bot.send_message(chat_id=user_id, text="You already guessed today!\n"
                             "Your guess was: {}".format(element.guess))
            return


    bot.send_message(chat_id = user_id, text="Welcome to todays challenge!\n"
                                             "As soon as the picture loads\n"
                                             "you will have 20 seconds to send\n"
                                             "your price guess\n")

    time.sleep(2)

    bot.send_message(chat_id = user_id, text="Lets Go!")

    time.sleep(1)

    for i in range(3):
        iteration = 3-i
        bot.send_message(chat_id=user_id, text=str(iteration))
        iteration-=1
        time.sleep(1)

    try:
        product_for_today=find_todays_product_from_db()
        bot.send_message(chat_id=user_id, text=str(
            hf.make_markdown_proof(product_for_today.image_link)
            ), parse_mode="MARKDOWNV2")
        bot.send_message(chat_id=user_id, text=product_for_today.title)
        start_time = time.time()

        # next step with message and start time
        bot.register_next_step_handler(message, get_user_guess, start_time)

    except (TypeError, AttributeError) as exception_message:
        print(exception_message)
        bot.send_message(chat_id=user_id, text="An Error occured. Please try again later.")

def get_time_difference(start_time, end_time):
    """Get time difference
    """
    return end_time - start_time

def get_user_guess(message, start_time):
    """Get users guess after typing /daily

    Args:
        message (Message): Message element to react to. In this case next step after /daily
        start_time (time.time): Time the user got the image

    Test:
        Send a price and see if the bot responds correctly (guess accepted)
        Send text withwith wrong format (right format = number fitting for float) and see if bot notices and gives you another try
        See if score changes after you guessed (only if you guessed somewhat correctly so your score is not 0)
    """
    end_time = time.time()
    user_id = int(message.from_user.id)
    over_time = False #If user guesses to slow (> 20 seconds)

    try:
        user_guess = float(message.text.replace( ',', '.'))
    except ValueError:
        bot.send_message(chat_id=user_id, text="Please type a number or float")
        bot.register_next_step_handler(message, get_user_guess, start_time)
        return

    if get_time_difference(start_time, end_time) > 20:
        bot.send_message(chat_id=user_id, text="You took too long to guess.\n"
                                                       "No more tries today.")
        over_time = True # user guesses to slow

    product_for_today=find_todays_product_from_db()

    if not over_time: # when answer was in time
        message_text=f"You guessed {round(user_guess,2)}€"
        bot.send_message(chat_id=user_id, text = message_text)

    # calculate score for guess
    if not over_time:
        user_score = scoring.eval_score(product_for_today.price, user_guess)
    else:
        user_score = 0
        user_guess = 0

    score = Score (
        telegram_id = user_id,
        date = dt.date.today(),
        product_id = product_for_today.product_id,
        guess = user_guess,
        score = user_score
    )
    session.add(score)
    session.commit()


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
    if not session.query(User).filter(User.telegram_id == user_id).first().admin:
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
    image_url = get_image(product_src)
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
    except pymysql.err.OperationalError:
        session.rollback()
        bot.send_message(chat_id=user_id, text='Unknown error')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        bot.answer_callback_query(call.id, "Answer is Yes")
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is No")

@bot.message_handler(func=lambda message: True)  # Returning that command is unknown for any other statement
def echo_all(message):
    """Echo all other messages

    Args:
        message (Message): user message that doesnt match any of the commands
    """
    user_id = int(message.from_user.id)

    possible_commands = ['/addproduct', '/daily', '/help', '/me', '/gameinfo', '/scoreboard', '/changename', '/setadmin', '/users', ] # all possible commands
    matching_commands = []

    for command in possible_commands:
        print(fuzz.ratio(command, message.text))
        if fuzz.ratio(command, message.text) > 79: # If word is similar enough for suggestion
            matching_commands.append(command)


    answer = 'Do not know this command or text: ' + message.text
    bot.reply_to(message, answer)

    # send all possible matches
    if len(matching_commands)>0:
        bot.send_message(chat_id=user_id, text='Did you mean: ' + ', '.join(matching_commands))


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
