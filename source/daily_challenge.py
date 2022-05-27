"""
script for sending daily challenges
"""
__author__ = "Florian Kellermann, Linus Eickhoff, Florian Kaiser"
__date__ = "09.05.2022"
__version__ = "0.0.1"
__license__ = "None"


import time
import sys
from apscheduler.schedulers.background import BackgroundScheduler
import pandas
import random

from bot import bot
from db import User, session, Product


CHALLENGE_READY = "0 8 * * *"
CHALLENGE_OVER = "0 22 * * *"
GET_NEW_PRODUCT = "0 0 * * *"

def start_challenges():
    """Start the daily challenges, read the crontag codes and send messages
    """
    ready_split = CHALLENGE_READY.split(" ")

    over_split = CHALLENGE_OVER.split(" ")

    new_product_split = GET_NEW_PRODUCT.split(" ")

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
    my_scheduler.add_job(get_todays_product, 'cron'\
                        ,day_of_week = new_product_split[4] \
                        , hour= new_product_split[1] \
                        , minute = new_product_split[0]\
                        , month= new_product_split[3]\
                        , day=new_product_split[2])

    my_scheduler.start()

    time.sleep( 3600 )
    my_scheduler.shutdown()
    start_challenges()

def get_todays_product():
    """Get a random product from the database

    Returns:
        Product: random product
    """
    products = []
    for element in session.query(Product).all():
        products.append(element)

    # choose random product
    random_product = products[int(len(products) * random.random())]

    return random_product


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
        for element in all_users["telegram_id"]:
            bot.send_message(chat_id=int(element), text="Todays challenge is over!\n"\
                                                    "Check the /scoreboard to see the leaderboard!")
    else:
        sys.exit(-1)


if __name__ == "__main__":
    send_current_event("start")
    time.sleep(10)

    try:
        start_challenges()
        sys.exit(-1)
    except KeyboardInterrupt:
        print("Ending")
        sys.exit(-1)
