import ConfigParser
import datetime
import logging
import pickle
import random
import socket
import sys
import thread
import traceback
import modules.logger as logger
import modules.protocol as protocol

buffSize = 4096


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = None

    def socketSetup(self):
        logger.log(logging.INFO, "Socket initialization")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen(5)

    def beginCrawlingProcedure(self):
        logger.log(logging.INFO, "Starting beginCrawlingProcedure")
        thread.start_new_thread(self.urlDispatcher, ())
        thread.start_new_thread(self.mainRoutine, ())

    def listen(self):
        print("- - - - - - - - - - - - - - -")
        logger.log(logging.INFO, "Waiting for working node to connect...")
        while 1:
            try:
                client, address = self.s.accept()
                thread.start_new_thread(self.connectionHandler, (client, address))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                break

    def connectionHandler(self, socket, address):
        client = SSClient(socket, address)
        try:
            client.Listen()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = "\n" + ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.log(logging.ERROR, message)
        finally:
            client.Disconnect()

    def urlDispatcher(self):
        logger.log(logging.INFO, "Starting urlDispatcher")

    def mainRoutine(self):
        logger.log(logging.INFO, "Starting mainRoutine")


class SSClient:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.isActive = True
        self.formattedAddr = logger.formatBrackets(str(str(address[0]) + ":" + str(address[1])))
        logger.log(logging.INFO, "New connection - Working node " + self.formattedAddr)

    def Listen(self):
        logger.log(logging.INFO, "Listening for inputs " + self.formattedAddr)

        while self.isActive:
            #Packet creation
            val = str(random.randint(1, 100))
            packet = protocol.Packet(protocol.INFO)
            packet.payload = val
            serializedObj = pickle.dumps(packet)

            #send
            self.socket.send(serializedObj)
            logger.log(logging.DEBUG, "Data sent " + self.formattedAddr + ": " + val)

            #receive - For testing
            data = self.socket.recv(buffSize)

            #broken connection
            if not data:
                logger.log(logging.INFO, "Lost connection - Working node " + self.formattedAddr)
                self.isActive = False
                break

            #packet treatment
            unserializedObj = pickle.loads(data)
            logger.log(logging.DEBUG, "Data received " + self.formattedAddr + ": " + str(unserializedObj.payload))

            #time.sleep(0.5) #temp - For testing

    def Disconnect(self):
        logger.log(logging.INFO, "Disconnecting - Working node " + self.formattedAddr)
        self.socket.close()


def main():
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config')
    host = config.get('server', 'listeningAddr')
    port = config.getint('server', 'listeningPort')
    logPath = config.get('common', 'logPath')
    verbose = config.get('common', 'verbose')
    if verbose == "True" or verbose == "true":
        verbose = True
    else:
        verbose = False

    #logging
    logger.init(logPath, "server-" + str(datetime.datetime.now()))
    logger.debugFlag = verbose

    #server
    server = Server(host, port)
    server.socketSetup()
    server.listen()

if __name__ == "__main__":
    main()