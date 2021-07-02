from dataspec.preprocessor import preprocess_spec, preprocess_csv_select, preprocess_nested
from dataspec.preprocessor import _parse_key, _is_spec_data, _update_no_params
from dataspec import builder, SpecException
import pytest

parse_key_tests = [
    (
        "field?param=value",
        "field",
        None,
        {"param": "value"}
    ),
    (
        "short_name?    param=value",
        "short_name",
        None,
        {"param": "value"}
    ),
    (
        "aligned:values?prefix=foo& suffix=bar",
        "aligned",
        "values",
        {"prefix": "foo", "suffix": "bar"}
    ),
    (
        "user_agent:csv?datafile=single_column.csv&headers=false",
        "user_agent",
        "csv",
        {"datafile": "single_column.csv", "headers": "false"}
    )
]


@pytest.mark.parametrize("input_key,expected_key,expected_type,expected_params", parse_key_tests)
def test_parse_key(input_key, expected_key, expected_type, expected_params):
    newkey, spectype, params = _parse_key(input_key)
    assert newkey == expected_key
    assert spectype == expected_type
    assert params == expected_params


specs_should_raise_exception = [
    {'foo?prefix=TEST': [1, 2, 3, 4, 5],
     'foo': [5, 6, 7]},
    {"one": {"type": "range", "data": [0, 9]},
     "one?prefix=withparams": [1, 2, 3]}
]


@pytest.mark.parametrize("spec", specs_should_raise_exception)
def test_preprocess_should_raise_spec_exception(spec):
    with pytest.raises(SpecException):
        preprocess_spec(spec)


default_transform_spec_tests = [
    (
        {'name': [1, 2, 3, 4, 5]},
        {'name': {'type': 'values', 'data': [1, 2, 3, 4, 5]}}
    ),
    (
        {'foo?prefix=TEST': [1, 2, 3, 4, 5]},
        {'foo': {'type': 'values', 'data': [1, 2, 3, 4, 5], 'config': {'prefix': 'TEST'}}}
    ),
    (
        {"foo:uuid": {}},
        {'foo': {'type': 'uuid'}}
    ),
    (
        {'bar?suffix=END': {'type': 'values', 'data': [1, 2, 3, 4], 'config': {'prefix': 'START'}}},
        {'bar': {'type': 'values', 'data': [1, 2, 3, 4], 'config': {'prefix': 'START', 'suffix': 'END'}}}
    ),
    (
        {'field_groups': [['one', 'two'], ['one', 'two', 'three']]},
        {'field_groups': [['one', 'two'], ['one', 'two', 'three']]}
    ),
    (
        {"network:ip?cidr=2.3.4.0/16": {}},
        {"network": {"type": "ip", "config": {"cidr": "2.3.4.0/16"}}}
    ),
    (
        {"geo:geo.pair": {}},
        {"geo": {"type": "geo.pair"}}
    ),
    (  # prefix in key overrides prefix in config for zero_to_ten
        {
            "zero_to_ten?prefix=A-": {"type": "range", "data": [0, 10, 0.5], "config": {"prefix": "C-"}},
            "ztt:range?prefix=B-": [0, 10, 0.5]
        },
        {
            "zero_to_ten": {"type": "range", "data": [0, 10, 0.5], "config": {"prefix": "A-"}},
            "ztt": {"type": "range", "data": [0, 10, 0.5], "config": {"prefix": "B-"}}
        }
    )
]


@pytest.mark.parametrize("input_spec,expected_output_spec", default_transform_spec_tests)
def test_preprocess_valid_specs(input_spec, expected_output_spec):
    updated = preprocess_spec(input_spec)
    assert updated == expected_output_spec


csv_select_transform_tests = [
    (
        {
            "placeholder": {"type": "csv_select", "data": {"one": 1, "two": 2, "six": 6},
                            "config": {"datafile": "not_real.csv", "headers": "no"}},
            "another:range": [1, 10]
        },
        {
            "one": {"type": "csv", "config": {"column": 1, "configref": "placeholder_configref"}},
            "two": {"type": "csv", "config": {"column": 2, "configref": "placeholder_configref"}},
            "six": {"type": "csv", "config": {"column": 6, "configref": "placeholder_configref"}},
            "another": {"type": "range", "data": [1, 10]},
            "refs": {
                "placeholder_configref": {"type": "configref", "config": {"datafile": "not_real.csv", "headers": "no"}}
            }
        }
    )
]


