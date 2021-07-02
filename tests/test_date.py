import datetime
import re

import pytest

import dataspec
from dataspec.loader import Loader
from dataspec import builder
# need this to trigger type handler registration
from dataspec.supplier.core import date


def test_basic_spec():
    spec = _date_spec()
    values = _get_unique_values(spec, 'foo')
    assert len(values) > 0


date_duration_tests = [
    (0, 1, 2),
    (1, 1, 2),
    (5, 5, 6),
    (22, 22, 23),
    (55, 55, 56),
]


@pytest.mark.parametrize("duration, min, max", date_duration_tests)
def test_spec_builder(duration, min, max):
    spec = _date_spec(duration_days=duration)
    values = _get_unique_values(spec, 'foo', iterations=1000)
    # total number of values created should be in this range
    assert min <= len(values) <= max


def test_date_start_positive_duration():
    config = {"duration_days": 3, "start": "02-01-2050"}
    spec = _date_spec(**config)
    _test_date_spec(spec, 'foo', 100, ['02-01-2050', '03-01-2050', '04-01-2050'])


def test_date_start_format():
    config = {"duration_days": 3, "start": "02-Feb-2050", "format": "%d-%b-%Y"}
    spec = _date_spec(**config)
    _test_date_spec(spec, 'foo', 100, ['02-Feb-2050', '03-Feb-2050', '04-Feb-2050'])


def test_date_start_and_end_with_format():
    config = {"start": "02-Feb-2050", "end": "04-Feb-2050", "format": "%d-%b-%Y"}
    spec = _date_spec(**config)
    _test_date_spec(spec, 'foo', 100, ['02-Feb-2050', '03-Feb-2050', '04-Feb-2050'])


def test_date_start_format_iso():
    config = {"duration_days": 3, "start": "02-Feb-2050", "format": "%d-%b-%Y"}
    spec = _date_iso_spec(**config)
    _test_date_start_format_iso_type(spec)


def test_date_start_format_iso_microseconds():
    config = {"start": "02-Feb-2050", "end": "10-Feb-2050", "format": "%d-%b-%Y"}
    spec = _date_iso_us_spec(**config)
    _test_date_start_format_iso_type(spec)


def test_date_end_before_start():
    config = {"start": "15-Feb-2050", "end": "01-Feb-2050", "format": "%d-%b-%Y"}
    spec = _date_spec(**config)
    with pytest.raises(dataspec.SpecException):
        next(spec.generator(1))


def _test_date_start_format_iso_type(spec):
    loader = Loader(spec)
    supplier = loader.get('foo')
    # only the date portion of the iso date
    values = list(set([_date_only(supplier.next(i)) for i in range(100)]))
    for instance in ['2050-02-02', '2050-02-03', '2050-02-04']:
        assert instance in values


def _date_only(iso_string):
    return iso_string.split('T')[0]


def test_date_offset():
    # started to 7 Feb - 5 day offset gives center of 2 Feb +- 1 day
    config = {"duration_days": 1, "start": "07-Feb-2050", "format": "%d-%b-%Y", "offset": 5}
    spec = _date_spec(**config)
    _test_date_spec(spec, 'foo', 100, ['02-Feb-2050'])


def test_date_center_date():
    config = {"center_date": "15-Feb-2050", "stddev_days": 5, "format": "%d-%b-%Y"}
    spec = _date_spec(**config)
    _test_date_spec(spec, 'foo', 100, ['13-Feb-2050', '14-Feb-2050', '15-Feb-2050', '16-Feb-2050', '17-Feb-2050'])


def test_date_center_date_stddev_only():
    config = {"stddev_days": 5, "format": "%d-%b-%Y"}
    spec = _date_spec(**config)
    _test_date_spec(spec, 'foo', 100, [datetime.datetime.now().strftime(config['format'])])


def _test_date_spec(spec, key, iterations, expected):
    values = _get_unique_values(spec, key, iterations)
    for instance in expected:
        assert instance in values


def _get_unique_values(spec, key, iterations=100):
    loader = Loader(spec)
    supplier = loader.get(key)
    return list(set([supplier.next(i) for i in range(iterations)]))


def _date_spec(**config):
    return builder.Builder().add_field('foo', builder.date(**config)).build()


def _date_iso_spec(**config):
    return builder.Builder().add_field('foo', builder.date_iso(**config)).build()


def _date_iso_us_spec(**config):
    return builder.Builder().add_field('foo', builder.date_iso_us(**config)).build()
