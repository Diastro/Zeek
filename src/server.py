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

buffSize = 524288

# (string:url) - Crawling algo
urlVisited = dict() # url already visited
urlPool = Queue.Queue(0) # url scrapped by working nodes
urlToVisit = Queue.Queue(0) # url scrapped by working nodes

# (string:url) - For stats
scrappedURLlist = []
visitedURLlist = []
skippedURLlist = []

# (packet+payload) - To be sent to _any_ node
outputQueue = Queue.Queue(200)

# temporary for server.run()
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
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))
        self.s.listen(5)
        logger.log(logging.INFO, "Listening on [" + str(self.host) + ":" + str(self.port) + "]")

    def run(self):
        """Launches the urlDispatcher and mainRoutine threads"""
        logger.log(logging.DEBUG, "Starting beginCrawlingProcedure")
        thread.start_new_thread(self.urlDispatcher, ())
        thread.start_new_thread(self.mainRoutine, ())

    def listen(self):
        """Waits for new clients to connect and launches a new client thread accordingly"""
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

        #temp testing, could take a parameter from config
        global serverRunning
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
        """Reads from the urlPool, makes sure the url has not been visited and adds it to the urlToVisit Queue"""
        logger.log(logging.INFO, "Starting server urlDispatcher")

        while self.isActive:
            url = urlPool.get(True)

            if url not in urlVisited:
                urlVisited[url] = True
                #logic if static crawling will come here
                urlToVisit.put(url)
                scrappedURLlist.append(url)

    def mainRoutine(self):
        """To Come in da future. For now, no use"""
        logger.log(logging.INFO, "Starting server mainRoutine")
        payload = protocol.URLPayload([str("http://www.businessinsider.com")], protocol.URLPayload.TOVISIT)
        packet = protocol.Packet(protocol.URL, payload)
        outputQueue.put(packet)

        # payload = protocol.URLPayload([str("http://www.lapresse.ca")], protocol.URLPayload.TOVISIT)
        # packet = protocol.Packet(protocol.URL, payload)
        # outputQueue.put(packet)

        # payload = protocol.URLPayload([str("http://www.reddit.com")], protocol.URLPayload.TOVISIT)
        # packet = protocol.Packet(protocol.URL, payload)
        # outputQueue.put(packet)

        urlVisited["http://www.businessinsider.com"] = True
        #urlVisited["http://www.lapresse.ca"] = True
        #urlVisited["http://www.reddit.com"] = True

        while self.isActive:
            try:
                url = urlToVisit.get(True)
                payload = protocol.URLPayload([str(url)], protocol.URLPayload.TOVISIT)
                packet = protocol.Packet(protocol.URL, payload)
                outputQueue.put(packet)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = "\n" + ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.ERROR, message)

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
        self.sentCount = 0
        self.data = ""

        logger.log(logging.INFO, logger.GREEN + "Working node connected " + self.formattedAddr + logger.NOCOLOR)

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
                logger.log(logging.INFO, "Sent URL to  " + self.formattedAddr + " " + str(packet.payload.urlList[0]))
                logger.log(logging.DEBUG, "Packet of type " + str(packet.type) + " sent to " + self.formattedAddr)

    def dispatcher(self, packet):
        """Dispatches packets to the right packet queue or takes action if needed (ie: infoPacket)"""
        if packet is None:
            return
        logger.log(logging.DEBUG, "Dispatching packet of type: " + str(packet.type))

        if packet.type == protocol.INFO:
            logger.log(logging.DEBUG, "Website received INFO packet from node " + self.formattedAddr)
        elif packet.type == protocol.URL:

            if packet.payload.type == protocol.URLPayload.SCRAPPED:
                logger.log(logging.INFO, "Received " + str(len(packet.payload.urlList)) + " / " + str(len(scrappedURLlist)) + " - " + str(len(skippedURLlist)) + " from node " + self.formattedAddr)
                for url in packet.payload.urlList:
                    urlPool.put(url)

            if packet.payload.type == protocol.URLPayload.VISITED:
                self.sentCount = self.sentCount-1
                for url in packet.payload.urlList:
                    logger.log(logging.DEBUG, "Visited " + url + " from node " + self.formattedAddr)
                    visitedURLlist.append(url)

            if packet.payload.type == protocol.URLPayload.SKIPPED:
                self.sentCount = self.sentCount-1
                for url in packet.payload.urlList:
                    logger.log(logging.DEBUG, "Skipped " + url + " from node " + self.formattedAddr)
                    skippedURLlist.append(url)

        else:
            logger.log(logging.CRITICAL, "Unrecognized packet type : " + str(packet.type) + ". This packet was dropped")
            return

    def writeSocket(self, obj):
        try:
            logger.log(logging.DEBUG, "Writing to " + self.formattedAddr)
            serializedObj = pickle.dumps(obj)
            self.socket.sendall(serializedObj + '\n\n12345ZEEK6789\n')
        except:
            raise Exception("Unable to write to socket (client disconnected)")

    def readSocket(self, timeOut=None):
        self.socket.settimeout(timeOut)
        data = self.data

        while self.isActive:
            buffer = self.socket.recv(buffSize)
            data = data + buffer

            logger.log(logging.DEBUG, "Buffer " + str(len(buffer)) + " " + self.formattedAddr)

            if not buffer:
                logger.log(logging.INFO, logger.GREEN + "Lost connection - Working node " + self.formattedAddr + logger.NOCOLOR)
                self.isActive = False

            if "\n\n12345ZEEK6789\n" in data:
                logger.log(logging.DEBUG, "Data " + str(len(data)) + " " + self.formattedAddr)
                data = data.split("\n\n12345ZEEK6789\n")
                self.data = "\n\n12345ZEEK6789\n".join(data[1:])
                break

        if self.isActive == False:
            return

        logger.log(logging.INFO, "Data " + str(len(data[0])) + " " + self.formattedAddr)

        return pickle.loads(data[0])

    def disconnect(self):
        """Disconnects the client"""
        logger.log(logging.DEBUG, "Disconnecting - Working node " + self.formattedAddr)
        self.isActive = False
        self.socket.close()


def handler(signum, frame):
    try:
        scrapped = len(scrappedURLlist)
        skipped = len(skippedURLlist)
        visited = len(visitedURLlist)

        #temp for testing
        # for url in visitedURLlist:
        #     logger.log(logging.DEBUG, "Visited : " + url)
        #
        # for url in scrappedURLlist:
        #     logger.log(logging.DEBUG, "Scrapped : " + url)

        print("\n\n-------------------------")
        print("Scrapped : " + str(scrapped))
        print("Skipped : " + str(skipped))
        print("Visited : " + str(visited))
        print("-------------------------")
        print(float(visited/skipped))
    except:
        #handles cases where crawling did occur (list were empty)
        pass

    print("\n\nExiting. ByeBye")
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