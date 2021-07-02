"""
Configures a supplier to provide a range of integers. Range is are inclusive for start and end

Range Spec format:

{
  "range_field": {
    "type": "range",
    "data": [start, stop, optional step]
  }
}
"""
import decimal
import json
import math

import dataspec

RANGE_KEY = 'range'
RAND_RANGE_KEY = 'rand_range'


@dataspec.registry.schemas(RANGE_KEY)
def get_range_schema():
    """ schema for range type """
    return dataspec.schemas.load(RANGE_KEY)


@dataspec.registry.schemas(RAND_RANGE_KEY)
def get_rand_range_schema():
    """ schema for rand range type """
    # This shares a schema with range
    return dataspec.schemas.load(RANGE_KEY)


@dataspec.registry.types(RANGE_KEY)
def configure_range_supplier(field_spec, _):
    """ configures the range value supplier """
    if 'data' not in field_spec:
        raise dataspec.SpecException('No data element defined for: %s' % json.dumps(field_spec))

    data = field_spec.get('data')
    if not isinstance(data, list) or len(data) < 2:
        raise dataspec.SpecException(
            'data element for ranges type must be list with at least two elements: %s' % json.dumps(field_spec))
    # we have the nested case
    if isinstance(data[0], list):
        suppliers_list = [_configure_supplier_for_data(field_spec, subdata) for subdata in data]
        return dataspec.suppliers.from_list_of_suppliers(suppliers_list, True)
    return _configure_supplier_for_data(field_spec, data)


def _configure_supplier_for_data(field_spec, data):
    """ configures the supplier based on the range data supplied """
    start = data[0]
    # default for built in range function is exclusive end, we want to default to inclusive as this is the
    # more intuitive behavior
    end = data[1] + 1
    if not end > start:
        raise dataspec.SpecException('end element must be larger than start: %s' % json.dumps(field_spec))
    if len(data) == 2:
        step = 1
    else:
        step = data[2]
    if _any_is_float(data):
        config = field_spec.get('config', {})
        precision = config.get('precision', None)
        if precision and not str(precision).isnumeric():
            raise dataspec.SpecException(f'precision must be valid integer {json.dumps(field_spec)}')
        range_values = list(float_range(float(start), float(end), float(step), precision))
    else:
        range_values = list(range(start, end, step))
    return dataspec.suppliers.values(range_values)


@dataspec.registry.types(RAND_RANGE_KEY)
def configure_rand_range_supplier(field_spec, loader):
    """ configures the random range value supplier """
    if 'data' not in field_spec:
        raise dataspec.SpecException('No data element defined for: %s' % json.dumps(field_spec))
    data = field_spec.get('data')
    config = dataspec.utils.load_config(field_spec, loader)
    if not isinstance(data, list) or len(data) == 0:
        raise dataspec.SpecException(
            'rand_range specs require data as array with at least one element: %s' % json.dumps(field_spec))
    start = 0
    if len(data) == 1:
        end = data[0]
    if len(data) >= 2:
        start = data[0]
        end = data[1]
    precision = None
    if len(data) > 2:
        precision = data[2]
    # config overrides third data element if specified
    precision = config.get('precision', precision)
    return dataspec.suppliers.random_range(start, end, precision)


def _any_is_float(data):
    """ are any of the items floats """
    for item in data:
        if isinstance(item, float):
            return True
    return False


def float_range(start, stop, step, precision=None):
    """
    Fancy foot work to support floating point ranges due to rounding errors with the way floating point numbers are
    stored
    """
    # attempt to defeat some rounding errors prevalent in python
    if precision:
        quantize = decimal.Decimal(str(1 / math.pow(10, int(precision))))
    current = decimal.Decimal(str(start))
    if precision:
        current = current.quantize(quantize)

    dstop = decimal.Decimal(str(stop))
    dstep = decimal.Decimal(str(step))
    while current < dstop:
        # inefficient?
        yield float(str(current))
        current = current + dstep
        if precision:
            current = current.quantize(quantize)