@pytest.mark.parametrize("input_spec,expected_output_spec", csv_select_transform_tests)
def test_preprocess_csv_select(input_spec, expected_output_spec):
    # need first layer of pre-processing done
    updated = preprocess_spec(input_spec)
    updated = preprocess_csv_select(updated)
    assert updated == expected_output_spec


nested_transform_tests = [
    (
        {
            "outer": {
                "type": "nested",
                "fields": {
                    "one:values": ["grey", "blue", "yellow"],
                    "two:range": [1, 10]
                }
            }
        },
        {
            "outer": {
                "type": "nested",
                "fields": {
                    "one": {"type": "values", "data": ["grey", "blue", "yellow"]},
                    "two": {"type": "range", "data": [1, 10]}
                }
            }
        }
    ),
    (
        {
            "outer:nested": {
                "fields": {
                    "placeholder": {"type": "csv_select", "data": {"one": 1, "two": 2, "six": 6},
                                    "config": {"datafile": "not_real.csv", "headers": "no"}}
                }
            },
            "another:range": [1, 10]
        },
        {
            "refs": {"placeholder_configref": {"type": "configref",
                                               "config": {"datafile": "not_real.csv", "headers": "no"}}},
            "outer": {
                "type": "nested",
                "fields": {
                    "one": {"type": "csv", "config": {"column": 1, "configref": "placeholder_configref"}},
                    "two": {"type": "csv", "config": {"column": 2, "configref": "placeholder_configref"}},
                    "six": {"type": "csv", "config": {"column": 6, "configref": "placeholder_configref"}}
                }
            },
            "another": {"type": "range", "data": [1, 10]},
        }
    ),
    (
        {
            "geo": {
                "type": "nested",
                "config": {"as_list": "true"},
                "fields": {"lat": 55.5, "long": 99.9}
            }
        }, {
            "geo": {
                "type": "nested",
                "config": {"as_list": "true"},
                "fields": {
                    "lat": {"type": "values", "data": 55.5},
                    "long": {"type": "values", "data": 99.9}
                }
            }
        },
    ),
    (
        {
            "one": {"type": "weightedref", "data": {"geo": 0.1}},
            "refs": {
                "geo": {
                    "type": "nested",
                    "config": {"as_list": "true"},
                    "fields": {
                        "lat": 55.5,
                        "long": 99.9
                    }
                }
            }
        },
        {
            "one": {"type": "weightedref", "data": {"geo": 0.1}},
            "refs": {
                "geo": {
                    "type": "nested",
                    "config": {"as_list": "true"},
                    "fields": {
                        "lat": {"type": "values", "data": 55.5},
                        "long": {"type": "values", "data": 99.9}
                    }
                }
            }
        }
    ),
    (
        builder.single_field('enemies', builder.nested(
            builder.single_field('inner', ['bat', 'slime', 'orc']).build())).build(),
        builder.single_field('enemies', builder.nested(
            builder.single_field('inner', builder.values(['bat', 'slime', 'orc'])).build())).build(),
    )
]


@pytest.mark.parametrize("input_spec,expected_output_spec", nested_transform_tests)
def test_preprocess_nested(input_spec, expected_output_spec):
    # need first layer of pre-processing done
    updated = preprocess_spec(input_spec)
    updated = preprocess_nested(updated)
    assert updated == expected_output_spec


def test_is_spec_data_positive_examples():
    examples = [
        1,
        'constant',
        25.5,
        ['a', 'b', 'c'],
        {'foo': 0.5, 'bar': 0.4, 'baz': 0.1}
    ]

    for example in examples:
        assert _is_spec_data(example, None)


def test_update_no_params():
    key = "field:nested"
    spec = {"id": {"type": "values", "data": [1, 2, 3]}}
    updated_specs = {}
    _update_no_params(key, spec, updated_specs)
    assert 'field' in updated_specs
    assert 'id' in updated_specs['field']
    assert 'nested' == updated_specs['field']['type']
