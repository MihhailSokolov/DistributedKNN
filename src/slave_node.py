"""
This module contains everything needed for Slave node
"""
import socket
import network_messages as messages


class SlaveNode(object):
    """
    Slave node class
    """

    def __init__(self, master_host='localhost', master_port=1223):
        """
        Constructor for Master Node class.
        :param master_host: Host name at which Master node to which we want to connect will be located
        :param master_port: Port number at which Master node to which we want to connect will be located
        """
        self.host = master_host
        self.port = master_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_node(self):
        self.socket.connect((self.host, self.port))
        print('Starting handshake')
        self.socket.send(messages.GREET_SERVER)
        data = self.socket.recv(1024)
        print('Slave received:', data)
        if data and data == messages.GREET_CLIENT:
            print('Handshake completed')
        self.socket.close()


if __name__ == '__main__':
    slave = SlaveNode()
    slave.start_node()
