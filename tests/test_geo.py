import decimal
from dataspec import builder, Loader
# need this to trigger registration
from dataspec.supplier.core import geo


def test_geo_lat_default_precision():
    spec = _geo_lat_spec()
    _test_geo_spec_falls_in_range(spec, 'lat', -90.0, 90.0, -4)


def test_geo_lat_precision():
    spec = _geo_lat_spec(precision=1)
    _test_geo_spec_falls_in_range(spec, 'lat', -90.0, 90.0, -1)


def test_geo_long_precision():
    spec = _geo_long_spec(precision=3)
    _test_geo_spec_falls_in_range(spec, 'long', -180.0, 180.0, -3)


def test_geo_long_precision_shorthand():
    spec = {"long:geo.long?precision=2": {}}
    _test_geo_spec_falls_in_range(spec, 'long', -180.0, 180.0, -2)


def _test_geo_spec_falls_in_range(spec, key, start, end, exponent):
    supplier = Loader(spec).get(key)
    value = supplier.next(0)
    _verify_in_range_and_has_precision(value, start, end, exponent)


def test_geo_spec_pair_default_order():
    spec = _geo_pair_spec(precision=1)
    supplier = Loader(spec).get('pair')
    value = supplier.next(0)
    parts = value.split(',')
    _verify_long(parts[0], -1)
    _verify_lat(parts[1], -1)


def test_geo_spec_pair_lat_first():
    spec = _geo_pair_spec(precision=2, lat_first="yes")
    supplier = Loader(spec).get('pair')
    value = supplier.next(0)
    parts = value.split(',')
    _verify_long(parts[1], -2)
    _verify_lat(parts[0], -2)


def test_geo_spec_pair_reduced_ranges():
    start_lat = 0.0
    end_lat = 75.0
    start_long = -180.0
    end_long = -90.0
    spec = _geo_pair_spec(
        start_lat=start_lat,
        end_lat=end_lat,
        start_long=start_long,
        end_long=end_long)

    supplier = Loader(spec).get('pair')
    value = supplier.next(0)
    parts = value.split(',')
    _verify_in_range_and_has_precision(parts[0], start_long, end_long, -4)
    _verify_in_range_and_has_precision(parts[1], start_lat, end_lat, -4)


def test_geo_spec_pair_reduced_ranges_bbox():
    start_lat = -90
    end_lat = -45.0
    start_long = 90.0
    end_long = 180.0

    spec = _geo_pair_spec(bbox=[start_long, start_lat, end_long, end_lat])

    supplier = Loader(spec).get('pair')
    value = supplier.next(0)
    parts = value.split(',')
    _verify_in_range_and_has_precision(parts[0], start_long, end_long, -4)
    _verify_in_range_and_has_precision(parts[1], start_lat, end_lat, -4)


def test_geo_pair_as_list():
    start_lat = -45.0
    end_lat = 45.0
    start_long = 50.0
    end_long = 60.0

    spec = _geo_pair_spec(bbox=[start_long, start_lat, end_long, end_lat], as_list=True)
    
    supplier = Loader(spec).get('pair')
    value = supplier.next(0)
    assert isinstance(value, list)
    _verify_in_range_and_has_precision(value[0], start_long, end_long, -4)
    _verify_in_range_and_has_precision(value[1], start_lat, end_lat, -4)


def _verify_lat(value, exponent):
    _verify_in_range_and_has_precision(value, -90.0, 90.0, exponent)


def _verify_long(value, exponent):
    _verify_in_range_and_has_precision(value, -180.0, 180.0, exponent)


def _verify_in_range_and_has_precision(value, start, end, exponent):
    as_decimal = decimal.Decimal(value)
    assert as_decimal >= start
    assert as_decimal <= end
    assert as_decimal.as_tuple().exponent == exponent


def _geo_lat_spec(**config):
    return builder.Builder() \
        .add_field('lat', builder.geo_lat(**config)) \
        .build()


def _geo_long_spec(**config):
    return builder.Builder() \
        .add_field('long', builder.geo_long(**config)) \
        .build()


def _geo_pair_spec(**config):
    return builder.Builder() \
        .add_field('pair', builder.geo_pair(**config)) \
        .build()
