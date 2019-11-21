"""
This module contains everything needed for master node.
"""
from src.messages.network_messages import *
import socket


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
        self.master_host = host
        self.master_port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def load_data(self, data):
        """
        Loads the dataset on Master node.
        :param data: Dataset to be stored
        :return: None
        """
        self.data = data

    def start_node(self):
        self.socket.bind((self.master_host, self.master_port))
        self.socket.listen(1)
        connection, (client_host, client_port) = self.socket.accept()
        print('Client', client_host + ':' + str(client_port), 'connected')
        try:
            while True:
                data = connection.recv(1024)
                if data and data == GREET_SERVER:
                    print('Master received:', data)
                    connection.sendall(GREET_CLIENT)
                else:
                    break

        finally:
            connection.close()


if __name__ == '__main__':
    master = MasterNode()
    master.start_node()
