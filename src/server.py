import ConfigParser
import datetime
import logging
import socket
import sys
import thread
import traceback
import modules.logger as logger

buffSize = 4096


class Server:
    def __init__(self):
        print("In Server...")


class SSClient:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.formattedAddr = "[" + str(address[0]) + ":" + str(address[1]) + "]"
        logger.log(logging.INFO, "New connection - Working node " + self.formattedAddr)

    def Listen(self):
        logger.log(logging.INFO, "Listening for inputs " + self.formattedAddr)

        while 1:
            data = self.socket.recv(buffSize)

            #broken connection
            if not data:
                logger.log(logging.INFO, "Lost connection - Working node " + self.formattedAddr)
                break

            logger.log(logging.DEBUG, "Data received " + self.formattedAddr + ": " + str(data))

    def Disconnect(self):
        logger.log(logging.INFO, "Disconnecting - Working node " + self.formattedAddr)
        self.socket.close()


def ConnectionHandler(socket, address):
    client = SSClient(socket, address)
    try:
        client.Listen()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        message = "\n" + ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.log(logging.ERROR, message)
    finally:
        client.Disconnect()


def main():
    #setup
    logger.init("server-" + str(datetime.datetime.now()))
    logger.debugFlag = True

    #config
    logger.log(logging.INFO, "Parsing the configuration file")
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config')
    host = config.get('server', 'listeningAddr')
    port = config.getint('server', 'listeningPort')

    #socket init
    logger.log(logging.INFO, "Socket initialization")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)

    #listening loop
    print("- - - - - - - - - - - - - - -")
    logger.log(logging.INFO, "Waiting for working node to connect...")
    while 1:
        try:
            client, address = s.accept()
            thread.start_new_thread(ConnectionHandler, (client, address))

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.log(logging.CRITICAL, message)
            break

if __name__ == "__main__":
    main()