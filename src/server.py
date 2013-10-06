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

#Payload
urlVisited = {} # url already visited
urlPool = Queue.Queue(0) # url pool arriving from working nodes

outputQueue = Queue.Queue(0)

serverRunning = False


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = None
        self.clientDict = {}
        self.isActive = True

    def setup(self):
        """Basic setup operation (socket binding, listen, etc)"""
        logger.log(logging.DEBUG, "Socket initialization")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen(5)
        logger.log(logging.INFO, "Listening on [" + str(self.host) + ":" + str(self.port) + "]")

    def run(self):
        """Launches the urlDispatcher and mainRoutine threads"""
        logger.log(logging.DEBUG, "Starting beginCrawlingProcedure")
        thread.start_new_thread(self.urlDispatcher, ())
        thread.start_new_thread(self.mainRoutine, ())

    def listen(self):
        """Waits for new clients to connect and launches the thread accordingly"""
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
        """Creates a server-side client object and makes it listen for inputs"""
        clientID = uuid.uuid4()
        client = SSClient(clientID, socket, address)
        self.clientDict[clientID] = client

        global serverRunning
        #temp testing, could take a parameter from config
        if len(self.clientDict) > 0  and serverRunning == False:
            self.run()
            serverRunning = True

        for clients in self.clientDict:
            logger.log(logging.DEBUG, "Working node connected : " + str(self.clientDict[clients].id))

        try:
            client.sendConfig()
            client.run()
            while client.isActive:
                time.sleep(0.3)
        except EOFError:
            pass
        except:
            client.isActive = False
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = "\n" + ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.log(logging.ERROR, message)
        finally:
            client.disconnect()
            del self.clientDict[clientID]

    def urlDispatcher(self):
        """Reads from the url pool, makes sure the url has not been visited and adds it to the urlToVisitQueue"""
        logger.log(logging.INFO, "Starting server urlDispatcher")

        while self.isActive:
            obj = urlPool.get(True)

            # if not visited
            # verification

            #urlToVisit.put(obj)

    def mainRoutine(self):
        """To Come in da future. For now, no use"""
        logger.log(logging.INFO, "Starting server mainRoutine")
        while self.isActive:
            payload = protocol.URLPayload([str("http://www.lapresse.ca" + str(datetime.datetime.now())), str("http://www.lapresse.ca" + str(datetime.datetime.now()))])
            packet = protocol.Packet(protocol.URL, payload)
            outputQueue.put(packet)

            time.sleep(2)

    def disconnectAllClient(self):
        """Disconnects all clients"""
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
        self.sentCount = 0

    def sendConfig(self):
        """Sends the configuration to the client"""
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

    def run(self):
        """Launched the input and output thread with the client itself"""
        thread.start_new_thread(self.inputThread, ())
        thread.start_new_thread(self.outputThread, ())

    def inputThread(self):
        """Listens for inputs from the client"""
        logger.log(logging.DEBUG, "Listening for packets " + self.formattedAddr)

        while self.isActive:
            try:
                deserializedPacket = self.readSocket()
                self.sentCount = self.sentCount-1
                self.dispatcher(deserializedPacket)

            except EOFError:
                #Fixes the pickle error if clients disconnects
                self.isActive = False

    def outputThread(self):
        """Checks if there are messages to send to the client and sends them"""
        while self.isActive:
            if self.sentCount > 5:
                time.sleep(0.1)
                continue
            packetToBroadCast = protocol.deQueue([outputQueue])

            if not packetToBroadCast:
                    continue

            for packet in packetToBroadCast:
                self.writeSocket(packet)
                self.sentCount = self.sentCount+1
                logger.log(logging.DEBUG, "Packet of type " + str(packet.type) + " sent to " + self.formattedAddr)

    def dispatcher(self, packet):
        """Dispatches packets to the right packet queue"""
        if packet.type is protocol.INFO:
            print("temp")
        elif packet.type is protocol.URL:
            #urlPool.put(packet)
            print("temp")
        else:
            logger.log(logging.CRITICAL, "Unrecognized packet type : " + str(packet.type) + ". This packet was dropped")
            return

        logger.log(logging.DEBUG, "Dispatched packet of type: " + str(packet.type))

    def writeSocket(self, obj):
        try:
            logger.log(logging.DEBUG, "Writing to " + self.formattedAddr)
            serializedObj = pickle.dumps(obj)
            self.socket.send(serializedObj)
        except:
            raise Exception("Unable to write to socket (client disconnected)")

    def readSocket(self, timeOut=None):
        self.socket.settimeout(timeOut)
        data = self.socket.recv(buffSize)

        #broken connection
        if not data:
            logger.log(logging.INFO, "Lost connection - Working node " + self.formattedAddr)
            self.isActive = False

        return pickle.loads(data)

    def disconnect(self):
        """Disconnects the client"""
        logger.log(logging.DEBUG, "Disconnecting - Working node " + self.formattedAddr)
        self.isActive = False
        self.socket.close()


def handler(signum, frame):
    print()
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
    server.setup()
    thread.start_new_thread(server.listen, ()) #testing

    while server.isActive:
        time.sleep(0.5)

    server.disconnectAllClient()
    logger.log(logging.INFO, "Exiting. ByeBye")


if __name__ == "__main__":
    main()