"""
Factory like module for core supplier related functions.
"""
from typing import Union, Dict, Any
import json

import dataspec
from .exceptions import SpecException
from .supplier.common import (SingleValue, MultipleValueSupplier, RotatingSupplierList, DecoratedSupplier,
                              CastingSupplier, RandomRangeSupplier, DistributionBackedSupplier, BufferedValueSuppier)
from .utils import load_config, is_affirmative, get_caster
from .supplier.core.combine import CombineValuesSupplier
from .supplier.list_values import ListValueSupplier
from .supplier.weighted_values import WeightedValueSupplier
from .supplier.list_stat_sampler import ListStatSamplerSupplier
from .supplier.list_count_sampler import ListCountSamplerSupplier
from .model import Distribution
from . import types, casters, distributions, ValueSupplierInterface
from .defaults import *


def values(spec, loader=None, **kwargs) -> ValueSupplierInterface:
    """
    Based on data, return the appropriate values supplier. data can be a spec, constant, list, or dict.

    >>> import dataspec
    >>> spec = {"type": "values", "data": [1,2,3,5,8,13]}
    >>> fib_supplier = dataspec.suppliers.values(spec)

    or just the raw data

    >>> fib_supplier = dataspec.suppliers.values([1,2,3,5,8,13])

    example with weights

    >>> weights =  {"1": 0.1, "2": 0.2, "3": 0.1, "4": 0.2, "5": 0.1, "6": 0.2, "7": 0.1}
    >>> mostly_even_supplier = dataspec.suppliers.values(weights)

    :param spec: to load values from, or raw data itself
    :param loader: if needed
    :param kwargs: extra kwargs to add to config
    :return: the value supplier for the spec
    """
    # shortcut notations no type, or data, the spec is the data
    if _data_not_in_spec(spec):
        data = spec
    else:
        data = spec['data']

    config = load_config(spec, loader, **kwargs)
    do_sampling = is_affirmative('sample', config, default=types.get_default('sample_mode'))

    if isinstance(data, list):
        # this supplier can handle the count param itself, so just return it
        return _value_list(data, config, do_sampling)
    if isinstance(data, dict):
        if do_sampling:
            raise SpecException('Cannot do sampling on weighted values: ' + json.dumps(spec))
        supplier = weighted_values(data)
    else:
        supplier = single_value(data)

    # Check for count param
    if 'count' in config:
        return MultipleValueSupplier(supplier, count_supplier_from_config(config))
    return supplier


def _data_not_in_spec(spec):
    """ check to see if the data element is defined for this spec """
    if isinstance(spec, dict):
        return 'data' not in spec
    return True


def count_supplier_from_data(data) -> ValueSupplierInterface:
    """
    generates a supplier for the count parameter based on the type of the data

    valid data for counts:
     * integer i.e. 1, 7, 99
     * list of integers: [1, 7, 99], [1], [1, 2, 1, 2, 3]
     * weighted map, where keys are numeric strings: {"1": 0.6, "2": 0.4}
     * dataspec.Distribution i.e. normal, gauess
    """
    if isinstance(data, list):
        supplier = _value_list(data, None, False)
    elif isinstance(data, dict):
        supplier = weighted_values(data)
    elif isinstance(data, Distribution):
        supplier = cast_supplier(distribution_supplier(data), cast_to='int')
    else:
        try:
            supplier = single_value(int(data))
        except ValueError as value_error:
            raise SpecException(f'Invalid count param: {data}') from value_error

    return supplier


def count_supplier_from_config(config: Dict) -> ValueSupplierInterface:
    """
    creates a count supplier from the config, if the count param is defined, otherwise uses default of 1

    optionally can specify count or count_dist.

    valid data for counts:
     * integer i.e. 1, 7, 99
     * list of integers: [1, 7, 99], [1], [1, 2, 1, 2, 3]
     * weighted map, where keys are numeric strings: {"1": 0.6, "2": 0.4}

    count_dist will be interpreted as a distribution i.e:

    >>> import dataspec
    >>> config = {"count_dist": "uniform(start=10, end=100)"}
    >>> count_supplier = dataspec.suppliers.count_supplier_from_config(config)

    :param config: to use
    :return: a count supplier
    """
    data = 1  # type: Any
    if config and 'count' in config:
        data = config['count']
    if config and 'count_dist' in config:
        data = distributions.from_string(config['count_dist'])
    return count_supplier_from_data(data)


