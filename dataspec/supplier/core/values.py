"""
Module for values type functionality
"""

import dataspec

VALUES_KEY = 'values'


@dataspec.registry.schemas(VALUES_KEY)
def get_schema():
    """ returns the values schema """
    return dataspec.schemas.load(VALUES_KEY)
