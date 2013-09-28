import ConfigParser
import datetime
import logging
import pickle
import Queue
import signal
import socket
import sys
import time
import thread
import traceback
import uuid
import modules.logger as logger
import modules.protocol as protocol

buffSize = 4096

urlVisited = {} # url already visited
urlPool = Queue.Queue(0) # url pool arriving from working nodes
urlToVisit = Queue.Queue(0) # url to be visited by working nodes


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = None
        self.clientDict = {}
        self.isActive = True

    def socketSetup(self):
        logger.log(logging.DEBUG, "Socket initialization")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen(5)
        logger.log(logging.INFO, "Listening on [" + str(self.host) + ":" + str(self.port) + "]")

    def beginCrawlingProcedure(self):
        logger.log(logging.DEBUG, "Starting beginCrawlingProcedure")
        thread.start_new_thread(self.urlDispatcher, ())
        thread.start_new_thread(self.mainRoutine, ())

    def listen(self):
        print("- - - - - - - - - - - - - - -")
        logger.log(logging.INFO, "Waiting for working nodes to connect...")
        while self.isActive:
            try:
                client, address = self.s.accept()
                thread.start_new_thread(self.connectionHandler, (client, address))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def connectionHandler(self, socket, address):
        clientID = uuid.uuid4()
        client = SSClient(clientID, socket, address)
        self.clientDict[clientID] = client

        for clients in self.clientDict:
            logger.log(logging.DEBUG, "Working node connected : " + str(self.clientDict[clients].id))

        try:
            client.sendConfig()
            client.listen()
        except EOFError:
            pass
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = "\n" + ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.log(logging.ERROR, message)
        finally:
            client.disconnect()
            del self.clientDict[clientID]

    def urlDispatcher(self):
        logger.log(logging.INFO, "Starting urlDispatcher")

    def mainRoutine(self):
        logger.log(logging.INFO, "Starting mainRoutine")

    def disconnectAllClient(self):
        for connectedClient in self.clientDict:
            self.clientDict[connectedClient].disconnect()
            logger.log(logging.DEBUG, "Disconnected : " + str(self.clientDict[connectedClient].id))


class SSClient:
    def __init__(self, cId, socket, address):
        self.id = cId
        self.socket = socket
        self.address = address
        self.isActive = True
        self.formattedAddr = logger.formatBrackets(str(str(address[0]) + ":" + str(address[1])))
        logger.log(logging.INFO, "Working node connected " + self.formattedAddr)

    def listen(self):
        logger.log(logging.DEBUG, "Listening for packets " + self.formattedAddr)

        while self.isActive:
            self.readSocket()
            time.sleep(1)

    def sendConfig(self):
        logger.log(logging.DEBUG, "Sending configuration to " + self.formattedAddr)

        payload = protocol.ConfigurationPayload(protocol.ConfigurationPayload.DYNAMIC_CRAWLING)
        packet = protocol.Packet(protocol.CONFIG, payload)
        self.writeSocket(packet)

        logger.log(logging.DEBUG, "Configuration sent waiting for ACK. " + self.formattedAddr)
        packet = self.readSocket(5)

        if packet.type == protocol.INFO:
            if packet.payload.info == protocol.InfoPayload.CLIENT_ACK:
                logger.log(logging.DEBUG, "Working node ACK received (configuration) " + self.formattedAddr)
                return
            else:
                self.isActive = False
                raise Exception("Unable to transmit configuration")

    def writeSocket(self, obj):
        serializedObj = pickle.dumps(obj)
        self.socket.send(serializedObj)

    def readSocket(self, timeOut=None):
        self.socket.settimeout(timeOut)
        data = self.socket.recv(buffSize)

        #broken connection
        if not data:
            logger.log(logging.INFO, "Lost connection - Working node " + self.formattedAddr)
            self.isActive = False

        return pickle.loads(data)

    def disconnect(self):
        logger.log(logging.DEBUG, "Disconnecting - Working node " + self.formattedAddr)
        self.socket.close()


def handler(signum, frame):
        print ("Exiting. ByeBye")
        sys.exit()

def main():
    signal.signal(signal.SIGINT, handler)
    logger.printAsciiLogo()
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
    #server.listen()
    thread.start_new_thread(server.listen, ()) #testing

    while server.isActive:
        time.sleep(0.5)

    #time.sleep(9) #testing
    #server.isActive = False
    #server.disconnectAllClient()
    logger.log(logging.INFO, "Exiting. ByeBye")


if __name__ == "__main__":
    main()