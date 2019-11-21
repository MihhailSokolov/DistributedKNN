"""
Module that contains DataPoint data
"""
import numpy as np
import uuid


class DataPoint(object):
    """
    DataPoint data that stores all required data for one data point
    """
    def __init__(self, data, label=None):
        """
        Constructor for DataPoint data.
        :param data: Array of values for each dimension
        :param label: Label assigned to the point
        """
        self.id = uuid.uuid4()
        self.data = np.array(data)
        if label:
            self.label = label
