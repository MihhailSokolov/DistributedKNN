"""
This module contains everything needed for master node.
"""
import socket
import random
import network_messages as messages
from data_point import DataPoint, parse_data_point
from knn_classifier import get_majority_vote
import argparse


class MasterNode(object):
    """
    Master node class
    """

    def __init__(self, dataset=None, points=None, k=5, host='localhost', port=1223):
        """
        Constructor for Master Node class.
        :param dataset: The whole dataset of points
        :param points:  List of points to classify
        :param host: Host name at which Master node will be located
        :param port: Port number at which Master node will be located
        """
        print('k =', k)
        print('host =', host)
        print('port =', port)
        self.data = dataset
        self.points = points
        self.k = k
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.connections = []

    def load_data(self, data):
        """
        Loads the dataset on Master node.
        :param data: Dataset to be stored
        :return: None
        """
        random.shuffle(data)
        self.data = data

    def load_points_to_classify(self, points):
        """
        Loads the points that need to be classified.
        :param points: List of points for classification
        :return: None
        """
        self.points = points

    def run(self, num_connections: int, dataset=None, points=None):
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
        else:
            random.shuffle(self.data)
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

    def start_connection_phase(self, num_connections: int):
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
        remaining_points = len(self.data) % n
        batch_size = int((len(self.data) - remaining_points) / n)
        for i, connection in enumerate(self.connections):
            need_send_additional_point = remaining_points - i > 0
            if need_send_additional_point:
                batch_size += 1
            data_batch = self.data[batch_size * i: batch_size * (i + 1)]
            data = connection[0].recv(1024)
            if data and data == messages.ClientMessages.SEND_DATA_REQUEST:
                connection[0].send(str.encode(str(len(data_batch))))
                data = connection[0].recv(1024)
                if data and data == messages.ClientMessages.READY:
                    for d in data_batch:
                        connection[0].send(str.encode(str(d)))
            if need_send_additional_point:
                batch_size -= 1
                remaining_points -= 1
        print('DATA DISTRIBUTION PHASE IS FINISHED')

    def start_classification_phase(self):
        """
        Starts Classification Phase where points are sent to Slave nodes for classification.
        :return: Classification results
        """
        print('CLASSIFICATION PHASE')
        for i, connection in enumerate(self.connections):
            data_batch = self.points
            data = connection[0].recv(1024)
            if data and data == messages.ClientMessages.SEND_DATA_REQUEST:
                connection[0].send(str.encode(str(len(data_batch))))
                data = connection[0].recv(1024)
                if data and data == messages.ClientMessages.READY:
                    for d in data_batch:
                        connection[0].send(str.encode(str(d)))
        for connection in self.connections:
            data = connection[0].recv(1024)
            if data and data == messages.ClientMessages.REQUEST_FOR_K:
                connection[0].send(str.encode(str(self.k)))
                connection[0].send(str.encode(str(len(self.connections))))
        neighbouring_points = {}
        for point in self.points:
            neighbouring_points[str(point.id)] = []
        for connection in self.connections:
            data = connection[0].recv(1024)
            if data and data == messages.ClientMessages.SEND_CLASSIFICATION_DATA_REQUEST:
                connection[0].send(messages.ServerMessages.ALLOW_PROCEED)
                data = connection[0].recv(1024)
                if data:
                    points_to_receive = int(data.decode())
                    for _ in range(points_to_receive):
                        data = connection[0].recv(1024)
                        if data:
                            neighbours_to_receive = int(data.decode())
                            data = connection[0].recv(1024)
                            if data:
                                point_id = str(data.decode())
                                for _ in range(neighbours_to_receive):
                                    data = connection[0].recv(1024)
                                    if data:
                                        neighbour_point = parse_data_point(data.decode())
                                        neighbouring_points[point_id].append(neighbour_point)
        final_classified_points = []
        for point in self.points:
            neighbours = neighbouring_points[str(point.id)]
            final_label = get_majority_vote(neighbours)
            print('Received all neighbours for', point.data, '('+str(point.id)+'):', [p.label for p in neighbours])
            final_classified_points.append(DataPoint(point.data, final_label, point.id))
        self.points = final_classified_points
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
        print('Classified points:')
        for point in self.points:
            print(point.data, '->', point.label)


if __name__ == '__main__':
    host_arg = 'localhost'
    port_arg = 1223
    k_arg = 5
    n = 2

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='Set Master node host name')
    parser.add_argument('--port', help='Set Master node port number')
    parser.add_argument('-k', help='Set number for k in kNN')
    parser.add_argument('-n', '--num-slaves', help='Set number of Slave nodes')
    args = parser.parse_args()
    if args.host:
        host_arg = args.host
    if args.port:
        port_arg = int(args.port)
    if args.k:
        k_arg = int(args.k)
    if args.num_slaves:
        n = int(args.num_slaves)

    master = MasterNode(dataset=[DataPoint([10, 100], '1'),
                                 DataPoint([20, 90], '1'),
                                 DataPoint([30, 80], '1'),
                                 DataPoint([40, 70], '1'),
                                 DataPoint([50, 60], '1'),
                                 DataPoint([60, 50], '0'),
                                 DataPoint([70, 40], '0'),
                                 DataPoint([80, 30], '0'),
                                 DataPoint([90, 20], '0'),
                                 DataPoint([100, 10], '0')],
                        points=[DataPoint([20, 50]),
                                DataPoint([80, 50])],
                        k=k_arg, host=host_arg, port=port_arg)
    master.run(n)
