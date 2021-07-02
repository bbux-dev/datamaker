"""
Module for the class that implements supplying weighted values
"""
import random

import dataspec


class WeightedValueSupplier(dataspec.ValueSupplierInterface):
    """
    Value supplier implementation for weighted values
    """

    def __init__(self, data, count_supplier: dataspec.ValueSupplierInterface):
        # may be passed raw data or a spec
        if isinstance(data, dict) and 'data' in data:
            data = data.get('data')
        self.choices = list(data.keys())
        self.weights = data.values()
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        vals = random.choices(self.choices, self.weights, k=count)
        if count == 1:
            return vals[0]
        return vals
