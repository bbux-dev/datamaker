import os
import pytest
import dataspec
from dataspec.loader import Loader
import dataspec.types as types
from dataspec.utils import load_custom_code

spec = {
    'foo': {
        'type': 'reverse_string',
        'ref': 'ONE'
    },
    'refs': {
        'ONE': {'type': 'values', 'data': ['raed a eod']}
    }
}

test_dir = f'{os.path.dirname(os.path.realpath(__file__))}/data'


class ReverseStringSupplier:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def next(self, iteration):
        value = str(self.wrapped.next(iteration))
        return value[::-1]


@dataspec.registry.types('reverse_string')
def configure_supplier(field_spec, loader):
    key = field_spec.get('ref')
    wrapped = loader.get(key)
    return ReverseStringSupplier(wrapped)


def test_registry_from_local():
    loader = Loader(spec)

    reg = types.registry
    all_types = reg.types.get_all()
    handler = all_types.get('reverse_string')

    supplier = handler(spec.get('foo'), loader)

    assert supplier.next(0) == 'doe a dear'


def test_registry_from_file():
    # string_reverser, same as above just different key
    load_custom_code(f'{test_dir}/custom.py')

    loader = Loader(spec)

    reg = types.registry
    all_types = reg.types.get_all()
    handler = all_types.get('string_reverser')

    supplier = handler(spec.get('foo'), loader)

    assert supplier.next(0) == 'doe a dear'


def test_registry_error_case():
    with pytest.raises(FileNotFoundError):
        # string_reverser, same as above just different key
        load_custom_code(f'{test_dir}/custom_does_not_exist.py')
