import string
import pytest
from dataspec import builder, Loader, SpecException
from dataspec.supplier.core import unicode_range


def test_unicode_no_data_element():
    spec = builder.single_field("field", builder.unicode_range(data=None)).build()
    spec['field'].pop('data')

    with pytest.raises(SpecException):
        Loader(spec).get("field")


def test_unicode_data_is_not_list():
    spec = builder.single_field("field", builder.unicode_range(data="0x3040,0x309f")).build()
    with pytest.raises(SpecException):
        Loader(spec).get("field")


def test_unicode_range_single_range_as_hex():
    field_spec = builder.unicode_range(data=[0x3040, 0x309f], count=5)
    spec = builder.single_field("text", field_spec).build()
    supplier = Loader(spec).get('text')
    first = supplier.next(0)
    for c in first:
        assert 0x3040 <= ord(c) <= 0x309f


def test_unicode_range_single_range_as_hex_strings():
    field_spec = builder.unicode_range(data=[0x3040, 0x309f], mean=5, stddev=2, min=2, max=7)
    spec = builder.single_field("text", field_spec).build()
    supplier = Loader(spec).get('text')
    first = supplier.next(0)
    assert 2 <= len(first) <= 7
    for c in first:
        assert 0x3040 <= ord(c) <= 0x309f


def test_unicode_multiple_ranges():
    data = [
        ['0x0590', '0x05ff'],
        ['0x3040', '0x309f']
    ]
    field_spec = builder.unicode_range(data=data, min=3, max=7)
    spec = builder.single_field("text", field_spec).build()

    supplier = Loader(spec).get('text')
    first = supplier.next(0)
    assert 3 <= len(first) <= 7
    for c in first:
        assert 0x0590 <= ord(c) <= 0x05ff or 0x3040 <= ord(c) <= 0x309f
