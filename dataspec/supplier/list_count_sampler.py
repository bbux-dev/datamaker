""" Module for ListCountSamplerSupplier """
from typing import Union
import random

import dataspec


class ListCountSamplerSupplier(dataspec.ValueSupplierInterface):
    """
    Supplies values by sampling from a list with hard min max and count
    """

    def __init__(self, data: Union[str, list],
                 count_supplier: dataspec.ValueSupplierInterface,
                 join_with: str = ''):
        self.values = data
        self.count_supplier = count_supplier
        self.join_with = join_with

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        data = random.sample(self.values, count)
        if self.join_with is not None:
            return self.join_with.join([str(elem) for elem in data])
        return data
