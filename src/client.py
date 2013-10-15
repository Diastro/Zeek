import ConfigParser
import datetime
import Queue
import logging
import pickle
import socket
import sys
import time
import thread
import traceback
import modules.logger as logger
import modules.protocol as protocol
import modules.scrapping as scrapping

buffSize = 524288


class WorkingNode():
    def __init__(self):
        self.host = None
        self.port = None
        self.masterNodeFormattedAddr = None
        self.crawlingType = None

        self.isActive = True
        self.outputQueue = Queue.Queue(0)
        self.infoQueue = Queue.Queue(0)
        self.urlToVisit = Queue.Queue(0)

    def connect(self, host, port):
        """Sets up the connection to the server (max 3 attemps)"""
        self.host = host
        self.port = port
        self.masterNodeFormattedAddr = "[" + str(self.host) + ":" + str(self.port) + "]"

        logger.log(logging.DEBUG, "Socket initialization")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for connectionAttempt in range(3, 0, -1):
            if connectionAttempt == 1:
                logger.log(logging.CRITICAL, "Unable to connect to host " + self.masterNodeFormattedAddr)
                sys.exit()
            try:
                logger.log(logging.DEBUG, "Connecting to host... " + self.masterNodeFormattedAddr)
                self.s.connect((self.host, self.port))
                logger.log(logging.INFO, "Connected to " + self.masterNodeFormattedAddr)
                break
            except socket.error:
                logger.log(logging.INFO, "Connection failed to " + self.masterNodeFormattedAddr)
                logger.log(logging.INFO, "Retrying in 3 seconds.")
                time.sleep(3)

    def readConfig(self):
        """Reads the configuration from the server"""
        logger.log(logging.DEBUG, "Waiting for configuration from the server.")
        if self.isActive:
            try:
                deserializedPacket = self.readSocket()
                if deserializedPacket.type == protocol.CONFIG:
                    self.crawlingType = deserializedPacket.payload.crawlingType
                    payload = protocol.InfoPayload(protocol.InfoPayload.CLIENT_ACK)
                    packet = protocol.Packet(protocol.INFO, payload)
                    self.writeSocket(packet)
                    logger.log(logging.DEBUG, "Configuration received.")
                    logger.log(logging.DEBUG, "Sending ACK for configuration.")
                else:
                    raise Exception("Unable to parse configuration.")
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def run(self):
        """Lunches main threads"""
        logger.log(logging.INFO, "Starting Crawling/Scrapping sequence...")
        if self.isActive:
            thread.start_new_thread(self.outputThread, ())
            thread.start_new_thread(self.inputThread, ())
            thread.start_new_thread(self.interpretingThread, ())
            thread.start_new_thread(self.crawlingThread, ())

    def inputThread(self):
        """Listens for inputs from the server"""
        logger.log(logging.DEBUG, "InputThread started")

        while self.isActive:
            try:
                deserializedPacket = self.readSocket()
                self.dispatcher(deserializedPacket)
            except EOFError:
                self.isActive = False
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def outputThread(self):
        """Checks if there are messages to send to the server and sends them"""
        logger.log(logging.DEBUG, "OutputThread started")

        while self.isActive:
            try:
                obj = self.outputQueue.get(True) #fix with helper method to prevent block
                self.writeSocket(obj)
                logger.log(logging.DEBUG, "Sending obj of type " + str(obj.type))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def interpretingThread(self):
        """Interprets message from the server other than type URL. (ie: INFO)"""
        logger.log(logging.DEBUG, "InterpretingThread started")

        while self.isActive:
            try:
                time.sleep(0.01) #temp - For testing
                packets = protocol.deQueue([self.infoQueue])

                if not packets:
                    continue

                for packet in packets:
                    if packet.type == protocol.INFO:
                        logger.log(logging.INFO, "Interpreting INFO packet : " + str(packet.payload.urlList))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def crawlingThread(self):
        """Takes URL from the urlToVisit queue and visits them"""
        logger.log(logging.DEBUG, "CrawlingThread started")

        while self.isActive:
            try:
                urlList = protocol.deQueue([self.urlToVisit])

                if not urlList:
                    time.sleep(0.2) #temp - For testing
                    continue

                for url in urlList:
                    try:
                        session = scrapping.visit(url)
                        logger.log(logging.DEBUG, "Session \n" + str(session.url) +
                          "\nCode : " + str(session.returnCode) +
                          "\nRequest time : " + str(session.requestTime) +
                          "\nBs time : " + str(session.bsParsingTime))

                        payload = protocol.URLPayload(session.scrappedURLs, protocol.URLPayload.SCRAPPED)
                        packet = protocol.Packet(protocol.URL, payload)
                        self.outputQueue.put(packet)

                        payload = protocol.URLPayload([url], protocol.URLPayload.VISITED)
                        packet = protocol.Packet(protocol.URL, payload)
                        self.outputQueue.put(packet)
                    except:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                        logger.log(logging.CRITICAL, message)

                        logger.log(logging.INFO, "Skipping URL : " + url)
                        payload = protocol.URLPayload([url], protocol.URLPayload.SKIPPED)
                        packet = protocol.Packet(protocol.URL, payload)
                        self.outputQueue.put(packet)
                        continue

            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def dispatcher(self, packet):
        """Dispatches packets to the right packet queue"""
        if packet.type == protocol.INFO:
            logger.log(logging.DEBUG, "Dispatching INFO packet")
            self.infoQueue.put(packet)
        elif packet.type == protocol.URL:
            logger.log(logging.DEBUG, "Dispatching url packet : " + str(packet.payload.urlList[0]))
            for site in packet.payload.urlList:
                self.urlToVisit.put(site)
        else:
            logger.log(logging.CRITICAL, "Unrecognized packet type : " + str(packet.type) + ". This packet was dropped")
            return

        logger.log(logging.DEBUG, "Dispatched packet of type: " + str(packet.type))

    def writeSocket(self, obj):
        try:
            logger.log(logging.DEBUG, "Writing to server")
            serializedObj = pickle.dumps(obj)
            self.s.send(serializedObj)
        except:
            raise Exception("Unable to write to socket (lost connection to server)")

    def readSocket(self, timeOut=None):
        self.s.settimeout(timeOut)
        data = ""

        while self.isActive:
            data = data + self.s.recv(buffSize)

            #broken connection
            if not data:
                logger.log(logging.INFO, "Lost connection to server " + self.masterNodeFormattedAddr)
                self.isActive = False

            try:
                pickle.loads(data)
            except:
                continue
            break

        if self.isActive == False:
            return

        return pickle.loads(data)

    def disconnect(self):
        """Disconnects from the server"""
        self.isActive = False
        self.s.close()


def main():
    #config
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config')
    host = config.get('client', 'hostAddr')
    port = config.getint('client', 'hostPort')
    logPath = config.get('common', 'logPath')
    verbose = config.get('common', 'verbose')
    if verbose == "True" or verbose == "true":
        verbose = True
    else:
        verbose = False

    #setup
    logger.init(logPath, "client-" + str(datetime.datetime.now()))
    logger.debugFlag = verbose

    node = WorkingNode()
    node.connect(host, port)
    node.readConfig()
    node.run()

    while node.isActive:
        time.sleep(0.5)

    node.disconnect()
    logger.log(logging.INFO, "Exiting. ByeBye")

if __name__ == "__main__":
    main()