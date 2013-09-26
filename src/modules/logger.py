import inspect
import logging
import os

debugFlag = True


def init(path, logName):
    if not os.path.exists(path):
        print path
        os.makedirs(path)
    logging.basicConfig(filename=path+logName, format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)


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


def formatBrackets(message):
    return "[" + str(message) + "]"