def single_value(data):
    """
    Creates value supplier for the single value

    Examples:

    >>> import dataspec
    >>> single_int_supplier = dataspec.suppliers.single_value(42)
    >>> single_str_supplier = dataspec.suppliers.single_value("42")
    >>> single_float_supplier = dataspec.suppliers.single_value(42.42)
    """
    return SingleValue(data)


def array_supplier(wrapped: ValueSupplierInterface,
                   count_config: dict) -> ValueSupplierInterface:
    """
    Wraps an existing supplier and always returns an array/list of elements, uses count config to determine
    number of items in the list

    Example:

    >>> import dataspec
    >>> config = {"count_dist": "normal(mean=2, stddev=1)"}
    >>> pet_supplier = dataspec.suppliers.values(["dog", "cat", "hamster", "pig", "rabbit", "horse"])
    >>> returns_mostly_two = dataspec.suppliers.array_supplier(pet_supplier, config)
    >>> pet_array = returns_mostly_two.next(0)
    """
    return MultipleValueSupplier(wrapped, count_supplier_from_config(count_config))


def from_list_of_suppliers(supplier_list, modulate_iteration: bool = True) -> ValueSupplierInterface:
    """
    Returns a supplier that rotates through the provided suppliers incrementally

    Example:

    >>> import dataspec
    >>> nice_pet_supplier = dataspec.suppliers.values(["dog", "cat", "hamster", "pig", "rabbit", "horse"])
    >>> mean_pet_supplier = dataspec.suppliers.values(["alligator", "cobra", "mongoose", "killer bee"])
    >>> pet_supplier = dataspec.suppliers.from_list_of_suppliers([nice_pet_supplier, mean_pet_supplier])

    :param supplier_list: to rotate through
    :param modulate_iteration: if the iteration number should be moded by the index of the supplier
    :return: a supplier for these suppliers
    """
    return RotatingSupplierList(supplier_list, modulate_iteration)


def _value_list(data: list,
                config: dict = None,
                do_sampling=False) -> ValueSupplierInterface:
    """
    creates a value list supplier

    :param data: for the supplier
    :param do_sampling: if the data should be sampled instead of iterated through
    :param config: config with optional count param
    :return: the supplier
    """
    if config is None:
        config = {}
    return ListValueSupplier(data, count_supplier_from_config(config), do_sampling)


def weighted_values(data: dict, config=None) -> ValueSupplierInterface:
    """
    creates a weighted value supplier

    Example:

    >>> import dataspec
    >>> weights = {"dog": 0.5, "cat": 0.2, "bunny": 0.1, "hamster": 0.1, "pig": 0.05, "snake": 0.04, "rat": 0.01}
    >>> weighted_pet_supplier = dataspec.suppliers.weighted_values(weights)
    >>> most_likely_a_dog = weighted_pet_supplier.next(0)

    :param data: for the supplier
    :param config: optional config
    :return: the supplier
    """
    return WeightedValueSupplier(data, count_supplier_from_config(config))


def combine(suppliers, config=None):
    """
    Creates a value supplier that will combine the outputs of the provided suppliers in order. The default is to
    join the values with an empty string. Provide the join_with config param to specify a different string to
    join the values with. Set as_list to true, if the values should be returned as a list and not joined

    Example:

    >>> import dataspec
    >>> pet_supplier = dataspec.suppliers.values(["dog", "cat", "hamster", "pig", "rabbit", "horse"], sample=True)
    >>> job_supplier = dataspec.suppliers.values(["breeder", "trainer", "fighter", "wrestler"], sample=True)
    >>> interesting_jobs = dataspec.suppliers.combine([pet_supplier, job_supplier], {'join_with': ' '})
    >>> next_career = interesting_jobs.next(0)

    :param suppliers: to combine value for
    :param config: for the combiner
    :return: the supplier
    """
    return CombineValuesSupplier(suppliers, config)


def random_range(start: Union[int, float],
                 end: Union[int, float],
                 precision: Union[int, float] = None,
                 count: Union[int, float, list, dict, dataspec.Distribution] = 1) -> ValueSupplierInterface:
    """
    Creates a random range supplier for the start and end parameters with the given precision (number of decimal places)

    Example:

    >>> range_supplier = dataspec.suppliers.random_range(5, 25, precision=3)
    >>> # should be between 5 and 25 with 3 decimal places
    >>> next_value = range_supplier.next(0))

    :param start: of range
    :param end: of range
    :param precision: number of decimal points to keep
    :param count: number of elements to return, default is one
    :return: the value supplier for the range
    """
    return RandomRangeSupplier(start, end, precision, count_supplier_from_data(count))


