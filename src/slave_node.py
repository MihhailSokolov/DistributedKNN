"""
This module contains everything needed for Slave node
"""
from data_point import parse_data_point
import socket
import network_messages as messages
import knn_classifier
import argparse


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
        self.data = []
        self.points_to_process = []
        self.host = master_host
        self.port = master_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_node(self):
        self.start_connection_phase()
        self.start_data_collection_phase()
        self.start_classification_phase()
        self.start_shutdown_phase()

    def start_connection_phase(self):
        """
        Starts Connection phase where connection to master is established.
        :return: None
        """
        print('CONNECTION PHASE')
        self.socket.connect((self.host, self.port))
        print('Starting handshake')
        self.socket.send(messages.ClientMessages.GREET_SERVER)
        data = self.socket.recv(1024)
        print('Slave received:', data)
        if data and data == messages.ServerMessages.GREET_CLIENT:
            print('Handshake completed')
        print('CONNECTION PHASE IS FINISHED')

    def start_data_collection_phase(self):
        """
        Starts Data Distribution Phase where dataset is received from the Master.
        :return: None
        """
        print('DATA DISTRIBUTION PHASE')
        self.socket.send(messages.ClientMessages.SEND_DATA_REQUEST)
        data = self.socket.recv(1024)
        if data:
            batch_size = int(data.decode())
            print('Ready to receive', batch_size, 'data points')
            self.socket.send(messages.ClientMessages.READY)
            self.data = []
            for i in range(batch_size):
                data = self.socket.recv(1024)
                if not data:
                    continue
                self.data.append(parse_data_point(data.decode()))
            print('Received points:', str([p.data for p in self.data]))
        print('DATA DISTRIBUTION PHASE IS FINISHED')

    def start_classification_phase(self):
        """
        Starts Classification Phase where points are sent to Slave nodes for classification.
        :return: Classification results
        """
        print('CLASSIFICATION PHASE')
        self.socket.send(messages.ClientMessages.SEND_DATA_REQUEST)
        data = self.socket.recv(1024)
        if data:
            batch_size = int(data.decode())
            print('Ready to receive', batch_size, 'data points')
            self.socket.send(messages.ClientMessages.READY)
            self.points_to_process = []
            for i in range(batch_size):
                data = self.socket.recv(1024)
                if not data:
                    continue
                self.points_to_process.append(parse_data_point(data.decode()))
        for p in self.points_to_process:
            print(p.data)
        self.socket.send(messages.ClientMessages.REQUEST_FOR_K)
        data = self.socket.recv(1024)
        if data:
            k = int(data.decode())
            data = self.socket.recv(1024)
            if data:
                n = int(data.decode())
                points_to_send = {}
                print('Extracting', (k//n)+1, 'neighbouring points for each data point')
                for point in self.points_to_process:
                    neighbours = knn_classifier.get_neighbours(self.data, point, (k // n) + 1)
                    points_to_send[point.id] = neighbours
                self.socket.send(messages.ClientMessages.SEND_CLASSIFICATION_DATA_REQUEST)
                data = self.socket.recv(1024)
                if data and data == messages.ServerMessages.ALLOW_PROCEED:
                    self.socket.send(str.encode(str(len(points_to_send.keys()))))
                    for point in points_to_send.keys():
                        self.socket.send(str.encode(str(len(points_to_send[point]))))
                        self.socket.send(str.encode(str(point)))
                        print('Sending neighbours for', point, str([p.label for p in points_to_send[point]]))
                        for neighbour in points_to_send[point]:
                            self.socket.send(str.encode(str(neighbour)))
        print('CLASSIFICATION PHASE IS FINISHED')

    def start_shutdown_phase(self):
        """
        Starts Shutdown Phase where connection is closed
        :return:
        """
        print('SHUTDOWN PHASE')
        self.socket.close()
        print('SHUTDOWN PHASE IS FINISHED')


if __name__ == '__main__':
    host = 'localhost'
    port = 1223

    parser = argparse.ArgumentParser()
    parser.add_argument('--master-host', '-mh', help='Set Master node host name')
    parser.add_argument('--master-port', '-mp', help='Set Master node port number')
    args = parser.parse_args()
    if args.master_host:
        host = args.master_host
    if args.master_port:
        port = int(args.master_port)

    slave = SlaveNode(master_host=host, master_port=port)
    slave.start_node()
