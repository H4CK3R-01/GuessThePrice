"""
script with functions for evaluating scores of users
"""
__author__ = "Florian Kellermann, Linus Eickhoff, Florian Kaiser"
__date__ = "02.05.2022"
__version__ = "0.0.1"
__license__ = "None"

import pandas as pd
import plotly.express as px


def eval_score(price, guess):
    """calculate the score of a user

    Args:
        price (float): price of the product
        guess (float): guess of the user
    
    Returns:
        float: score of the user

    """
    price = float(price)
    guess = float(guess)

    diff = abs(price - guess) # difference between price and guess in absolute value (e.g.: |-5| = 5)
    rel = diff / price

    if rel > 2: # guess extremely off -> 0 points
        return 0

    score = (1.0 - rel/2)*1000.0
    score = round(score) # round to nearest integer

    return score


def get_relative_deviation(price, guess):
    """calculate the relative deviation of a guess

    Args:
        price (float): price of the product
        guess (float): guess of the user

    Returns:
        float: relative deviation of the guess (take times hundred for percentage)

    """
    price = float(price)
    guess = float(guess)

    diff = abs(price - guess) # difference between price and guess in absolute value (e.g.: |-5| = 5)
    deviation = diff / price # formula for relative deviation: (price - guess) / price

    return deviation


def plot_linegraph(x_data, y_data):
    """plot the score to test score function

    Args:
        x_data (list): list of prices
        y_data (list): list of scores

    Returns:
        None

    """
    fig = px.line(x=x_data, y=y_data) # plot line graph from given data, only used for internal testing of score functions
    fig.show()


if __name__ == "__main__":
    # run only directly for test reasons
    # plotting might be deleted, only created for checking score function (it gives expected results)
    PRICE = 2500
    GUESS = 4900
    print("This is a module with functions for evaluating scores of users. It is not intended to be run directly.")
    print(eval_score(PRICE, GUESS))

    scores = []
    guesses = []
    step = 2*round(PRICE/100)
    for i in range(100):
        guesses.append(i*step)
        scores.append(eval_score(PRICE, PRICE-i*step))

    print(scores)
    print(guesses)

    plot_linegraph(guesses, scores)
