"""
This module handles the weightedref type.

A weighted ref spec is used to select the values from a set of refs in a weighted fashion.

The weightedref Field Spec structure is:
{
  "<field name>": {
    "type": "weightedref",
    "data": { "valid_ref_1": 0.N, "valid_ref_2": 0.N, ... }
  }
}
"""
import dataspec


class WeightedRefsSupplier(dataspec.ValueSupplierInterface):
    """
    Value supplier that uses a weighted scheme to supply values from different reference value suppliers
    """

    def __init__(self, key_supplier, values_map):
        self.key_supplier = key_supplier
        self.values_map = values_map

    def next(self, iteration):
        key = self.key_supplier.next(iteration)
        supplier = self.values_map.get(key)
        if supplier is None:
            raise dataspec.SpecException("Unknown Key '%s' for Weighted Reference" % key)
        return supplier.next(iteration)


@dataspec.registry.types('weightedref')
def configure_supplier(parent_field_spec, loader):
    """ configures supplier for weighted ref specs """
    config = dataspec.utils.load_config(parent_field_spec, loader)
    data = parent_field_spec['data']
    key_supplier = dataspec.suppliers.values(data)
    values_map = {}
    for key in data.keys():
        supplier = loader.get(key)
        values_map[key] = supplier
    supplier = WeightedRefsSupplier(key_supplier, values_map)
    if 'count' in config:
        return dataspec.suppliers.array_supplier(supplier, config)
    return supplier
