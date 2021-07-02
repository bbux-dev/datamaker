"""
Module for handling character class types
"""
import json
import string

import dataspec

CHAR_CLASS_KEY = 'char_class'
_UNDER_SCORE = '_'

_CLASS_MAPPING = {
    "ascii": ''.join(chr(x) for x in range(128)),
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "letters": string.ascii_letters,
    "word": f'{string.ascii_letters}{string.digits}{_UNDER_SCORE}',
    "printable": string.printable,
    "visible": ''.join(string.printable.split()),
    "punctuation": string.punctuation,
    "special": string.punctuation,
    "digits": string.digits,
    "hex": string.hexdigits,
    "hex-lower": string.digits + 'abcdef',
    "hex-upper": string.digits + 'ABCDEF',
}


@dataspec.registry.schemas(CHAR_CLASS_KEY)
def get_char_class_schema():
    """ get the schema for the char_class type """
    return dataspec.schemas.load(CHAR_CLASS_KEY)


for key in _CLASS_MAPPING.keys():
    @dataspec.registry.schemas("cc-" + key)
    def get_char_class_alias_schema():
        """ get the schema for the char_class type """
        return dataspec.schemas.load(CHAR_CLASS_KEY)


@dataspec.registry.types(CHAR_CLASS_KEY)
def configure_supplier(spec, _):
    """ configure the supplier for char_class types """
    if 'data' not in spec:
        raise dataspec.SpecException(f'Data is required field for char_class type: {json.dumps(spec)}')
    config = spec.get('config', {})
    data = spec['data']
    if isinstance(data, str) and data in _CLASS_MAPPING:
        data = _CLASS_MAPPING[data]
    if isinstance(data, list):
        new_data = [_CLASS_MAPPING[datum] if datum in _CLASS_MAPPING else datum for datum in data]
        data = ''.join(new_data)
    if 'exclude' in config:
        for char_to_exclude in config.get('exclude'):
            data = data.replace(char_to_exclude, '')
    if 'join_with' not in config:
        config['join_with'] = dataspec.types.get_default('char_class_join_with')
    if dataspec.utils.any_key_exists(config, ['mean', 'stddev']):
        return dataspec.suppliers.list_stat_sampler(data, config)
    return dataspec.suppliers.list_count_sampler(data, config)


@dataspec.registry.types('cc-ascii')
def configure_ascii_supplier(spec, loader):
    """ configure the supplier for char_class types """
    spec['data'] = 'ascii'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-lower')
def configure_lower_supplier(spec, loader):
    """ configure the supplier for lower char_class types """
    spec['data'] = 'lower'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-upper')
def configure_upper_supplier(spec, loader):
    """ configure the supplier for upper char_class types """
    spec['data'] = 'upper'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-letters')
def configure_letters_supplier(spec, loader):
    """ configure the supplier for letters char_class types """
    spec['data'] = 'letters'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-word')
def configure_word_supplier(spec, loader):
    """ configure the supplier for char_class types """
    spec['data'] = 'word'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-printable')
def configure_printable_supplier(spec, loader):
    """ configure the supplier for char_class types """
    spec['data'] = 'printable'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-visible')
def configure_visible_supplier(spec, loader):
    """ configure the supplier for visible char_class types """
    spec['data'] = 'visible'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-punctuation')
def configure_punctuation_supplier(spec, loader):
    """ configure the supplier for char_class types """
    spec['data'] = 'punctuation'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-special')
def configure_special_supplier(spec, loader):
    """ configure the supplier for special char_class types """
    spec['data'] = 'special'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-digits')
def configure_digits_supplier(spec, loader):
    """ configure the supplier for digits char_class types """
    spec['data'] = 'digits'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-hex')
def configure_hex_supplier(spec, loader):
    """ configure the supplier for hex char_class types """
    spec['data'] = 'hex'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-hex-lower')
def configure_hex_lower_supplier(spec, loader):
    """ configure the supplier for hex-lower char_class types """
    spec['data'] = 'hex-lower'
    return configure_supplier(spec, loader)


@dataspec.registry.types('cc-hex-upper')
def configure_hex_upper_supplier(spec, loader):
    """ configure the supplier for hex-upper char_class types """
    spec['data'] = 'hex-upper'
    return configure_supplier(spec, loader)
