"""
script for sending daily challenges
"""
__author__ = "Florian Kellermann, Linus Eickhoff, Florian Kaiser"
__date__ = "09.05.2022"
__version__ = "0.0.1"
__license__ = "None"


import sys
from apscheduler.schedulers.background import BackgroundScheduler
import time

from bot import bot
from db import User, session, Product
import pandas


CHALLENGE_READY = "0 10 * * *"
CHALLENGE_OVER = "0 20 * * *"

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
    all_users = pandas.DataFrame(session.query(User).all())
    
    user_ids = all_users.query["telegram_id"]
    
    for element in all_users:
        print("tbd")
    
    if str_event == "start":
        print("tbd")
    elif str_event == "over":
        print("tbd")
    else:
        sys.exit(-1)


if __name__ == "__main__":
    try:
        test = pandas.DataFrame(session.query(User).all())
        print(test)
        start_challenges()
        sys.exit(-1)
    except KeyboardInterrupt:
        print("Ending")
        sys.exit(-1)
        