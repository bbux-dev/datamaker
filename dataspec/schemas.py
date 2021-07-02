import json
import logging
import importlib.resources as pkg_resources
from jsonschema import Draft7Validator  # type: ignore
from dataspec import schema
from .exceptions import ResourceError, SpecException

log = logging.getLogger(__name__)


def load(key):
    """ load the schema for the provided key """
    naming_convention = f'{key}.schema.json'
    return _load_resource_as_json(naming_convention)


def _load_resource_as_json(resource_name):
    try:
        with pkg_resources.open_text(schema, resource_name) as schema_resource:
            return json.load(schema_resource)
    except FileNotFoundError as err:
        raise ResourceError(f'No resource with name {resource_name} was found') from err


def validate_schema_for_spec(spec_type, field_spec, type_schema):
    """ performs schema validation for the provided field_spec """
    definitions = _load_resource_as_json('definitions.json')
    if 'definitions' in type_schema:
        type_schema['definitions'].update(definitions['definitions'])
    else:
        type_schema['definitions'] = definitions['definitions']
    validator = Draft7Validator(type_schema)
    errors = sorted(validator.iter_errors(field_spec), key=lambda e: e.path)
    if len(errors) > 0:
        for error in errors:
            log.warning(error.message)
        raise SpecException(f'Failed to validate spec type: {spec_type} with spec: {field_spec}')
