import pytest
from dataspec import ResourceError, SpecException
from dataspec.schemas import load, validate_schema_for_spec
from dataspec.supplier.core import range_suppliers
from dataspec.supplier.core import values
import dataspec.types as types


def test_load_unknown_key():
    with pytest.raises(ResourceError):
        load('fluffy')


def test_load_valid():
    for type_name in ['range']:
        _test_load_valid(type_name)


def _test_load_valid(type_name):
    schema = load(type_name)
    assert schema is not None
    assert isinstance(schema, dict) is True


def test_lookup_from_registry():
    for type_name in ['range']:
        _test_lookup_from_registry(type_name)


def _test_lookup_from_registry(type_name):
    schema = types.lookup_schema(type_name)
    assert schema is not None
    assert isinstance(schema, dict) is True


def test_load_and_validate_schema():
    range_schema = types.lookup_schema('range')
    validate_schema_for_spec('range', {'type': 'range', 'data': [0, 10]}, range_schema)


def test_load_and_validate_invalid_schema():
    range_schema = types.lookup_schema('range')
    with pytest.raises(SpecException):
        validate_schema_for_spec('range', {'type': 'range'}, range_schema)


def test_invalid_count_param_values_spec():
    values_schema = types.lookup_schema('values')
    with pytest.raises(SpecException):
        spec = {'type': 'values', 'data': [1, 2, 3], 'config': {'count': {}}}
        validate_schema_for_spec('values', spec, values_schema)
