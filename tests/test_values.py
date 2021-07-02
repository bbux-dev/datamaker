from dataspec import Loader
import dataspec.suppliers as suppliers
from dataspec.loader import preprocess_spec
from dataspec.exceptions import SpecException
import dataspec.builder as builder
from collections import Counter
import pytest


def test_single_value():
    spec = {'type': 'values', 'data': 42}
    most_common_keys = _get_most_common_keys(spec, 10, 2)

    assert len(most_common_keys) == 1
    assert 42 in most_common_keys


def test_values_list():
    spec = {'data': [1, 2, 3, 4, 5]}
    most_common_keys = _get_most_common_keys(spec, 10, 10)

    assert len(most_common_keys) == 5
    assert [1, 2, 3, 4, 5] == most_common_keys


def test_weighted_values():
    spec = {'data': {'foo': 0.5, 'bar': 0.4, 'baz': 0.1}}
    most_common_keys = _get_most_common_keys(spec, 100, 2)

    assert 'foo' in most_common_keys
    assert 'bar' in most_common_keys


def test_weighted_values_non_zero_count():
    spec = builder.values({'foo': 0.5, 'bar': 0.4, 'baz': 0.1}, count=2)
    supplier = suppliers.values(spec)

    data = supplier.next(0)
    assert isinstance(data, list)
    assert len(data) == 2


def test_shortcut_notation():
    # not type or data key, just what would have been the value for the data key
    spec = builder.values({'foo': 0.5, 'bar': 0.4, 'baz': 0.1})
    most_common_keys = _get_most_common_keys(spec, 100, 2)

    assert 'foo' in most_common_keys
    assert 'bar' in most_common_keys


def _get_most_common_keys(spec, iterations, num_keys_to_collect):
    supplier = suppliers.values(spec)
    data = [supplier.next(i) for i in range(iterations)]
    counter = Counter(data)
    most_common_keys = [item[0] for item in counter.most_common(num_keys_to_collect)]
    return most_common_keys


def test_sampling_mode_invalid_for_weighted_values():
    # sampling is only valid for list based suppliers
    spec = builder.single_field('foo?sample=True', {10: 0.5, 20: 0.3, 30: 0.2}).build()
    _test_invalid_spec(spec, 'foo')


def test_count_param_invalid():
    # the word two is not a valid count
    spec = {'foo?count=two': ['A', 'B', 'C', 'D']}
    _test_invalid_spec(spec, 'foo')


def _test_invalid_spec(spec, key):
    updated = preprocess_spec(spec)
    with pytest.raises(SpecException):
        suppliers.values(updated[key])


def test_count_param_valid():
    spec = {
        'foo?count=2': ['A', 'B', 'C', 'D']
    }
    updated = preprocess_spec(spec)
    supplier = suppliers.values(updated['foo'])
    first = supplier.next(0)
    assert type(first) == list
    assert ['A', 'B'] == first


def test_configref_for_values():
    """ verifies that the values ref inherits the config from the configref """
    spec = builder.single_field("name?configref=quoteit", ["bob", "joe", "ann", "sue"]) \
        .add_ref("quoteit", builder.configref(quote="\"")) \
        .build()
    supplier = Loader(spec).get('name')
    assert supplier.next(0) == '"bob"'


def test_values_list_order():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    spec = builder.single_field('field', data).build()
    supplier = Loader(spec).get('field')

    values = [supplier.next(i) for i in range(10)]
    assert values == data


def test_values_count_as_list():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    spec = builder.single_field('field', builder.values(data, count=[2, 3])).build()
    supplier = Loader(spec).get('field')

    first = supplier.next(0)
    assert isinstance(first, list) and len(first) == 2
    second = supplier.next(1)
    assert isinstance(second, list) and len(second) == 3