def list_stat_sampler(data: Union[str, list],
                      config: dict) -> ValueSupplierInterface:
    """
    sample from list (or string) with stats based params

    Example:

    >>> import dataspec
    >>> stats_config = {"mean": 2, "stddev": 1}
    >>> pet_list = ["dog", "cat", "hamster", "pig", "rabbit", "horse"]
    >>> pet_supplier = dataspec.suppliers.list_stat_sampler(pet_list, stats_config)
    >>> new_pets = pet_supplier.next(0)

    string example

    >>> char_config = {"min": 2, "mean": 4, "max": 8}
    >>> char_supplier = dataspec.suppliers.list_stat_sampler("#!@#$%^&*()_-~", char_config)
    >>> two_to_eight_chars = char_supplier.next(0)

    :param data: list to select subset from
    :param config: with minimal of mean specified
    :return: the supplier
    """
    return ListStatSamplerSupplier(data, config)


def list_count_sampler(data: list, config: dict) -> ValueSupplierInterface:
    """
    Samples N elements from data list based on config.  If count is provided,
    each iteration exactly count elements will be returned.  If only min is provided,
    between min and the total number of elements will be provided. If only max is provided,
    between one and max elements will be returned. Specifying both min and max will provide
    a sample containing a number of elements in this range.

    Example:

    >>> import dataspec
    >>> count_config = {"min": 2, "max": 5}
    >>> pet_list = ["dog", "cat", "hamster", "pig", "rabbit", "horse"]
    >>> pet_supplier = dataspec.suppliers.list_count_sampler(pet_list, count_config)
    >>> new_pets = pet_supplier.next(0)

    :param data: list to select subset from
    :param config: with minimal of count or min and max supplied
    :return: the supplier
    """
    if 'count' in config or 'count_dist' in config:
        count_supplier = count_supplier_from_config(config)
    else:
        min_cnt = int(config.get('min', 1))
        max_cnt = int(config.get('max', len(data))) + 1
        count_range = list(range(min_cnt, max_cnt))
        count_supplier = _value_list(count_range, None, True)
    return ListCountSamplerSupplier(data, count_supplier, config.get('join_with', None))


def distribution_supplier(distribution: Distribution) -> ValueSupplierInterface:
    """
    creates a ValueSupplier that uses the given distribution to generate values

    :param distribution: to use
    :return: the value supplier
    """
    wrapped = DistributionBackedSupplier(distribution)
    # buffer the values
    return buffered(wrapped, {})


def is_decorated(field_spec):
    """
    is this spec a decorated one
    :param field_spec: to check
    :return: true or false
    """
    if 'config' not in field_spec:
        return False
    config = field_spec.get('config')
    return 'prefix' in config or 'suffix' in config or 'quote' in config


def decorated(field_spec, supplier):
    """
    Creates a decorated supplier around the provided on
    :param field_spec: the spec
    :param supplier: the supplier to decorate
    :return: the decorated supplier
    """
    return DecoratedSupplier(field_spec.get('config'), supplier)


def is_cast(field_spec):
    """
    is this spec requires casting
    :param field_spec: to check
    :return: true or false
    """
    if not isinstance(field_spec, dict):
        return False
    config = field_spec.get('config', {})
    return 'cast' in config


def cast_supplier(supplier: ValueSupplierInterface,
                  field_spec: dict = None,
                  cast_to: str = None) -> ValueSupplierInterface:
    """
    Provides a cast_supplier either from config or from explicit cast_to

    :param supplier: to cast results of
    :param field_spec: to look up cast config from
    :param cast_to: explicit cast type to use
    :return: the casting supplier
    """

    if cast_to:
        caster = casters.get(cast_to)
    else:
        if field_spec is None:
            config = {}
        else:
            config = field_spec.get('config', {})
        caster = get_caster(config)
    return CastingSupplier(supplier, caster)


def is_buffered(field_spec):
    """
    Should the values for this spec be buffered

    :param field_spec: to check
    :return: true or false
    """
    config = field_spec.get('config', {})
    return 'buffer_size' in config or is_affirmative('buffer', config)


def buffered(wrapped: ValueSupplierInterface, field_spec):
    """
    Creates a Value Supplier that buffers the results of the wrapped supplier

    :param wrapped: the Value Supplir to buffer values for
    :param field_spec: to check
    :return:
    """
    config = field_spec.get('config', {})
    buffer_size = int(config.get('buffer_size', 10))
    return BufferedValueSuppier(wrapped, buffer_size)
