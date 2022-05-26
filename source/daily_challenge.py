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

from bot import bot
from db import User, session, Product


CHALLENGE_READY = "0 8 * * *"
CHALLENGE_OVER = "0 22 * * *"

def start_challenges():
    """Start the daily challenges, read the crontag codes and send messages
    """
    ready_split = CHALLENGE_READY.split(" ")

    over_split = CHALLENGE_OVER.split(" ")

    my_scheduler = BackgroundScheduler()

    my_scheduler.add_job(send_current_event, 'cron'\
                        ,day_of_week = ready_split[4] , hour= ready_split[1] , minute = ready_split[0], month= ready_split[3] , day=ready_split[2]\
                        ,args = ("start", ))
 
    my_scheduler.add_job(send_current_event, 'cron'\
                        ,day_of_week = over_split[4] , hour= over_split[1] , minute = over_split[0], month= over_split[3] , day=over_split[2]\
                        ,args = ("over", ))

    my_scheduler.start()

    time.sleep( 3600 )
    my_scheduler.shutdown()
    start_challenges()



def send_current_event(str_event):
    """Sending the current event at the given crontabs

    Args:
        str_event (String): event to send
    """
    all_users = pandas.DataFrame(session.query(User.telegram_id).all())
    
    if str_event == "start":
        for element in all_users["telegram_id"]:
            bot.send_message(chat_id=int(element), text="Todays challenge is available!\nTry /daily to give it a try :)")
    elif str_event == "over":
        for element in all_users["telegram_id"]:
            bot.send_message(chat_id=int(element), text="Todays challenge is over!\nCheck the /scoreboard to see the leaderboard!")
    else:
        sys.exit(-1)


if __name__ == "__main__":
    try:
        test = pandas.DataFrame(session.query(User.telegram_id).all())
        for element in test["telegram_id"]:
            print(element)
        start_challenges()
        sys.exit(-1)
    except KeyboardInterrupt:
        print("Ending")
        sys.exit(-1)
        