"""
Module for holding classes for common supporting Value Suppliers.  These are not core suppliers, but are used to
modify or wrap the functionality of the core suppliers.

"""
import random
from collections import deque

import dataspec


class SingleValue(dataspec.ValueSupplierInterface):
    """
    Encapsulates supplier that only returns a static value
    """

    def __init__(self, data):
        self.data = data

    def next(self, _):
        return self.data


class MultipleValueSupplier(dataspec.ValueSupplierInterface):
    """
    Supplier that generates list of values based on count parameter
    """

    def __init__(self, wrapped: dataspec.ValueSupplierInterface, count_supplier: dataspec.ValueSupplierInterface):
        self.wrapped = wrapped
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        return [self.wrapped.next(iteration + i) for i in range(count)]


class RotatingSupplierList(dataspec.ValueSupplierInterface):
    """
    Class that rotates through a list of suppliers incrementally to provide the next value
    """

    def __init__(self, suppliers, modulate_iteration):
        """
        :param suppliers: list of suppliers to rotate through
        :param modulate_iteration: if the iteration should be split evenly across all suppliers
        """
        self.suppliers = suppliers
        self.modulate_iteration = modulate_iteration

    def next(self, iteration):
        idx = iteration % len(self.suppliers)
        if self.modulate_iteration:
            modulated_iteration = int(iteration / len(self.suppliers))
            return self.suppliers[idx].next(modulated_iteration)
        return self.suppliers[idx].next(iteration)


class DecoratedSupplier(dataspec.ValueSupplierInterface):
    """
    Class used to add additional data to other suppliers output, such as a
    prefix or suffix or to surround the output with quotes
    """

    def __init__(self, config, supplier):
        self.prefix = config.get('prefix', '')
        self.suffix = config.get('suffix', '')
        self.quote = config.get('quote', '')
        self.wrapped = supplier

    def next(self, iteration):
        value = self.wrapped.next(iteration)
        # todo: cache mapping for efficiency?
        return f'{self.quote}{self.prefix}{value}{self.suffix}{self.quote}'


class CastingSupplier(dataspec.ValueSupplierInterface):
    """
    Class that just casts the results of other suppliers
    """

    def __init__(self, wrapped, caster):
        self.wrapped = wrapped
        self.caster = caster

    def next(self, iteration):
        return self.caster.cast(self.wrapped.next(iteration))


class RandomRangeSupplier(dataspec.ValueSupplierInterface):
    """
    Class that supplies values uniformly selected from specified bounds
    """

    def __init__(self, start, end, precision, count_supplier: dataspec.ValueSupplierInterface):
        self.start = float(start)
        self.end = float(end)
        self.precision = precision
        self.format_str = '{: .' + str(precision) + 'f}'
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        next_nums = [random.uniform(self.start, self.end) for _ in range(count)]
        if self.precision is not None:
            next_nums = [self.format_str.format(next_num) for next_num in next_nums]
        if count == 1:
            return next_nums[0]
        return next_nums


class DistributionBackedSupplier(dataspec.ValueSupplierInterface):
    """
    Class that supplies values selected from a distribution such as a Guassian or Uniform distribution.

    @see dataspec.distributions
    """

    def __init__(self, distribution: dataspec.Distribution):
        self.distribution = distribution

    def next(self, _):
        return self.distribution.next_value()


class BufferedValueSuppier(dataspec.ValueSupplierInterface):
    """
    Class for buffering the values from other suppliers. This allows the interaction
    of one supplier with the previous values of another supplier
    """

    def __init__(self, wrapped: dataspec.ValueSupplierInterface, buffer_size: int):
        self.wrapped = wrapped
        self.buffer: deque = deque(maxlen=buffer_size)
        self.current = -1
        self.buffer_size = buffer_size

    def next(self, iteration):
        if iteration > self.current:
            value = self.wrapped.next(iteration)
            self.buffer.append(value)
            self.current = iteration
            return value

        idx = len(self.buffer) - (self.current - iteration) - 1
        if idx < 0:
            raise ValueError('Buffer index out of range')
        return self.buffer[idx]