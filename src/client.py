import ConfigParser
import datetime
import logging
import random
import socket
import sys
import time
import traceback
import modules.logger as logger

buffSize = 4096


def main():
    #setup
    logPath = 'logs/'
    logger.init(logPath + "client-" + str(datetime.datetime.now()))
    logger.debugFlag = True

    #config
    logger.log(logging.INFO, "Parsing the configuration file")
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config')
    host = config.get('client', 'hostAddr')
    port = config.getint('client', 'hostPort')

    #socket init
    logger.log(logging.INFO, "Socket initialization")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for connectionAttempt in range(3, 0, -1):
        if connectionAttempt == 1:
            logger.log(logging.CRITICAL, "Unable to connect to host [" + str(host) + ":" + str(port) + "]")
            sys.exit()
        try:
            logger.log(logging.INFO, "Connecting to host... [" + str(host) + ":" + str(port) + "]")
            s.connect((host, port))
            logger.log(logging.INFO, "Connected to host [" + str(host) + ":" + str(port) + "]")
            break
        except socket.error:
            logger.log(logging.INFO, "Connection failed to [" + str(host) + ":" + str(port) + "]")
            logger.log(logging.INFO, "Retrying in 3 seconds.")
            time.sleep(3)

    #######################################
    #Temporary part from here going down
    print("- - - - - - - - - - - - - - -")
    while 1:
        try:
            val = random.randint(1,100)
            print(val)
            s.send(str(val))
            time.sleep(0.08)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.log(logging.CRITICAL, message)
            break
    s.close()
    #######################################

if __name__ == "__main__":
    main()