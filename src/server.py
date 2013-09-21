import socket
import sys
import thread

list1 = []
host = '127.0.0.1'
port = 5050
backlog = 5
size = 1024


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

        while 1:
            data = self.socket.recv(1024)

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
    #loading modules
    sys.path.append("modules/")

    #socket setup
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(backlog)

    Server()
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