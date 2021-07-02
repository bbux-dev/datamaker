"""
Module to hold models for core data structures and classes
"""
from pathlib import Path
from typing import Union


class DataSpec(dict):
    """
    Class representing a DataSpec object
    """

    def __delitem__(self, key):
        return self.raw_spec.__delitem__(key)

    def __setitem__(self, key, value):
        return self.raw_spec.__setitem__(key, value)

    def __getitem__(self, key):
        return self.raw_spec.__getitem__(key)

    def __contains__(self, key):
        return self.raw_spec.__contains__(key)

    def __repr__(self):
        return f"{type(self.raw_spec).__name__}({super().__repr__()})"

    def pop(self, key):
        return self.raw_spec.pop(key)

    def __init__(self, raw_spec):
        self.raw_spec = raw_spec

    def generator(self, iterations: int, **kwargs):
        """
        Creates a generator that will produce records or render the template for each record

        Usage:

        >>> import dataspec

        >>> builder = dataspec.Builder()
        >>> builder.values(['bob', 'bobby', 'robert', 'bobo']))

        >>> spec = builder.build()

        >>> template = 'Name: {{ name }}'

        >>> generator = spec.generator(
        >>>     iterations=4,
        >>>     template=template)

        >>>  for i in range(5):
        >>>      try:
        >>>          record = next(generator)
        >>>          print(record)
        >>>      except StopIteration:
        >>>          pass

        :param iterations: the number of iterations to run
        :return: record generator
        """


class Distribution:
    """
    Interface Class for a numeric distribution such as a Uniform or Gaussian distribution
    """

    def next_value(self) -> float:
        """ get the next value for this distribution """


class ValueSupplierInterface:
    """
    Interface for Classes that supply values
    """
    def next(self, iteration):
        """
        Produces the next value for the given iteration
        :param iteration: current iteration
        :return: the next value
        """