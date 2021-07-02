import string
import pytest
from dataspec import builder, Loader, SpecException
from dataspec.supplier.core import char_class


def test_char_class_no_data_element():
    spec = _char_class_spec(data="special", count=4)
    spec['name'].pop('data')

    with pytest.raises(SpecException):
        Loader(spec).get('name')


def test_char_class_special_exclude():
    exclude = "&?!."
    spec = _char_class_spec(data="special", min=1, max=5, exclude=exclude)

    supplier = Loader(spec).get('name')
    _verify_values(supplier, 1, 5, exclude)


def test_char_class_word():
    spec = _char_class_spec(data="special", count=4)

    supplier = Loader(spec).get('name')
    _verify_values(supplier, 4, 4)


def test_char_class_stats_config():
    spec = _char_class_spec(data="word", mean=5, stddev=2, min=3, max=8)

    supplier = Loader(spec).get('name')
    _verify_values(supplier, 3, 8)


def test_char_class_printable():
    spec = _cc_abbrev_spec(abbrev="printable", mean=3, stddev=2, min=1, max=5)

    supplier = Loader(spec).get('name')
    _verify_values(supplier, 1, 5)


def test_char_class_abbreviations():
    abbreviations = ['cc-' + key for key in char_class._CLASS_MAPPING.keys()]

    for abbreviation in abbreviations:
        spec = _cc_abbrev_spec(abbrev=abbreviation, count=7)

        supplier = Loader(spec).get('name')
        _verify_values(supplier, 7, 7)


def test_char_class_multiple_classes():
    exclude = "CUSTOM"
    spec = _char_class_spec(data=["lower", "digits", "CUSTOM"], exclude=exclude)

    supplier = Loader(spec).get('name')
    value = supplier.next(0)
    assert isinstance(value, str)
    for char in value:
        assert char in string.ascii_lowercase or char in string.digits


def _verify_values(supplier, min_size, max_size, exclude='', iterations=100):
    for i in range(iterations):
        value = supplier.next(i)
        assert min_size <= len(value) <= max_size
        for excluded in exclude:
            assert excluded not in value


def _char_class_spec(data, **config):
    return builder.Builder() \
        .add_field("name", builder.char_class(data=data, **config)) \
        .build()


def _cc_abbrev_spec(abbrev, **config):
    return builder.Builder() \
        .add_field("name", builder.char_class_abbrev(cc_abbrev=abbrev, **config)) \
        .build()
