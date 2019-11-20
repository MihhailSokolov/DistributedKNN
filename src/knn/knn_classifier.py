"""
Module contains all methods required for kNN classification
"""
import numpy as np
from collections import Counter
import operator


def euclidean(p1, p2):
    """
    Computes the euclidean distance between point p and q.
    :param p1: first DataPoint
    :param p2: second DataPoint
    :return: distance as float.
    """
    return np.linalg.norm(p1.data - p2.data)


def get_neighbours(dataset, data_point, k):
    """
    Calculate distances from data_point to all points in the dataset.
    :param dataset: [n x d] numpy array of training samples (n: number of samples, d: number of dimensions).
    :param data_point: [d x 1] numpy array of test instance features.
    :param k: number of neighbours to return.
    :return: list of length k with neighbour indices.
    """
    distances = {}
    for i, point in enumerate(dataset):
        distances[point] = euclidean(point, data_point)
    neighbours_map = sorted(distances.items(), key=operator.itemgetter(1))[:k]
    return list(map(lambda p: p[0], neighbours_map))


def get_majority_vote(points):
    """
    Finds label that is most common.
    :param points: the list of DataPoints
    :return: the label of most common data.
    """
    labels = [point.label for point in points]
    (most_common, _) = Counter(labels).most_common(1)[0]
    return most_common


def classify(dataset, new_point, k):
    """
    Classifies new data point based k nearest neighbours in the dataset.
    :param dataset: All data points
    :param new_point: New data point for classification
    :param k: Number of neighbours
    :return: label of the new point
    """
    return get_majority_vote(get_neighbours(dataset, new_point, k))