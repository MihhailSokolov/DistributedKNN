"""
Module contains all methods required for kNN classification
"""
import numpy as np
from collections import Counter


def euclidean(p, q):
    """
    Computes the euclidean distance between point p and q.
    :param p: point p as a numpy array.
    :param q: point q as a numpy array.
    :return: distance as float.
    """
    return np.linalg.norm(p - q)


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
        distances[euclidean(point, data_point)] = point

    neighbours = distances.items()[:k]
    return neighbours


def get_majority_vote(labels):
    """
    Finds label that is most common.
    :param labels: the list of labels
    :return: the label of most common class.
    """
    return Counter(labels).most_common(1)
