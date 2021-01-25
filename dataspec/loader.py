import json
import dataspec.suppliers as suppliers
from dataspec.exceptions import SpecException
import dataspec.types as types


class Refs:
    """
    Holder object for references
    """

    def __init__(self, refspec):
        self.refspec = refspec

    def get(self, key):
        return self.refspec.get(key)


class Loader:
    """
    Parent object for loading value suppliers from specs
    """

    def __init__(self, specs):
        self.specs = _preprocess_spec(specs)
        self.cache = {}
        if 'refs' in specs:
            self.refs = Refs(self.specs.get('refs'))
        else:
            self.refs = None

    def get(self, key):
        """
        Retrieve the value supplier for the given field key

        :param key: key to use, may have url format i.e. field_name?param=value...
        """
        if key in self.cache:
            return self.cache[key]

        data_spec = self.specs.get(key)
        if data_spec is None:
            raise SpecException("No key " + key + " found in specs")
        return self.get_from_spec(data_spec)

    def get_from_spec(self, data_spec):
        """
        Retrieve the value supplier for the given field spec
        """
        if isinstance(data_spec, list):
            spec_type = None
        else:
            spec_type = data_spec.get('type')

        if spec_type is None or spec_type == 'values':
            supplier = suppliers.values(data_spec)
        else:
            handler = types.lookup_type(spec_type)
            if handler is None:
                raise SpecException('Unable to load handler for: ' + json.dumps(data_spec))
            supplier = handler(data_spec, self)

        if suppliers.isdecorated(data_spec):
            return suppliers.decorated(data_spec, supplier)
        return supplier


def _preprocess_spec(raw_spec):
    """
    Preprocesses the spec into a format that is easier to use.
    Pushes all url params in keys into config object. Converts shorthand specs into full specs
    :param raw_spec: to preprocess
    :return: the reformatted spec
    """
    updated = {}
    for key, spec in raw_spec.items():
        if '?' not in key:
            # check for conflicts
            if key in updated:
                raise SpecException(f'Field {key} defined multiple times: ' + json.dumps(spec))
            updated[key] = spec
        else:
            if ' ' in key:
                raise SpecException(f'Invalid url key {key}, no spaces allowed')
            newkey, params = key.replace('?', ' ').split(' ', 2)
            if newkey in updated:
                raise SpecException(f'Field {key} defined multiple times: ' + json.dumps(spec))
            if isinstance(spec, dict) and 'config' in spec:
                config = spec['config']
            else:
                config = {}
            for param in params.split('&'):
                keyvalue = param.split('=')
                config[keyvalue[0]] = keyvalue[1]

            if isinstance(spec, dict) and 'data' in spec:
                data = spec['data']
            else:
                data = spec

            updated[newkey] = {
                'type': 'values',
                'data': data,
                'config': config
            }
    if 'refs' in raw_spec:
        updated['refs'] = _preprocess_spec(raw_spec['refs'])
    return updated
