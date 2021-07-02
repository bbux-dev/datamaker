"""
Module for preprocessing spec before generating values. Exists to handle shorthand notation and
pushing params from URL form of field?param=value in to config object.
"""
import json
import logging
from urllib.parse import urlparse
from urllib.parse import parse_qs
import dataspec
from .exceptions import SpecException

log = logging.getLogger(__name__)


@dataspec.registry.preprocessors('default')
def preprocess_spec(raw_spec):
    """
    Preprocesses the spec into a format that is easier to use.
    Pushes all url params in keys into config object. Converts shorthand specs into full specs
    :param raw_spec: to preprocess
    :return: the reformatted spec
    """
    updated_specs = {}
    for key, spec in raw_spec.items():
        if key == 'refs':
            updated_specs[key] = preprocess_spec(raw_spec[key])
            continue
        if key == 'field_groups':
            updated_specs[key] = spec
            continue
        if '?' not in key:
            _update_no_params(key, spec, updated_specs)
        else:
            _update_with_params(key, spec, updated_specs)

    return updated_specs


@dataspec.registry.preprocessors('csv-select')
def preprocess_csv_select(raw_spec):
    """
    Converts and csv-select elements into standard csv ones
    :param raw_spec: to process
    :return: converted spec
    """
    updated_specs = {}
    for key, spec in raw_spec.items():
        if 'type' in spec and spec['type'] == 'csv_select':
            configref_name = f'{key}_configref'
            configref = {
                'type': 'configref',
                'config': spec.get('config', {})
            }
            if 'refs' not in raw_spec:
                updated_specs['refs'] = {configref_name: configref}
            else:
                updated_specs['refs'][configref_name] = configref
            for name, column in spec.get('data', {}).items():
                spec_for_column = {
                    'type': 'csv',
                    'config': {
                        'column': column,
                        'configref': configref_name
                    }
                }
                if name not in raw_spec:
                    updated_specs[name] = spec_for_column
                else:
                    alt_name = f'{name}-{column}'
                    updated_specs[alt_name] = spec_for_column
        else:
            updated_specs[key] = spec
    return updated_specs


@dataspec.registry.preprocessors('nested')
def preprocess_nested(raw_spec):
    """
    Converts all nested elements
    :param raw_spec: to process
    :return: converted spec
    """
    updated_specs = {}
    if 'refs' in raw_spec:
        if 'refs' in updated_specs:
            updated_specs['refs'].update(preprocess_spec(raw_spec['refs']))
        else:
            updated_specs['refs'] = preprocess_spec(raw_spec['refs'])
    for key, spec in raw_spec.items():
        if key == 'refs':
            # run preprocessors on refs too
            updated_refs = preprocess_spec(spec)
            updated_refs = preprocess_csv_select(updated_refs)
            # in case we have nested nested elements
            updated_refs = preprocess_nested(updated_refs)
            updated_specs['refs'] = updated_refs
            continue

        if 'type' in spec and spec['type'] == 'nested':
            if 'fields' not in spec:
                raise dataspec.SpecException('Missing fields key for nested spec: ' + json.dumps(spec))
            fields = spec['fields']
            updated = preprocess_spec(fields)
            updated = preprocess_csv_select(updated)
            # in case we have nested nested elements
            updated = preprocess_nested(updated)
            # this may have created a refs element, need to move this to the root
            _update_root_refs(updated_specs, updated)
            spec['fields'] = updated
            updated_specs[key] = spec
        else:
            updated_specs[key] = spec
    return updated_specs


def _update_root_refs(updated_specs, updated):
    """
    Updates to root refs if needed by popping the refs from the updated and merging with existing refs or creating
    a new refs element
    :param updated_specs: specs being updated
    :param updated: current updated spec that may have refs injected into it
    :return: None
    """
    if 'refs' in updated:
        refs = updated.pop('refs')
        if 'refs' in updated_specs:
            updated_specs.get('refs').update(refs)
        else:
            updated_specs['refs'] = refs


def _update_with_params(key, spec, updated_specs):
    """
    handles the case that there are ?param=value portions in the key
    These get stripped out and pushed into the config object
    """
    newkey, spectype, params = _parse_key(key)

    if newkey in updated_specs:
        raise SpecException(f'Field {key} defined multiple times: ' + json.dumps(spec))
    # the updated spec to populate
    updated = _convert_to_values_if_needed(spec, spectype)

    config = updated.get('config', {})
    config.update(params)
    updated['config'] = config
    if spectype:
        updated['type'] = spectype

    updated_specs[newkey] = updated


def _update_no_params(key, spec, updated_specs):
    """
    handles the case when there are no ?param=value portions in the key
    key may have name:type notation that still needs to be handled
    """
    if ':' in key:
        newkey, spectype = key.split(':', 2)
        if not _is_spec_data(spec, spectype):
            spec['type'] = spectype
        else:
            spec = {
                'type': spectype,
                'data': spec
            }
    else:
        newkey = key
    # check for conflicts
    if key in updated_specs:
        raise SpecException(f'Field {key} defined multiple times: ' + json.dumps(spec))

    spectype = spec.get('type') if isinstance(spec, dict) else None
    updated = _convert_to_values_if_needed(spec, spectype)

    updated_specs[newkey] = updated


def _convert_to_values_if_needed(spec, spectype):
    """ converts to a values spec if this is data only """
    if _is_spec_data(spec, spectype):
        return {
            'type': 'values',
            'data': spec
        }
    else:
        return spec


def _parse_key(field_name):
    """
    Expected key to have URL format. Two main forms:
    1. field:field_type?param1=val&param2=val...
    2. field?param1=val...
    """
    parsed_url = urlparse(field_name)
    parsed_query = parse_qs(parsed_url.query)
    if parsed_url.scheme:
        newkey = parsed_url.scheme
        spectype = parsed_url.path
    else:
        # case that the key portion has non standard chars such as _
        if ':' in parsed_url.path:
            newkey, spectype = parsed_url.path.split(':', 2)
        else:
            newkey = parsed_url.path
            spectype = None
    config = {}
    for key, value in parsed_query.items():
        if len(value) == 1:
            config[key.strip()] = value[0]
        else:
            config[key.strip()] = value

    return newkey, spectype, config


def _is_spec_data(spec, spectype):
    """
    Checks to see if the spec is data only
    :return: true if only data, false if it is a spec
    """
    if spec == 'nested' or spectype == 'nested':
        return False
    # if it is not a dictionary, then it is definitely not a spec
    if not isinstance(spec, dict):
        return True
    for core_field in ['type', 'data', 'config', 'ref', 'refs', 'fields']:
        if core_field in spec:
            return False
    # if empty, then may be using abbreviated notation i.e. field:type?param=value...
    if len(spec) == 0:
        return False
    # didn't find any core fields, and spec is not empty, so this must be data
    return True
