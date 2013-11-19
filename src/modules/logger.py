import inspect
import logging
import os
import sys

debugFlag = True
GREEN = '\033[92m'
PINK = '\033[95m'
BLUE = '\033[94m'
RED = '\033[91m'
YELLOW = '\033[93m'
NOCOLOR = '\033[0m'

color = [GREEN, PINK, BLUE, RED, YELLOW, NOCOLOR]

def init(path, logName):
    basePath = os.path.dirname(sys.argv[0])
    if basePath:
        basePath = basePath + "/"
    path = basePath + path
    if not os.path.exists(path):
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
        fileName = ''.join(func.co_filename.split('/')[-1])
        line = func.co_firstlineno
        message = "[" + str(func.co_name) + " - " + str(fileName) + ", " + str(line) + "] " + message

    if level == logging.CRITICAL:
        message = "\n\n ************************\n" + message

    #printing to logs
    if debugFlag and level == logging.DEBUG:
        print(message)
    elif level is not logging.DEBUG:
        print(message)

    for c in color:
        message = message.replace(c, "")

    logging.log(level, message)


def formatBrackets(message):
    return "[" + str(message) + "]"


def printAsciiLogo():
    print("")
    print(" .----------------.  .----------------.  .----------------.  .----------------. ")
    print("| .--------------. || .--------------. || .--------------. || .--------------. |")
    print("| |   ________   | || |  _________   | || |  _________   | || |  ___  ____   | |")
    print("| |  |  __   _|  | || | |_   ___  |  | || | |_   ___  |  | || | |_  ||_  _|  | |")
    print("| |  |_/  / /    | || |   | |_  \_|  | || |   | |_  \_|  | || |   | |_/ /    | |")
    print("| |     .'.' _   | || |   |  _|  _   | || |   |  _|  _   | || |   |  __'.    | |")
    print("| |   _/ /__/ |  | || |  _| |___/ |  | || |  _| |___/ |  | || |  _| |  \ \_  | |")
    print("| |  |________|  | || | |_________|  | || | |_________|  | || | |____||____| | |")
    print("| |              | || |              | || |              | || |              | |")
    print("| '--------------' || '--------------' || '--------------' || '--------------' |")
    print(" '----------------'  '----------------'  '----------------'  '----------------' ")
    print("")
    print("                                       +++                                      ")
    print("                                      (o o)                                     ")
    print("                                 -ooO--(_)--Ooo-                                ")
    print("                                      v1.0a                                     ")
    print("                                 David Albertson                                ")
    print("")


