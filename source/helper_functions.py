"""
script for helper functions for bot related stuff
"""
__author__ = "Florian Kellermann, Linus Eickhoff, Florian Kaiser"
__date__ = "28.05.2022"
__version__ = "1.0.0"
__license__ = "None"


def contains_markdownv1_symbols(text):
    """ checks if text contains markdown symbols
    :type text: string

    :param text: text to check

    :return: true if text contains markdown symbols

    :rtype: bool
    """
    if text.find("_") != -1 or text.find("*") != -1 or text.find("`") != -1:  # check if text contains relevant markdown symbols
        return True

    return False


def make_markdown_proof(text):  # used to avoid errors related to markdown parsemode for telegram messaging
    """ makes text markdown proof
    :type text: string

    :param text: text to make markdown proof

    :return: markdown proof text

    :rtype: string
    """
    text = str(text)

    text = text.replace("_", "\\_")  # replace _ with \_ because \ is used as escape character in markdown, double escape is needed because \ is also a escape character in strings
    text = text.replace("*", "\\*")
    text = text.replace("`", "\\`")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    text = text.replace("(", "\\(")
    text = text.replace(")", "\\)")
    text = text.replace("#", "\\#")
    text = text.replace("+", "\\+")
    text = text.replace("-", "\\-")
    text = text.replace("!", "\\!")
    text = text.replace(".", "\\.")
    text = text.replace("?", "\\?")
    text = text.replace("/", "\\/")
    text = text.replace("~", "\\~")
    text = text.replace("|", "\\|")
    text = text.replace("<", "\\<")
    text = text.replace(">", "\\>")
    text = text.replace("&", "\\&")
    text = text.replace("^", "\\^")
    text = text.replace("$", "\\$")
    text = text.replace("%", "\\%")
    text = text.replace("=", "\\=")
    text = text.replace("@", "\\@")

    return text


if __name__ == '__main__':
    print("this is a module for helper functions for the bot and should not be run directly")
    print(make_markdown_proof("_test_"))
    text = make_markdown_proof("_test_")
    print(f"{text}")
