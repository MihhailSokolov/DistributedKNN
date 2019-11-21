"""
This module contains everything needed for master node.
"""
from socketserver import TCPServer, BaseRequestHandler
import network_messages as messages


class RequestHandler(BaseRequestHandler):
    def handle(self):
        print('Request from', self.client_address[0] + ':' + str(self.client_address[1]))
        data = self.request.recv(1024)
        if data and data == messages.GREET_SERVER:
            print('Master received:', data)
            self.request.sendall(messages.GREET_CLIENT)


class MasterNode(object):
    """
    Master node class
    """

    def __init__(self, dataset=None, host='localhost', port=1223):
        """
        Constructor for Master Node class.
        :param dataset: The whole dataset of points
        :param host: Host name at which Master node will be located
        :param port: Port number at which Master node will be located
        """

        self.data = dataset
        self.server = TCPServer((host, port), RequestHandler)

    def load_data(self, data):
        """
        Loads the dataset on Master node.
        :param data: Dataset to be stored
        :return: None
        """
        self.data = data

    def start_node(self):
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print('Stopping Master node')
        finally:
            self.server.shutdown()


if __name__ == '__main__':
    master = MasterNode()
    master.start_node()
