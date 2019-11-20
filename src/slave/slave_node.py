"""
This module contains everything needed for Slave node
"""
import socket


class SlaveNode(object):
    """
    Slave node class
    """

    def __init__(self, host='localhost', port=1223):
        """
        Constructor for Master Node class.
        :param host: Host name at which Slave node will be located
        :param port: Port number at which Slave node will be located
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_node(self):
        self.socket.connect((self.host, self.port))
        self.socket.send(b'hello, world!')
        data = self.socket.recv(1024)
        print('Slave received:', data)
        self.socket.close()


if __name__ == '__main__':
    slave = SlaveNode()
    slave.start_node()
