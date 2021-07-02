import pytest

from dataspec import builder, Loader, SpecException
from dataspec.supplier.core import range_suppliers


def test_range_lists_missing_data():
    with pytest.raises(SpecException):
        range_suppliers.configure_range_supplier({'type': 'range_list'}, None)


def test_range_lists_invalid_data_type():
    with pytest.raises(SpecException):
        range_suppliers.configure_range_supplier({'type': 'range_list', 'data': 42}, None)


def test_range_lists_end_before_start():
    start = 10
    end = 9
    with pytest.raises(SpecException):
        range_suppliers.configure_range_supplier({'type': 'range_list', 'data': [start, end]}, None)


def test_range_lists_valid():
    start = 2
    end = 10
    step = 2
    supplier = range_suppliers.configure_range_supplier({'type': 'range_list', 'data': [start, end, step]}, None)

    expected = [2, 4, 6, 8, 10]
    actual = [supplier.next(i) for i in range(5)]

    assert expected == actual


def test_range_lists_float_step():
    start = 0
    end = 1
    step = .1
    supplier = range_suppliers.configure_range_supplier({'type': 'range_list', 'data': [start, end, step]}, None)

    expected = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    actual = [supplier.next(i) for i in range(11)]

    assert expected == actual


def test_range_lists_float_start_end():
    start = 0.5
    end = 5.5
    supplier = range_suppliers.configure_range_supplier({'type': 'range_list', 'data': [start, end]}, None)

    expected = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
    actual = [supplier.next(i) for i in range(6)]

    assert expected == actual


def test_rand_range():
    spec = builder.Builder() \
        .add_field("field", builder.rand_range([100.9, 109.9], cast="int")) \
        .build()
    supplier = Loader(spec).get('field')

    first = supplier.next(0)
    assert str(first).isnumeric()
    # occasionally gets rounded down to 100
    assert 100 <= first <= 110


def test_nested_range_lists_simple():
    data = [
        [0, 10],
        [20, 30]
    ]
    spec = builder.single_field("field:range", data).build()
    supplier = Loader(spec).get('field')

    first = supplier.next(0)
    assert 0 <= first <= 10
    second = supplier.next(1)
    assert 20 <= second <= 30


def test_nested_range_lists_mixed_types_and_step():
    data = [
        [0, 10, 2],
        [20.0, 30.0]
    ]
    spec = builder.single_field("field:range", data).build()
    supplier = Loader(spec).get('field')

    first = supplier.next(0)
    assert first % 2 == 0
    assert 0 <= first <= 10
    second = supplier.next(1)
    assert 20.0 <= second <= 30.0


def test_nested_range_lists_mixed_types_and_step_cast():
    data = [
        [0.5, 2.5, 0.5],
        [20.01234, 30.56789]
    ]
    spec = builder.single_field("field:range?cast=str&precision=2", data).build()
    supplier = Loader(spec).get('field')

    assert supplier.next(0) == '0.5'
    assert supplier.next(1) == '20.01'


def test_float_range1():
    range_list = list(range_suppliers.float_range(1.0, 5.0, 1.0))
    assert range_list == [1.0, 2.0, 3.0, 4.0]


def test_float_range_with_precision1():
    range_list = list(range_suppliers.float_range(1.25, 2.25, 0.25, 2))
    assert range_list == [1.25, 1.5, 1.75, 2.0]


def test_float_range_with_precision2():
    range_list = list(range_suppliers.float_range(1.2499999, 2.2499999, 0.25, 2))
    assert range_list == [1.25, 1.5, 1.75, 2.0]
