"""
Module for numeric distributions such as uniform or gaussian
"""
import random
import inspect
import dataspec
from dataspec.model import Distribution


class UniformDistribution(Distribution):
    """
    Class that samples values from a uniform distribution between the start and end points
    """

    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end

    def next_value(self):
        return random.uniform(self.start, self.end)


class GaussDistribution(Distribution):
    """
    Class that samples values from a normal distribution with provided mean and standard deviation
    """

    def __init__(self, mean: float, stddev: float):
        self.mean = mean
        self.stddev = stddev

    def next_value(self):
        return random.gauss(self.mean, self.stddev)


class BoundedDistribution(Distribution):
    """
    Class bounds another distribution
    """

    def __init__(self,
                 distribution: Distribution,
                 min_val: float = 0.0,
                 max_val: float = None):
        self.distribution = distribution
        self.min = min_val
        self.max = max_val

    def next_value(self):
        value = self.distribution.next_value()
        if self.min and value < self.min:
            return self.min
        if self.max and value > self.max:
            return self.max
        return value


@dataspec.registry.distribution('uniform')
def uniform(start, end):
    """ uniform distribution for from start to end """
    return UniformDistribution(start, end)


@dataspec.registry.distribution('normal')
def normal(mean, stddev, **kwargs):
    """ normal distribution for normal keyword """
    return _gaussian_distribution(mean, stddev, **kwargs)


@dataspec.registry.distribution('gauss')
def gauss(mean, stddev, **kwargs):
    """ normal distribution for gauss keyword """
    return _gaussian_distribution(mean, stddev, **kwargs)


@dataspec.registry.distribution('gaussian')
def gaussian(mean, stddev, **kwargs):
    """ normal distribution for gaussian keyword """
    return _gaussian_distribution(mean, stddev, **kwargs)


def _gaussian_distribution(mean, stddev, **kwargs):
    """ normal distribution for mean and standard deviation """
    distribution = GaussDistribution(mean, stddev)
    if 'min' in kwargs or 'max' in kwargs:
        return BoundedDistribution(distribution, kwargs.get('min'), kwargs.get('max'))
    return distribution


def from_string(dist_func_str: str) -> Distribution:
    """
    Uses a function form of the distribution to look up and configure it

    >>> distribution = dataspec.distributions.from_string("uniform(start=10, end=25)")

    Distribution params need to use key=value format
    :param dist_func_str:
    :return: the specified distribution if registered
    """
    try:
        open_paren = dist_func_str.index('(')
        close_paren = dist_func_str.index(')')
    except ValueError as value_error:
        raise ValueError('Invalid function format: ' + dist_func_str) from value_error

    if open_paren == 0 or close_paren < open_paren or close_paren != len(dist_func_str.strip()) - 1:
        raise ValueError('Invalid function format: ' + dist_func_str)

    name = dist_func_str[0:open_paren]
    dist_func = dataspec.registry.distribution.get(name)

    args = dist_func_str[open_paren + 1:close_paren]
    kwargs = _convert_to_kwargs(args)

    if kwargs is None or _invalid_args_for_func(dist_func, kwargs):
        raise ValueError('Invalid args for function: ' + dist_func_str)

    return dist_func(**kwargs)


def _invalid_args_for_func(dist_func, kwargs):
    """ verifies the args match """
    argspec = inspect.getfullargspec(dist_func)
    expected_args = argspec.args
    actual_args = list(set(kwargs.keys()) - {'min', 'max'})
    return sorted(actual_args) != sorted(expected_args)


def _convert_to_kwargs(args):
    """
    converts string of key=val, ..., key=val to dictionary
    :param args: to convert
    :return: dictionary of key values
    """
    parts = args.split(',')
    kwargs = {}
    for part in parts:
        keyval = part.split('=')
        if len(keyval) != 2:
            return None
        kwargs[keyval[0].strip()] = float(keyval[1].strip())
    return kwargs
