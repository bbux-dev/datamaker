import os
import pytest
from dataspec.loader import Loader
from dataspec import builder, SpecException
# need this to trigger registration
from dataspec.supplier.core import csv

test_dir = os.sep.join([os.path.dirname(os.path.realpath(__file__)), 'data'])


# test data from https://wiki.splunk.com/Http_status.csv

def test_csv_valid_with_header_indexed_column():
    spec = _build_csv_spec('status')
    loader = Loader(spec, data_dir=test_dir)
    supplier = loader.get('status')

    assert supplier.next(0) == '100'
    # last entry
    assert supplier.next(39) == '505'
    # verify wrap around
    assert supplier.next(40) == '100'


def test_csv_valid_no_header_indexed_column():
    spec = _build_csv_spec('status', datafile="test_no_headers.csv", headers=False)
    loader = Loader(spec, data_dir=test_dir)
    supplier = loader.get('status')

    assert supplier.next(0) == '100'


def test_csv_valid_with_header_field_name_column():
    spec = _build_csv_spec('status', column="status")
    loader = Loader(spec, data_dir=test_dir)
    supplier = loader.get('status')

    assert supplier.next(0) == '100'


def test_csv_valid_with_header_field_name_column_shorthand():
    spec = {"status_desc:csv?datafile=test.csv&headers=true&column=2": {}}
    loader = Loader(spec, data_dir=test_dir)
    supplier = loader.get('status_desc')

    assert supplier.next(0) == 'Continue'


def test_csv_valid_sample_mode():
    spec = {"status_desc:csv?datafile=test.csv&headers=true&column=2&sample=true": {}}
    loader = Loader(spec, data_dir=test_dir)
    supplier = loader.get('status_desc')

    assert supplier.next(0) is not None


def test_csv_valid_sample_mode_with_count():
    spec = {"status_desc:csv?datafile=test.csv&headers=true&column=2&sample=true&count=2": {}}
    loader = Loader(spec, data_dir=test_dir)
    supplier = loader.get('status_desc')

    assert len(supplier.next(0)) == 2


def test_csv_valid_sample_mode_with_count_as_list():
    spec = {"status_desc:csv?datafile=test.csv&headers=true&column=2&sample=true": {"config": {"count": [4, 3, 2]}}}
    loader = Loader(spec, data_dir=test_dir)
    supplier = loader.get('status_desc')

    assert len(supplier.next(0)) == 4
    assert len(supplier.next(1)) == 3
    assert len(supplier.next(2)) == 2


def test_invalid_csv_config_unknown_key():
    # column name should be status not status_code
    spec = _build_csv_spec('status', column="status_code")
    _test_invalid_csv_config('status', spec)


def _test_invalid_csv_config(key, spec):
    loader = Loader(spec, data_dir=test_dir)
    with pytest.raises(SpecException) as err:
        next(spec.generator(1, data_dir=test_dir))


def test_csv_single_column():
    # we don't specify the column number or name, so default is to expect single column of values
    spec = {"user_agent:csv?datafile=single_column.csv&headers=false": {}}
    loader = Loader(spec, data_dir=test_dir)
    supplier = loader.get('user_agent')

    expected = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.2) Gecko/20090803 Firefox/3.5.2 Slackware'

    assert supplier.next(4) == expected


def _build_csv_spec(field_name, **config):
    base = {
        "datafile": "test.csv",
        "headers": True,
        "column": 1
    }
    base.update(config)
    return builder.Builder() \
        .add_field(field_name, builder.csv(**base)) \
        .build()


def test_buffered_csv_end_of_data_raises_spec_exception():
    csv_path = f'{test_dir}/test.csv'
    csv_data = csv.BufferedCsvData(csv_path, ',', '"', True, 5)
    with pytest.raises(SpecException):
        csv_data.next('status', 100, False, 1)


def test_buffered_csv_does_not_support_sample_mode():
    csv_path = f'{test_dir}/test.csv'
    do_sampling = True
    csv_data = csv.BufferedCsvData(csv_path, ',', '"', True, 5)
    with pytest.raises(SpecException):
        csv_data.next('status', 0, do_sampling, 1)


def test_buffered_csv_does_not_support_count_greater_than_one():
    csv_path = f'{test_dir}/test.csv'
    invalid_count = 2
    csv_data = csv.BufferedCsvData(csv_path, ',', '"', True, 5)
    with pytest.raises(SpecException):
        csv_data.next('status', 0, False, invalid_count)
