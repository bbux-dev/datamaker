"""
Module for key providers

A KeyProvider is used to supply the names of fields that should be used in the current record. Some times all the fields
will be used for every iteration.  Other times there will be different fields used in different records. This module
provides classes that provide these fields according to various schemes such as rotating lists or weighted lists.

"""
from typing import List, Tuple, Union, Dict
import json
from . import suppliers, ValueSupplierInterface
from .model import DataSpec
from .exceptions import SpecException

ROOT_KEYS = ['refs', 'field_groups']


class KeyProviderInterface:
    """ Interface for KeyProviders """

    def get(self) -> Tuple[str, List[str]]:
        """
        get the next set of field names to process
        :return: key_group_name, key_list_for_group_name
        """


def from_spec(specs: Union[dict, DataSpec]) -> KeyProviderInterface:
    """
    creates the appropriate key provider for the fields from the supplied spec

    if no field_groups key found, returns KeyProvider with all the fields provided for every iteration

    if field_groups is specified it can take one of three forms:
    1. List[List[str]] i.e:
    { "field_groups": [
        ["one", "two"],
        ["one", "two", "three"]
      ]
    }
    2. Dict[str, Dict[str, ] -> With weight and fields specified i.e.
    { "field_groups": {
      "groupA": {
        "weight": 0.7, "fields": ["one", "two"]
      },
      "groupB": {
        "weight": 0.3, "fields": ["one", "two", "three"]
      }
    }
    3. Dict[str, List[str]] -> This is called named groups
    {
      "groupA": ["one", "two"],
      "groupB": ["one", "two", "three"], ...
    }
    """
    if isinstance(specs, DataSpec):
        raw_spec = specs.raw_spec
    else:
        raw_spec = specs
    if 'field_groups' in raw_spec:
        field_groups = raw_spec['field_groups']
        if isinstance(field_groups, dict):
            if isinstance(list(field_groups.values())[0], list):
                return _create_rotating_lists_key_provider(field_groups)
            return _create_weighted_key_provider(field_groups)
        if isinstance(field_groups, list):
            return _create_rotating_lists_key_provider(field_groups)
    # default when no field groups specified
    keys = [key for key in raw_spec.keys() if key not in ROOT_KEYS]
    return KeyListProvider(keys)


class KeyListProvider(KeyProviderInterface):
    """ Class the provides static list of keys """

    def __init__(self, keys: List[str]):
        self.keys = keys

    def get(self):
        return 'ALL', self.keys


class RotatingKeyListProvider(KeyProviderInterface):
    """ Class the provides keys from list of various keys in rotating manner """

    def __init__(self, keys: List[Tuple[str, List[str]]]):
        """
        Keys should be list of tuples of form:
         [(name1, [key1, key2, ..., keyN]), (name2, [key1, key2, ...keyN), ...]
        :param keys: to rotate through
        """
        self.keys = keys
        self.cnt = 0

    def get(self):
        idx = self.cnt % len(self.keys)
        self.cnt += 1
        entry = self.keys[idx]
        # entry is tuple so should
        return entry


class WeightedGroupKeyProvider(KeyProviderInterface):
    """ Class that supplies keys according to weighted scheme """

    def __init__(self, field_groups: dict, supplier: ValueSupplierInterface, fields_key: str = 'fields'):
        self.field_groups = field_groups
        self.supplier = supplier
        self.fields_key = fields_key

    def get(self):
        key = self.supplier.next(0)
        if key not in self.field_groups or self.fields_key not in self.field_groups[key]:
            raise SpecException(
                f'Key: {key}, or fields key {self.fields_key} not found: {json.dumps(self.field_groups)}')
        return key, self.field_groups[key]['fields']


def _create_weighted_key_provider(field_groups: Dict) -> KeyProviderInterface:
    """ Creates a weighted field group key provide for the supplied field_groups """
    weights = {key: value['weight'] for key, value in field_groups.items()}
    supplier = suppliers.weighted_values(weights)
    return WeightedGroupKeyProvider(field_groups, supplier)


def _create_rotating_lists_key_provider(field_groups: Union[List, Dict]) -> KeyProviderInterface:
    """ Creates a rotating key list provider for the field_groups """
    if isinstance(field_groups, list):
        keys = [('_'.join(keys_list), keys_list) for keys_list in field_groups]
    elif isinstance(field_groups, dict):
        keys = [(key, value) for key, value in field_groups.items()]
    else:
        raise ValueError('Invalid type for field_groups only one of list or dict allowed')
    return RotatingKeyListProvider(keys)
