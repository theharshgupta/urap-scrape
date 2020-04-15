import sys, os

def block_print():
    """
    Blocks all print statements when called
    :return: None
    """
    sys.stdout = open(os.devnull, 'w')


def enable_print():
    """
    Enable the print statements. Called after block_print function
    :return: None
    """
    sys.stdout = sys.__stdout__

TIMEOUT_LIMIT = 5
