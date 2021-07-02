"""
Module for storing default settings across package
"""
from . import registry


@registry.defaults('sample_mode')
def default_list_sample_mode():
    """ By default we do not sample from lists backed types """
    return False


@registry.defaults('char_class_join_with')
@registry.defaults('combine_join_with')
def default_char_class_join_with():
    """ default join for char_class and combine types """
    return ''


@registry.defaults('combine_as_list')
@registry.defaults('geo_as_list')
def default_as_list_false():
    """ default as list for combine and geo types """
    return False


@registry.defaults('geo_lat_first')
def default_geo_lat_first():
    """ default lat first for geo types """
    return False


@registry.defaults('geo_join_with')
def default_geo_join_with():
    """ default join for geo types """
    return ','


@registry.defaults('date_stddev_days')
def default_date_stddev_days():
    """ default date stddev days """
    return 15


@registry.defaults('date_format')
def default_date_format():
    """ default date format """
    return "%d-%m-%Y"


@registry.defaults('geo_precision')
def default_geo_type_precision():
    """ default digits after decimal for geo types """
    return 4


@registry.defaults('json_indent')
def default_json_indent():
    """ default spaces to indent when using json-pretty formatter """
    return 4
