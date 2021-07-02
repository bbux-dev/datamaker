"""
Module for value list supplier implementation
"""
import random

import dataspec


class ListValueSupplier(dataspec.ValueSupplierInterface):
    """
    Value Supplier implementation for supplying values from lists
    """

    def __init__(self, data: list, count: dataspec.ValueSupplierInterface, do_sampling: bool = False):
        self.values = data
        self.do_sampling = do_sampling
        self.count = count

    def next(self, iteration):
        cnt = self.count.next(iteration)
        if self.do_sampling:
            values = random.sample(self.values, cnt)
        else:
            values = [self._value(iteration, i) for i in range(cnt)]
        if cnt == 1:
            return values[0]
        return values

    def _value(self, iteration, i):
        idx = (iteration + i) % len(self.values)
        return self.values[idx]
