"""
script with functions for evaluating scores of users
"""
__author__ = "Florian Kellermann, Linus Eickhoff, Florian Kaiser"
__date__ = "02.05.2022"
__version__ = "0.0.1"
__license__ = "None"

import plotly.express as px


def eval_score(price, guess):
    """calculate the score of a user

    Args:
        price (float): price of the product
        guess (float): guess of the user
    
    Returns:
        float: score of the user
    
    Raises:
        ValueError: if price or guess is negative

    Test:
        test eval_score by plotting the score graph and comparing it to the expected result (should be linear or logarithmic/exponential)
        test with edge cases (e.g. price = 1, guess = 0) -> if guess is half or times 2 actual price -> score should be 0, score has to be always between 0 and 1000
    """
    price = float(price)
    guess = float(guess)

    if price <= 0 or guess < 0:
        raise ValueError("Price has to be positive, guess has to be positive or zero") # raise error if price or guess is negative

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

    Raises:
        ValueError: if price or guess is negative
    
    Test:
        test get_relative_deviation with edge cases (e.g. price = 1, guess = 0) -> if guess is half or times 2 actual price -> return value has to be a float >= 0
        test get_relative_deviation with negative price -> should throw ValueError

    """
    if price <= 0 or guess < 0:
        raise ValueError("Price has to be positive, guess has to be positive or zero") # raise error if price or guess is negative

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
