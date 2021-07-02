import os
import json
import pytest
import logging
from jsonschema import validate
from jsonschema.exceptions import ValidationError

log = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(message)s',
                    level=logging.INFO)

ASSUMED_VALID = "valid"
ASSUMED_INVALID = "invalid"
INSTANCE = "instance"
MESSAGE = "note"

root_dir = os.path.dirname(os.path.realpath(__file__))
schema_dir = os.path.realpath(os.sep.join([root_dir, '..', 'dataspec', 'schema']))
tests_dir = os.sep.join([root_dir, 'data'])


def test_values_schema():
    _test_run_validation("values.tests.json")


def test_range_schema():
    _test_run_validation("range.tests.json")


def test_combine_schema():
    _test_run_validation("combine.tests.json")


def test_combine_list_schema():
    _test_run_validation("combine_list.tests.json")


def test_uuid_schema():
    _test_run_validation("uuid.tests.json")


def test_char_class_schema():
    _test_run_validation("char_class.tests.json")


def test_date_schema():
    _test_run_validation("date.tests.json")


def test_geo_lat_schema():
    _test_run_validation("geo.lat.tests.json")


def test_geo_long_schema():
    _test_run_validation("geo.long.tests.json")


def test_geo_pair_schema():
    _test_run_validation("geo.pair.tests.json")


def test_unicode_range_schema():
    _test_run_validation("unicode_range.tests.json")


def test_ip_schema():
    _test_run_validation("ip.tests.json")


def test_select_list_subset():
    _test_run_validation("select_list_subset.tests.json")


def _test_run_validation(test_file_name):
    definitions = load_schema_file('definitions.json')
    tests = load_test_file(test_file_name)
    should_have_failed = {}
    for file, type_tests in tests.items():
        if 'EXAMPLE' in file:
            continue
        schema = load_schema_file(file)
        # hack for now
        schema['definitions'] = definitions['definitions']
        for should_be_valid in type_tests[ASSUMED_VALID]:
            validate(should_be_valid[INSTANCE], schema=schema)
        for should_not_be_valid in type_tests[ASSUMED_INVALID]:
            log.debug(json.dumps(should_not_be_valid))
            try:
                validate(should_not_be_valid[INSTANCE], schema=schema)
            except ValidationError:
                continue
            failed_for_file = should_have_failed.get(file)
            if failed_for_file is None:
                failed_for_file = []
            failed_for_file.append(should_not_be_valid)
            should_have_failed[file] = failed_for_file
    log_should_have_failed(should_have_failed)
    if len(should_have_failed) > 0:
        pytest.fail('Some invalid specs did not fail validation')


def log_should_have_failed(should_have_failed):
    for file, failed_for_file in should_have_failed.items():
        log.warning('Should have failed but did not for %s', file)
        for should_not_be_valid in failed_for_file:
            if MESSAGE in should_not_be_valid:
                log.warning(should_not_be_valid[MESSAGE])
            log.warning(should_not_be_valid[INSTANCE])


def test_validate_count_formats():
    definitions = load_schema_file('definitions.json')
    schema = definitions['definitions']['count']

    bad_counts = [
        True,  # invalid count type,
        [],  # empty count type,
        [1.1, 1.7],  # counts not integers
        {},  # empty count type
        {"one": 0.7, "two": 0.3},  # bad count keys
    ]

    for bad_count in bad_counts:
        # print(json.dumps(bad_count))
        with pytest.raises(ValidationError):
            validate(bad_count, schema=schema)


def load_test_file(file_name):
    return _load_file(tests_dir, file_name)


def load_schema_file(file_name):
    return _load_file(schema_dir, file_name)


def _load_file(root_dir, file_name):
    with open(os.sep.join([root_dir, file_name]), 'r') as handle:
        return json.load(handle)
