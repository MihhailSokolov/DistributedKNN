"""
Module that contains DataPoint data
"""
import numpy as np
from uuid import uuid4


class DataPoint(object):
    """
    DataPoint data that stores all required data for one data point
    """

    def __init__(self, data, label=None, point_id=str(uuid4())):
        """
        Constructor for DataPoint data.
        :param data: Array of values for each dimension
        :param label: Label assigned to the point
        """
        self.id = point_id
        self.data = np.array(data)
        self.label = label

    def __str__(self) -> str:
        return '(' + str(self.id) + ';[' + ','.join([str(point) for point in self.data]) + '];' \
               + (self.label if self.label is not None else '') + ')'


def parse_data_point(str_point: str) -> DataPoint:
    if str_point.startswith('(') and str_point.endswith(')'):
        str_point = str_point[1:-1]
    str_parts = str_point.split(';')
    point_id = str_parts[0]
    str_data = str_parts[1]
    if str_data.startswith('[') and str_data.endswith(']'):
        str_data = str_data[1:-1]
    data_parts = str_data.split(',')
    data = []
    for d in data_parts:
        data.append(float(d))
    label = str_parts[2] if len(str_parts) > 2 else None
    return DataPoint(data, label, point_id)
