"""
This module contains everything needed for Slave node
"""
from data_point import parse_data_point, DataPoint
import socket
import network_messages as messages
import knn_classifier


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
        self.classification_data = []
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
            print('RECEIVED:', data)
            batch_size = int(data.decode())
            print('Ready to receive', batch_size, 'data points')
            self.socket.send(messages.ClientMessages.READY)
            self.data = []
            for i in range(batch_size):
                data = self.socket.recv(1024)
                if not data:
                    continue
                self.data.append(parse_data_point(data.decode()))
            print('Received points:')
            for d in self.data:
                print(d.data, 'label =', d.label)
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
            print('RECEIVED:', data)
            batch_size = int(data.decode())
            print('Ready to receive', batch_size, 'data points')
            self.socket.send(messages.ClientMessages.READY)
            self.classification_data = []
            for i in range(batch_size):
                data = self.socket.recv(1024)
                if not data:
                    continue
                self.classification_data.append(parse_data_point(data.decode()))
        for p in self.classification_data:
            print(p.data)
        self.socket.send(messages.ClientMessages.REQUEST_FOR_K)
        data = self.socket.recv(1024)
        if data:
            k = int(data.decode())
            print('EXECUTING CLASSIFICATION WITH k =', k)
            classified_points = []
            for point in self.classification_data:
                point_label = knn_classifier.classify(self.data, point, k)
                classified_points.append(DataPoint(point.data, point_label, point.id))
            print('CLASSIFICATION FINISHED, SENDING', len(classified_points), 'CLASSIFIED POINTS')
            self.socket.send(messages.ClientMessages.SEND_CLASSIFICATION_DATA_REQUEST)
            data = self.socket.recv(1024)
            if data and data == messages.ServerMessages.ALLOW_PROCEED:
                self.socket.send(str.encode(str(len(classified_points))))
                for point in classified_points:
                    self.socket.send(str.encode(str(point)))
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
    slave = SlaveNode()
    slave.start_node()
