"""
Combine handler builds a combine value supplier from the provided spec

A combine Field Spec is used to concatenate or append two or more fields or reference to one another.
The combine field structure is:
{
  "<field name>": {
    "type": "combine",
    "fields": ["valid field name1", "valid field name2"],
    OR
    "refs": ["valid ref1", "valid ref2"],
    "config": { "join_with": "<optional string to use to join fields or refs, default is none"}
  }
}
"""
from typing import List
import json

import dataspec

COMBINE_KEY = 'combine'
COMBINE_LIST_KEY = 'combine-list'


class CombineValuesSupplier(dataspec.ValueSupplierInterface):
    """
    Class for combining the values from the output of two or more value suppliers
    """

    def __init__(self, suppliers: List[dataspec.ValueSupplierInterface], config: dict):
        self.suppliers = suppliers
        self.as_list = config.get('as_list', dataspec.types.get_default('combine_as_list'))
        self.joiner = config.get('join_with', dataspec.types.get_default('combine_join_with'))

    def next(self, iteration):
        values = [str(supplier.next(iteration)) for supplier in self.suppliers]
        if self.as_list:
            return values
        return self.joiner.join(values)


@dataspec.registry.schemas(COMBINE_KEY)
def get_combine_schema():
    """ get the schema for the combine type """
    return dataspec.schemas.load(COMBINE_KEY)


@dataspec.registry.schemas(COMBINE_LIST_KEY)
def get_combine_list_schema():
    """ get the schema for the combine_list type """
    return dataspec.schemas.load(COMBINE_LIST_KEY)


@dataspec.registry.types(COMBINE_KEY)
def configure_combine_supplier(field_spec, loader):
    """ configures supplier for combine type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise dataspec.SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))

    if 'refs' in field_spec:
        supplier = _load_from_refs(field_spec, loader)
    else:
        supplier = _load_from_fields(field_spec, loader)
    return supplier


@dataspec.registry.types(COMBINE_LIST_KEY)
def configure_combine_list_supplier(field_spec, loader):
    """ configures supplier for combine-list type """
    if 'refs' not in field_spec:
        raise dataspec.SpecException('Must define refs for combine-list type. %s' % json.dumps(field_spec))

    refs_list = field_spec['refs']
    if len(refs_list) < 1 or not isinstance(refs_list[0], list):
        raise dataspec.SpecException(
            'refs pointer must be list of lists: i.e [["ONE", "TWO"]]. %s' % json.dumps(field_spec))

    suppliers_list = []
    for ref in refs_list:
        spec = dict(field_spec)
        spec['refs'] = ref
        suppliers_list.append(_load_from_refs(spec, loader))
    return dataspec.suppliers.from_list_of_suppliers(suppliers_list, True)


def _load_from_refs(combine_field_spec, loader):
    """ loads the combine type from a set of refs """
    keys = combine_field_spec.get('refs')
    return _load(combine_field_spec, keys, loader)


def _load_from_fields(combine_field_spec, loader):
    """ load the combine type from a set of field names """
    keys = combine_field_spec.get('fields')
    return _load(combine_field_spec, keys, loader)


def _load(combine_field_spec, keys, loader):
    """ create the combine supplier for the types from the given keys """
    to_combine = []
    for key in keys:
        supplier = loader.get(key)
        to_combine.append(supplier)
    config = combine_field_spec.get('config', {})
    return CombineValuesSupplier(to_combine, config)
