import decimal
import dataspec.suppliers as suppliers


def test_random_range():
    value = suppliers.random_range(-180.0, -90.0, 7).next(0)
    as_decimal = decimal.Decimal(value)
    assert as_decimal >= -180.0
    assert as_decimal <= -90.0
    assert as_decimal.as_tuple().exponent == -7

