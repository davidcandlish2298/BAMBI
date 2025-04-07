import inspect # imported to help log out where I am in the code
import logging
import importlib.util # needed for flask checking

# Need to setup logging in utils
logger = logging.getLogger(__name__)

logger.info("Started logging in utils.py")

def log_active_function():
    # I was finding myself doing a lot of "logging.info("Entering function ABC")" so wrote this helper function to automate it
    # I didn't know how to do this so I looked up some solutions on stackoverflow
    # https://stackoverflow.com/questions/10973362/python-logging-function-name-file-name-line-number-using-a-single-file
    # the response dated Jun 11 2012 from Matthew Schinkel contained
    # func = inspect.currentframe().f_back.f_code
    # I then looked up how to get just the function name and added .co_name after reading the link below and experimenting
    # https://stackoverflow.com/questions/5067604/determine-function-name-from-within-that-function

    active_function = inspect.currentframe().f_back.f_code.co_name
    logger.info(f"Entered function - {active_function}")

def check_flask():
    # checks if flask is installed, if not it won't even offer the web app as an option until it is
    flaskstatus = importlib.util.find_spec("flask")
    # if this evaluates true, allows usage of web-app mode
    return flaskstatus is not None
