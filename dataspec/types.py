"""
Module for the dataspec registration system
"""
from typing import Any
import logging
import catalogue  # type: ignore

log = logging.getLogger(__name__)


class registry:
    """
    Catalogue registry for types, preprocessors, logging configuration, and others
    """
    # types for field specs
    types = catalogue.create('dataspec', 'type')
    # schemas for field spec types
    schemas = catalogue.create('dataspec', 'schemas')
    # functions to modify specs before running
    preprocessors = catalogue.create('dataspec', 'preprocessor')
    # custom logging setup
    logging = catalogue.create('dataspec', 'logging')
    # registered formats for output
    formats = catalogue.create('dataspec', 'format')
    # different numeric distributions, normal, uniform, etc
    distribution = catalogue.create('dataspec', 'distribution')
    # default values
    defaults = catalogue.create('dataspec', 'defaults')


def lookup_type(key):
    """
    Looks up the type in the registry
    :param key: for type to look up
    :return: the type if found
    """
    return registry.types.get(key)


def lookup_schema(key):
    """
    Looks up the schema in the registry
    :param key: for schema to look up
    :return: the schema if found
    """
    all_keys = list(registry.schemas.get_all().keys())
    if key in all_keys:
        schema_load_function = registry.schemas.get(key)
    else:
        log.debug('No schema found for type %s', key)
        return None

    return schema_load_function()


def valid_formats():
    """ list of registered formats """
    return list(registry.formats.get_all().keys())


def get_default(key):
    """ get the default value for the specified key """
    func = registry.defaults.get(key)
    return func()


def set_default(key: str, value: Any):
    """ set the default value for the given key in the registry """
    registry.defaults.register(name=key, func=lambda *_: value)


def all_defaults():
    """ creates a dictionary of the current state of the registered defaults """
    return {k: get_default(k) for k in registry.defaults.get_all()}
