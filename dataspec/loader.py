"""
Loader module is the interface into the dataspec data generation utility.  This class handles loading, parsing and
delegating the handling of various data types.
"""

import json
from typing import Union, Dict
from . import suppliers
from . import utils
from .model import DataSpec
from .types import lookup_type, lookup_schema, registry
from .schemas import validate_schema_for_spec
from .exceptions import SpecException


class Refs:
    """
    Holder object for references
    """

    def __init__(self, refspec):
        if refspec:
            self.refspec = refspec
        else:
            self.refspec = {}

    def get(self, key):
        """ get the ref for the key """
        return self.refspec.get(key)


class Loader:
    """
    Parent object for loading value suppliers from specs
    """
    RESERVED = ['type', 'data', 'ref', 'refs', 'config']

    def __init__(self, data_spec, data_dir='./data', enforce_schema=False):
        raw_spec = utils.get_raw_spec(data_spec)
        self.specs = preprocess_spec(raw_spec)
        self.datadir = data_dir
        self.enforce_schema = enforce_schema
        self.cache = {}
        self.refs = Refs(self.specs.get('refs'))

    def get(self, key):
        """
        Retrieve the value supplier for the given field or ref key

        :param key: key to for field or ref name
        """
        if key in self.cache:
            return self.cache[key]

        data_spec = self.specs.get(key)
        if data_spec is None:
            data_spec = self.refs.get(key)
        if data_spec is None:
            raise SpecException("No key " + key + " found in specs")
        supplier = self.get_from_spec(data_spec)
        self.cache[key] = supplier
        return supplier

    def get_from_spec(self, field_spec):
        """
        Retrieve the value supplier for the given field spec
        """
        if isinstance(field_spec, list):
            spec_type = None
        elif isinstance(field_spec, dict):
            spec_type = field_spec.get('type')
        else:
            # assume it is data, so values?
            spec_type = 'values'

        if spec_type == 'configref':
            raise SpecException(f'Cannot use configref as source of data: {json.dumps(field_spec)}')
        if spec_type is None or spec_type == 'values':
            if self.enforce_schema:
                _validate_schema_for_spec(spec_type, field_spec)
            supplier = suppliers.values(field_spec, self)
        else:
            handler = lookup_type(spec_type)
            if handler is None:
                raise SpecException('Unable to load handler for: ' + json.dumps(field_spec))
            if self.enforce_schema:
                _validate_schema_for_spec(spec_type, field_spec)
            supplier = handler(field_spec, self)
        if suppliers.is_cast(field_spec):
            supplier = suppliers.cast_supplier(supplier, field_spec)
        if suppliers.is_decorated(field_spec):
            supplier = suppliers.decorated(field_spec, supplier)
        if suppliers.is_buffered(field_spec):
            supplier = suppliers.buffered(supplier, field_spec)
        return supplier

    def get_ref_spec(self, key):
        """ returns the spec for the ref with the provided key """
        return self.refs.get(key)


def _validate_schema_for_spec(spec_type, field_spec):
    type_schema = lookup_schema(spec_type)
    if type_schema is None:
        return
    validate_schema_for_spec(spec_type, field_spec, type_schema)


def preprocess_spec(data_spec: Union[Dict[str, Dict], DataSpec]):
    """
    Uses the registered preprocessors to cumulatively update the spec
    :param data_spec: to preprocess
    :return: updated version of the spec after all preprocessors have run on it
    """
    raw_spec = utils.get_raw_spec(data_spec)
    updated = dict(raw_spec)
    preprocessors = registry.preprocessors.get_all()
    for name in preprocessors:
        preprocessor = registry.preprocessors.get(name)
        updated = preprocessor(updated)
    return updated
