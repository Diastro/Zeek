import socket
import sys
import thread
import ConfigParser
import logging
import datetime

buffSize = 4096


class Server:
    def __init__(self):
        print("In Server...")


class SSClient:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        print("In Server-Side client..." + str(address[0]) + ":" + str(address[1]))

    def Listen(self):
        print("SSClient is listening")
        logging.info('In listen')
        while 1:
            data = self.socket.recv(buffSize)

            #Disconnection
            if not data:
                print("Lost connection to client - Disconnecting...")
                break

            print(str(data))

    def Disconnect(self):
        print("Disconnecting Server-Side client... - " + str(self.address))
        self.socket.close()


def ConnectionHandler(socket, address):
    client = SSClient(socket, address)
    try:
        client.Listen()
    except:
        print("Exception raised in client.Listen() - " + str(address))
        print("Error - " + str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
    finally:
        client.Disconnect()


def main():
    #setup
    logName = str(datetime.datetime.now())
    logging.basicConfig(filename=logName, format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)

    #config
    logging.info('Parsing the configuration file...')
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config')
    host = config.get('server', 'listeningAddr')
    port = config.getint('server', 'listeningPort')

    #socket init
    logging.info('Socket initialization...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)

    #listening loop
    while 1:
        try:
            client, address = s.accept()
            thread.start_new_thread(ConnectionHandler, (client, address))
        except:
            print("Exception raised in main loop - ")
            print("Error - " + str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
            break

if __name__ == "__main__":
    main()