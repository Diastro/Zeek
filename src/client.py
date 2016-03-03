import ConfigParser
import datetime
import Queue
import logging
import os
import pickle
import socket
import sys
import time
import thread
import traceback
import modules.logger as logger
import modules.protocol as protocol
import modules.scrapping as scrapping

sys.setrecursionlimit(10000)

buffSize = 524288
delimiter = '\n\n12345ZEEK6789\n'


class WorkingNode():
    def __init__(self):
        # socket
        self.host = None
        self.port = None
        self.data = ""

        # general
        self.isActive = True
        self.masterNodeFormattedAddr = None
        self.crawlingType = None

        # data container
        self.outputQueue = Queue.Queue(0)
        self.infoQueue = Queue.Queue(0)
        self.urlToVisit = Queue.Queue(0)

        # object
        self.scrapper = None
        self.config = None


    def connect(self, host, port):
        """Sets up the connection to the server (max 6 attemps)"""
        self.host = host
        self.port = port
        self.masterNodeFormattedAddr = "[" + str(self.host) + ":" + str(self.port) + "]"

        logger.log(logging.DEBUG, "Socket initialization")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for connectionAttempt in range(6, 0, -1):
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
                logger.log(logging.DEBUG, "Configuration received.")

                if deserializedPacket.type == protocol.CONFIG:
                    self.crawlingType = deserializedPacket.payload.crawlingType
                    self.config = deserializedPacket.payload.config

                    # dynamic module reload
                    basePath = os.path.dirname(sys.argv[0])
                    if basePath:
                        basePath = basePath + "/"

                    # path building
                    rulePath = basePath + "modules/rule.py"
                    scrappingPath = basePath + "modules/scrapping.py"

                    # re-writing source .py
                    logger.log(logging.INFO, "Importing rule.py from server")
                    ruleFd = open(rulePath, 'w')
                    ruleFd.write(self.config.rule_py)
                    ruleFd.close()

                    logger.log(logging.INFO, "Importing scrapping.py from server")
                    scrappingFd = open(scrappingPath, 'w')
                    scrappingFd.write(self.config.scrapping_py)
                    scrappingFd.close()

                    # compilation test
                    try:
                        code=open(rulePath, 'rU').read()
                        compile(code, "rule_test", "exec")
                    except:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                        logger.log(logging.CRITICAL, message)
                        logger.log(logging.ERROR, "Unable to compile rule.py (is the syntax right?)")
                        sys.exit(0)

                    try:
                        code=open(scrappingPath, 'rb').read(os.path.getsize(scrappingPath))
                        compile(code, "scrapping_test", "exec")
                    except:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                        logger.log(logging.CRITICAL, message)
                        logger.log(logging.ERROR, "Unable to compile scrapping.py (is the syntax right?)")
                        sys.exit(0)

                    # dynamic reload of modules
                    # TODO reloading of rule.py should eventually come here
                    logger.log(logging.INFO, "Reloading modules imported for server")
                    reload(sys.modules["modules.scrapping"])


                    payload = protocol.InfoPayload(protocol.InfoPayload.CLIENT_ACK)
                    packet = protocol.Packet(protocol.INFO, payload)
                    self.writeSocket(packet)

                    logger.log(logging.DEBUG, "Sending ACK for configuration.")
                else:
                    raise Exception("Unable to parse configuration.")
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.CRITICAL, message)
                self.isActive = False

    def run(self):
        """Launches main threads"""
        logger.log(logging.INFO, "\n\nStarting Crawling/Scrapping sequence...")
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

        self.scrapper = scrapping.Scrapper(self.config.userAgent, self.config.robotParserEnabled, self.config.domainRestricted, self.config.crawling)

        while self.isActive:
            try:
                urlList = protocol.deQueue([self.urlToVisit])

                if not urlList:
                    time.sleep(0.2) #temp - For testing
                    continue

                for url in urlList:
                    session = self.scrapper.visit(url)
                    logger.log(logging.DEBUG, "Session \n" + str(session.url) +
                      "\nCode : " + str(session.returnCode) +
                      "\nRequest time : " + str(session.requestTime) +
                      "\nBs time : " + str(session.bsParsingTime))

                    if not session.failed:
                        if self.crawlingType == protocol.ConfigurationPayload.DYNAMIC_CRAWLING:
                            payload = protocol.URLPayload(session.scrappedURLs, protocol.URLPayload.SCRAPPED_URL)
                            packet = protocol.Packet(protocol.URL, payload)
                            self.outputQueue.put(packet)

                        payload = protocol.URLPayload([url], protocol.URLPayload.VISITED, session=session)
                        packet = protocol.Packet(protocol.URL, payload)
                        self.outputQueue.put(packet)
                    else:
                        logger.log(logging.INFO, "Skipping URL : " + url)
                        payload = protocol.URLPayload([url], protocol.URLPayload.SKIPPED, session)
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
        if packet is None:
            return
        elif packet.type == protocol.INFO:
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
            serializedObj = pickle.dumps(obj)
            logger.log(logging.DEBUG, "Sending " + str(len(serializedObj + delimiter)) + " bytes to server")
            self.s.sendall(serializedObj + delimiter)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.log(logging.CRITICAL, message)
            raise Exception("Unable to write to socket (lost connection to server)")

    def readSocket(self, timeOut=None):
        self.s.settimeout(timeOut)
        data = self.data

        if "\n\n12345ZEEK6789\n" in data:
            data = data.split("\n\n12345ZEEK6789\n")
            self.data = "\n\n12345ZEEK6789\n".join(data[1:])
            return pickle.loads(data[0])

        while self.isActive:
            buffer = self.s.recv(buffSize)
            data = data + buffer

            if not buffer:
                logger.log(logging.INFO, "\nLost connection to server " + self.masterNodeFormattedAddr)
                self.isActive = False

            if "\n\n12345ZEEK6789\n" in data:
                data = data.split("\n\n12345ZEEK6789\n")
                self.data = "\n\n12345ZEEK6789\n".join(data[1:])
                break

        if self.isActive == False:
            return

        logger.log(logging.DEBUG, "Receiving " + str(len(data[0])) + " bytes from server")

        return pickle.loads(data[0])

    def disconnect(self):
        """Disconnects from the server"""
        self.isActive = False
        self.s.close()


def main():
    path = os.path.dirname(sys.argv[0])
    if path:
        path = path + "/"

    #config
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read(path + 'config')
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

if __name__ == "__main__":
    main()