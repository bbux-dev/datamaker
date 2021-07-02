"""
Module for configref types
"""
import dataspec


@dataspec.registry.types('configref')
def configure_handler(_, __):
    """" Does nothing, just place holder """
