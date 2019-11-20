import unittest
from src.data.data_point import DataPoint
from src.knn.knn_classifier import *


class TestKNNClassifier(unittest.TestCase):

    def test_get_majority_vote(self):
        point1 = DataPoint([1.0, 1.0], 'a')
        point2 = DataPoint([0.0, 0.0], 'b')
        point3 = DataPoint([1.0, 0.0], 'a')
        points = [point1, point2, point3]
        majority = get_majority_vote(points)
        self.assertEqual(majority, 'a', 'Majority label should "a"')

    def test_get_neighbours(self):
        point1 = DataPoint([1.0, 1.0], 'a')
        point2 = DataPoint([0.0, 0.0], 'b')
        point3 = DataPoint([1.0, 0.0], 'a')
        points = [point3, point1, point2]
        new_point = DataPoint([0.0, 1.0], None)
        result = [point1, point2]
        neighbours = get_neighbours(points, new_point, 2)
        self.assertEqual(neighbours, result, 'Should return 2 closest points: point1[1.0, 1.0] and point2[0.0, 0.0]')

    def test_euclidean_distance(self):
        point1 = DataPoint([1.0, 1.0], 'a')
        point2 = DataPoint([0.0, 0.0], 'b')
        d = 2 ** 0.5
        result = euclidean(point1, point2)
        self.assertEqual(result, d, 'Euclidean distance between these points should be sqrt(2)')

    def test_knn_classification(self):
        point1 = DataPoint([1.0, 1.0], 'a')
        point2 = DataPoint([0.0, 0.0], 'b')
        point3 = DataPoint([1.0, 0.0], 'a')
        point4 = DataPoint([-1.0, 1.0], 'b')
        point5 = DataPoint([-1.0, 0.0], 'a')
        points = [point3, point1, point2, point5, point4]
        new_point = DataPoint([0.0, 1.0], None)
        k1 = 3
        label1 = 'b'
        result1 = classify(points, new_point, k1)
        self.assertEqual(result1, label1, 'With 3 neighbours classification should result in "b" label')
        k2 = 5
        label2 = 'a'
        result2 = classify(points, new_point, k2)
        self.assertEqual(result2, label2, 'With 5 neighbours classification should result in "a" label')
