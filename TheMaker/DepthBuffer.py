import queue
import threading

class DepthBuffer:
    """
    Buffers order book depth updates and verifies validity
    """

    def __init__(self):
        self.__buffer__ = queue.Queue()
        self.thread = threading.Thread(target=self.process)

    def start(self):
        self.thread.start()

    def process(self):
        while True:
            if not self.__buffer__.empty():
                update = self.__buffer__.get()
