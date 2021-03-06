import string
import pytest
from dataspec import Loader, SpecException
from dataspec.type_handlers import char_class_handler


def test_char_class_no_data_element():
    spec = {
        "name": {
            "type": "char_class",
            "config": {"count": 4}
        }
    }

    with pytest.raises(SpecException):
        Loader(spec).get('name')


def test_char_class_special_exclude():
    exclude = "&?!."
    spec = {
        "name": {
            "type": "char_class",
            "data": "special",
            "config": {
                "min": 1,
                "max": 5,
                "exclude": exclude
            }
        }
    }

    supplier = Loader(spec).get('name')
    _verify_values(supplier, 1, 5, exclude)


def test_char_class_word():
    spec = {
        "name": {
            "type": "char_class",
            "data": "word",
            "config": {"count": 4}
        }
    }

    supplier = Loader(spec).get('name')
    _verify_values(supplier, 4, 4)


def test_char_class_stats_config():
    spec = {
        "name": {
            "type": "char_class",
            "data": "word",
            "config": {
                "mean": 5,
                "stddev": 2,
                "min": 3,
                "max": 8
            }
        }
    }

    supplier = Loader(spec).get('name')
    _verify_values(supplier, 3, 8)


def test_char_class_printable():
    spec = {
        "name": {
            "type": "cc-printable",
            "config": {
                "mean": 3,
                "stddev": 2,
                "min": 1,
                "max": 5
            }
        }
    }

    supplier = Loader(spec).get('name')
    _verify_values(supplier, 1, 5)


def test_char_class_abbreviations():
    abbreviations = ['cc-' + key for key in char_class_handler._CLASS_MAPPING.keys()]

    for abbreviation in abbreviations:
        spec = {
            "name": {
                "type": abbreviation,
                "config": {"count": 7}
            }
        }

        supplier = Loader(spec).get('name')
        _verify_values(supplier, 7, 7)


def test_char_class_multiple_classes():
    exclude = "CUSTOM"
    spec = {
        "name": {
            "type": "char_class",
            "data": ["lower", "digits", "CUSTOM"],
            "config": {
                "exclude": exclude
            }
        }
    }

    value = Loader(spec).get('name').next(0)
    for char in value:
        assert char in string.ascii_lowercase or char in string.digits


def _verify_values(supplier, min_size, max_size, exclude='', iterations=100):
    for i in range(iterations):
        value = supplier.next(i)
        assert min_size <= len(value) <= max_size
        for excluded in exclude:
            assert excluded not in value
