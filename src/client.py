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

        logger.log(logging.INFO, "Socket initialization")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for connectionAttempt in range(3, 0, -1):
            if connectionAttempt == 1:
                logger.log(logging.CRITICAL, "Unable to connect to host " + self.masterNodeFormattedAddr)
                sys.exit()
            try:
                logger.log(logging.INFO, "Connecting to host... " + self.masterNodeFormattedAddr)
                self.s.connect((self.host, self.port))
                logger.log(logging.INFO, "Connected to host " + self.masterNodeFormattedAddr)
                thread.start_new_thread(self.outputThread, ())
                thread.start_new_thread(self.inputThread, ())
                thread.start_new_thread(self.interpretingThread, ())
                #thread.start_new_thread(self.crawlingThread, ())
                break
            except socket.error:
                logger.log(logging.INFO, "Connection failed to " + self.masterNodeFormattedAddr)
                logger.log(logging.INFO, "Retrying in 3 seconds.")
                time.sleep(3)

    def inputThread(self):
        while self.isActive:
            try:
                data = self.s.recv(buffSize)
                if not data:
                    logger.log(logging.INFO, "Lost connection to server " + self.masterNodeFormattedAddr)
                    self.isActive = False
                    break
                deserializedPacket = pickle.loads(data)
                self.dispatcher(deserializedPacket)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def outputThread(self):
        while self.isActive:
            try:
                packet = self.outputQueue.get(True)
                self.s.send(pickle.dumps(packet))
                logger.log(logging.DEBUG, "Sending : " + str(packet.payload))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def dispatcher(self, packet):
        if packet.type is protocol.INFO:
            self.infoQueue.put(packet)
        elif packet.type is protocol.URL:
            self.urlToVisit.put(packet)
        else:
            logger.log(logging.CRITICAL, "Unrecognized packet type : " + str(packet.type) + ". This packet was dropped")
            return

        logger.log(logging.DEBUG, "Received : " + str(packet.payload))

    def interpretingThread(self):
        logger.log(logging.INFO, "Interpreting started")

        while self.isActive:
            try:
                time.sleep(0.01) #temp - For testing
                packets = protocol.deQueue([self.urlToVisit, self.infoQueue])

                if not packets:
                    continue

                for packet in packets:
                    if packet.type == protocol.INFO:
                        val = int(packet.payload)
                        packet.payload = val+1
                        self.outputQueue.put(packet)
                    elif packet.type == protocol.URL:
                        val = int(packet.payload)
                        packet.payload = val+1
                        self.outputQueue.put(packet)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def crawlingThread(self):
        logger.log(logging.INFO, "Crawler started")

    def disconnect(self):
        self.s.close()


def main():
    #config
    logger.log(logging.INFO, "Parsing the configuration file")
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
    logPath = logPath
    logger.init(logPath, "client-" + str(datetime.datetime.now()))
    logger.debugFlag = verbose

    node = WorkingNode()
    node.connect(host, port)

    while node.isActive:
        time.sleep(0.9)

    node.disconnect()
    logger.log(logging.INFO, "Exiting. ByeBye")

if __name__ == "__main__":
    main()