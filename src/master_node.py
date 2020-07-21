"""
This module contains everything needed for master node.
"""
import socket
import math
import network_messages as messages


class MasterNode(object):
    """
    Master node class
    """

    def __init__(self, dataset=None, points=None, host='localhost', port=1223):
        """
        Constructor for Master Node class.
        :param dataset: The whole dataset of points
        :param points:  List of points to classify
        :param host: Host name at which Master node will be located
        :param port: Port number at which Master node will be located
        """
        self.data = dataset
        self.points = points
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.connections = []

    def load_data(self, data):
        """
        Loads the dataset on Master node.
        :param data: Dataset to be stored
        :return: None
        """
        self.data = data

    def load_points_to_classify(self, points):
        """
        Loads the points that need to be classified.
        :param points: List of points for classification
        :return: None
        """
        self.points = points

    def run(self, num_connections, dataset=None, points=None):
        """
        Starts Master node to run the whole process of establishing connections, distributing data,
        running classification and closing the connections.
        :param num_connections: number of connections to establish (number of slave nodes)
        :param dataset: The whole dataset of points
        :param points: List of points for classification
        :return: None
        """
        self.start_connection_phase(num_connections)
        if self.data is None:
            if dataset is not None:
                self.load_data(dataset)
            else:
                print('No data provided! Shutting down...')
                self.start_shutdown_phase()
                return
        self.start_data_distribution_phase()
        if self.points is None:
            if points is not None:
                self.load_points_to_classify(points)
            else:
                print('No classification points provided! Shutting down...')
                self.start_shutdown_phase()
                return
        self.start_classification_phase()
        self.start_shutdown_phase()

    def start_connection_phase(self, num_connections):
        """
        Starts Connection phase where all connections are established.
        :param num_connections: number of connections to establish (number of slave nodes)
        :return: None
        """
        self.socket.listen(num_connections)
        print('CONNECTION PHASE')
        while len(self.connections) < num_connections:
            connection, address = self.socket.accept()
            data = connection.recv(1024)
            if data and data == messages.ClientMessages.GREET_SERVER:
                self.connections.append((connection, address))
                connection.send(messages.ServerMessages.GREET_CLIENT)
        print('Established connections:')
        for connection in self.connections:
            print('\t', connection[1][0] + ':' + str(connection[1][1]))
        print('CONNECTION PHASE IS FINISHED')

    def start_data_distribution_phase(self):
        """
        Starts Data Distribution Phase where initial dataset is distributed to the Slave nodes.
        :return: None
        """
        print('DATA DISTRIBUTION PHASE')
        n = len(self.connections)
        # TODO: Make sure rounding error does not leave out some data points
        batch_size = int(len(self.data) / n)
        for i, connection in enumerate(self.connections):
            data_batch = self.data[batch_size * i: batch_size * (i + 1)]
            data = connection[0].recv(1024)
            if data and data == messages.ClientMessages.SEND_DATA_REQUEST:
                byte_length = int(math.log2(len(data_batch) / 8)) + 1
                connection[0].send(len(data_batch).to_bytes(byte_length, byteorder='big'))
                data = connection[0].recv(1024)
                if data and data == messages.ClientMessages.READY:
                    for d in data_batch:
                        # TODO: Fix math domain error (need better way to determine number of bytes)
                        byte_length = int(math.log2(int(d / 8))) + 1
                        connection[0].send(d.to_bytes(byte_length, byteorder='big'))
        print('DATA DISTRIBUTION PHASE IS FINISHED')

    def start_classification_phase(self):
        """
        Starts Classification Phase where points are sent to Slave nodes for classification.
        :return: Classification results
        """
        print('CLASSIFICATION PHASE')
        for point in self.points:
            pass
        # TODO: Implement
        print('CLASSIFICATION PHASE IS FINISHED')

    def start_shutdown_phase(self):
        """
        Starts Shutdown Phase where all connections are closed
        :return:
        """
        print('SHUTDOWN PHASE')
        for connection in self.connections:
            print('\t', 'Closing connection with', connection[1][0] + ':' + str(connection[1][1]))
            connection[0].close()
        self.socket.close()
        print('SHUTDOWN PHASE IS FINISHED')


if __name__ == '__main__':
    master = MasterNode(dataset=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    master.run(1)
