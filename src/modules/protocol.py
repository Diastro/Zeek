import Queue

INFO = 1
URL = 2

class Packet():
    def __init__(self, type):
        self.type = type
        self.payload = 0

    def setPayload(self, payload):
        self.payload = payload

def deQueue(queueArray):
    packetArray = []
    for queue in queueArray:
        try:
            packet = queue.get(block=False)
            packetArray.append(packet)
        except Queue.Empty:
            pass
    return packetArray