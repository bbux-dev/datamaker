import yaml
import json

from dataspec.loader import Loader
# to trigger registration
from dataspec.supplier.core import combine


yaml_spec = '''
---
foo:
  type: combine
  refs: [ONE, TWO]
  config:
    join_with: ''
refs:
  ONE:
    type: values
    data: [do, ca, pi]
  TWO:
    type: values
    data: [g, t, g]
'''

yaml_shorthand_spec = '''
---
foo?join_with=&quote=":
  type: combine
  refs: [ONE, TWO]
refs:
  ONE: [do, ca, pi]
  TWO: [g, t, g]
'''


def test_load_yaml():
    spec = yaml.load(yaml_spec, Loader=yaml.FullLoader)
    loader = Loader(spec)
    supplier = loader.get('foo')

    assert supplier.next(0) == 'dog'
    assert supplier.next(1) == 'cat'
    assert supplier.next(2) == 'pig'


def test_load_yaml_shorthand():
    spec = yaml.load(yaml_shorthand_spec, Loader=yaml.FullLoader)
    loader = Loader(spec)
    supplier = loader.get('foo')

    assert supplier.next(0) == '"dog"'
    assert supplier.next(1) == '"cat"'
    assert supplier.next(2) == '"pig"'
