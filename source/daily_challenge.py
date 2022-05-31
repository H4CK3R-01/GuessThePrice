"""
script for sending daily challenges
"""
__author__ = "Florian Kellermann, Linus Eickhoff, Florian Kaiser"
__date__ = "09.05.2022"
__version__ = "0.0.1"
__license__ = "None"


import time
import sys
import pandas
import random
import datetime as dt
from apscheduler.schedulers.background import BackgroundScheduler


from bot import bot
from db import User, session, Product, Score

CHALLENGE_READY = "0 8 * * *"
CHALLENGE_OVER = "0 22 * * *"
USER_REMINDER = "0 19 * * *"
GET_NEW_PRODUCT = "0 0 * * *"

def start_challenges():
    """Start the daily challenges, read the crontag codes and send messages
    """
    ready_split = CHALLENGE_READY.split(" ")

    over_split = CHALLENGE_OVER.split(" ")

    new_product_split = GET_NEW_PRODUCT.split(" ")

    reminder_split = USER_REMINDER.split(" ")

    my_scheduler = BackgroundScheduler()

    # Sending the current event at the given crontags
    # Challenge ready
    my_scheduler.add_job(send_current_event, 'cron'\
                        , day_of_week = ready_split[4] \
                        , hour= ready_split[1] \
                        , minute = ready_split[0]\
                        , month= ready_split[3] \
                        , day=ready_split[2]\
                        ,args = ("start", ))

    # Challenge over
    my_scheduler.add_job(send_current_event, 'cron'\
                        , day_of_week = over_split[4] \
                        , hour= over_split[1] \
                        , minute = over_split[0]\
                        , month= over_split[3] \
                        , day=over_split[2]\
                        ,args = ("over", ))

    # Get new product
    my_scheduler.add_job(set_todays_product, 'cron'\
                        ,day_of_week = new_product_split[4] \
                        , hour= new_product_split[1] \
                        , minute = new_product_split[0]\
                        , month= new_product_split[3]\
                        , day=new_product_split[2])

    my_scheduler.add_job(remind_users, 'cron'\
                        ,day_of_week = reminder_split[4] \
                        , hour= reminder_split[1] \
                        , minute = reminder_split[0]\
                        , month= reminder_split[3]\
                        , day=reminder_split[2])

    my_scheduler.start()

    time.sleep( 3600 )
    my_scheduler.shutdown()
    start_challenges()

def remind_users():
    """Remind users if they havent played until 7pm
    """
    all_users = pandas.DataFrame(session.query(User.telegram_id).all())
    guessed_today = False

    for user in all_users["telegram_id"]:
        guessed_today = False
        user_guesses = session.query(Score).filter(Score.telegram_id == user).all()
        for guesses in user_guesses:
            if guesses.date.date() == dt.datetime.now().date():
                guessed_today = True
                break
        if not guessed_today:
            bot.send_message(chat_id=user, text="REMINDER: You haven't guessed today!\n"\
                                                     "There are 3 Hours left. Good Luck :)\n"\
                                                     "/daily")


def set_todays_product():
    """Get a random product from the database

    Returns:
        Product: random product
    """

    # Find old product and set todays_product false

    products = []
    for element in session.query(Product).all():
        if element.todays_product:
            element.todays_product = False
            session.commit()
            products.append(element)
        else:
            products.append(element)

    # choose random product
    random_product = products[int(len(products) * random.random())]

    # find product_id in db and delete element
    session.query(Product).filter(Product.product_id == random_product.product_id).update({'todays_product': True})
    session.commit()


def send_current_event(str_event):
    """Sending the current event at the given crontabs

    Args:
        str_event (String): event to send
    """
    all_users = pandas.DataFrame(session.query(User.telegram_id).all())

    if str_event == "start":
        for element in all_users["telegram_id"]:
            bot.send_message(chat_id=int(element), text="Todays challenge is available!\n"\
                                                        "Try /daily to give it a try :)")
    elif str_event == "over":
        product_today = find_todays_product_from_db()
        for element in all_users["telegram_id"]:
            user_guesses = session.query(Score).filter(Score.telegram_id == element).all()
            user_guess, user_score = 0, 0
            for guesses in user_guesses: # find todays guess and score
                if guesses.date.date() == dt.datetime.now().date():
                    user_guess = guesses.guess
                    user_score = guesses.score
            bot.send_message(chat_id=int(element), text="Todays challenge is over!\n"\
                                                    "The correct price is: " + str(product_today.price) + "€\n"\
                                                    "Your guess was: " + str(user_guess) + "€\n"\
                                                    "Your score was: " + str(user_score) + "\n"\
                                                    "Check the /scoreboard to see the leaderboard!")
    else:
        sys.exit(-1)

def find_todays_product_from_db():
    """Find todays product from db based on todays_product
    """
    product = None
    for element in session.query(Product).all():
        if element.todays_product:
            product = element
            break
    return product

if __name__ == "__main__":
    set_todays_product()
    try:
        start_challenges()
        sys.exit(-1)
    except KeyboardInterrupt:
        print("Ending")
        sys.exit(-1)
