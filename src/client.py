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
from server import urlToVisit

buffSize = 4096


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
        logger.log(logging.DEBUG, "Waiting for configuration from the server.")
        if self.isActive:
            try:
                deserializedPacket = self.readSocket()
                if deserializedPacket.type is protocol.CONFIG:
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
        if self.isActive:
            thread.start_new_thread(self.outputThread, ())
            thread.start_new_thread(self.inputThread, ())
            thread.start_new_thread(self.interpretingThread, ())
            thread.start_new_thread(self.crawlingThread, ())

    def disconnect(self):
        self.isActive = False
        self.s.close()

    def inputThread(self):
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
        logger.log(logging.DEBUG, "OutputThread started")

        while self.isActive:
            try:
                obj = self.outputQueue.get(True)
                self.writeSocket(obj)
                logger.log(logging.DEBUG, "Sending obj of type " + str(obj.type))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def interpretingThread(self):
        logger.log(logging.DEBUG, "InterpretingThread started")

        while self.isActive:
            try:
                time.sleep(0.01) #temp - For testing
                #packets = protocol.deQueue([self.urlToVisit, self.infoQueue])
                packets = protocol.deQueue([self.urlToVisit])

                if not packets:
                    continue

                for packet in packets:
                    if packet.type is protocol.URL:
                        #visiting site
                        logger.log(logging.INFO, "Visiting site : " + str(packet.payload.urlList))
                        self.outputQueue.put(packet)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def crawlingThread(self):
        logger.log(logging.DEBUG, "CrawlingThread started")

        while self.isActive:
            site = urlToVisit.get(True)
            logger.log(logging.DEBUG, "Visiting site " + site)

    def writeSocket(self, obj):
        serializedObj = pickle.dumps(obj)
        self.s.send(serializedObj)

    def readSocket(self, timeOut=None):
        self.s.settimeout(timeOut)
        data = self.s.recv(buffSize)

        #broken connection
        if not data:
            logger.log(logging.INFO, "Lost connection to server " + self.masterNodeFormattedAddr)
            self.isActive = False

        return pickle.loads(data)

    def dispatcher(self, packet):
        if packet.type is protocol.INFO:
            self.infoQueue.put(packet)
        elif packet.type is protocol.URL:
            self.urlToVisit.put(packet)
        else:
            logger.log(logging.CRITICAL, "Unrecognized packet type : " + str(packet.type) + ". This packet was dropped")
            return

        logger.log(logging.DEBUG, "Dispatched packet of type: " + str(packet.type))


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