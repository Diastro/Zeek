import inspect
import logging
import datetime

debugFlag = True


def init():
    logName = str(datetime.datetime.now())
    logging.basicConfig(filename=logName, format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)


def debugFlag(flag):
    debugFlag = flag
    if debugFlag:
        logging.disable(logging.NOTSET)
    else:
        logging.disable(logging.DEBUG)


def log(level, message):
    #message formatting
    if level == logging.DEBUG:
        func = inspect.currentframe().f_back.f_code
        fileName = func.co_filename
        line = func.co_firstlineno
        message = "[" + str(func.co_name) + " - " + str(fileName) + ", " + str(line) + "] " + message

    if level == logging.CRITICAL:
        message = "\n\n ************************\n" + message

    #printing to logs
    if debugFlag and level == logging.DEBUG:
        print(message)
    elif level is not logging.DEBUG:
        print(message)
    logging.log(level, message)
