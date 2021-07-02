#!/bin/env python

import json
import logging
import yaml
from collections import OrderedDict
import subprocess
import argparse

from examples import EXAMPLES

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('example')

template = """
import dataspec

spec_builder = dataspec.spec_builder()

FRAGMENT

spec = spec_builder.build()
"""


def build_example(name, spec, iterations=5, pipes=""):
    if pipes is None:
        pipes = ""
    spec_string = json.dumps(spec.raw_spec)
    cmd = f"dataspec --inline '{spec_string}' --log-level error -i {iterations} {pipes}"
    out = subprocess.check_output(cmd, shell=True)
    cmd_display = cmd
    if len(spec_string) > 80:
        cmd_display = f"dataspec -s dataspec.json --log-level error -i {iterations} {pipes}"
    ordered = order_spec(spec.raw_spec)
    dirty_yaml = yaml.dump(ordered, sort_keys=False, width=4096).strip()
    cleaned_yaml = clean_semi_formatted_yaml(dirty_yaml)
    try:
        if yaml.load(cleaned_yaml) != spec.raw_spec:
            print('yaml does not match raw')
            print(name)
            print(json.dumps(yaml.load(cleaned_yaml), indent=4))
            print(json.dumps(spec.raw_spec, indent=4))
    except Exception:
        print('yaml does not load')
        print(cleaned_yaml)
        print(dirty_yaml)

    example = {
        "json": json.dumps(ordered, cls=MyEncoder, sort_keys=False, indent=2).strip(),
        "yaml": cleaned_yaml,
        "api": code.strip().replace('\n\n\n', '\n\n'),
        "command": cmd_display.strip(),
        "output": out.decode('utf-8').strip()
    }
    return example


def clean_semi_formatted_yaml(toclean: str):
    """
    Our custom YAML formatter adds a bunch of stuff we need to clean up since it is working with
    and OrderdDict as the underlying structure.
    """
    return toclean.replace('!!list ', '')


def order_spec(raw_spec):
    outer = {}
    for field, spec in raw_spec.items():
        if field == 'refs':
            continue
        outer[field] = order_field_spec(spec)
    if 'refs' in raw_spec:
        updated_refs = {}
        for ref, spec in raw_spec['refs'].items():
            updated_refs[ref] = order_field_spec(spec)
        outer['refs'] = updated_refs
    return outer


def order_field_spec(field_spec):
    if not isinstance(field_spec, dict):
        return NoIndent(field_spec)
    ordered = OrderedDict()
    if 'type' in field_spec:
        ordered['type'] = field_spec['type']
    if 'data' in field_spec:
        ordered['data'] = NoIndent(field_spec['data'])
    if 'refs' in field_spec:
        refs = field_spec['refs']
        if isinstance(refs[0], list):
            ordered['refs'] = [NoIndent(ref) for ref in refs]
        else:
            ordered['refs'] = NoIndent(refs)
    for key in ['config', 'ref', 'fields']:
        if key in field_spec:
            ordered[key] = field_spec[key]
    for key, val in field_spec.items():
        if key not in ['type', 'data', 'config', 'ref', 'refs', 'fields']:
            ordered[key] = val
    return ordered


##################################
# from https://stackoverflow.com/questions/13249415/how-to-implement-custom-indentation-when-pretty-printing-with-the-json-module
##################################
from _ctypes import PyObj_FromPtr
import json
import re


class NoIndent(object):
    """ Value wrapper. """

    def __init__(self, value):
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        """
        Added to support formatting for YAML
        """
        return representer.represent_scalar(' ', u'{.value}'.format(node))


class MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))

    def __init__(self, **kwargs):
        # Save copy of any keyword argument values needed for use here.
        self.__sort_keys = kwargs.get('sort_keys', None)
        super(MyEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, NoIndent)
                else super(MyEncoder, self).default(obj))

    def encode(self, obj):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.
        json_repr = super(MyEncoder, self).encode(obj)  # Default JSON.

        # Replace any marked-up object ids in the JSON repr with the
        # value returned from the json.dumps() of the corresponding
        # wrapped Python object.
        for match in self.regex.finditer(json_repr):
            # see https://stackoverflow.com/a/15012814/355230
            id = int(match.group(1))
            no_indent = PyObj_FromPtr(id)
            json_obj_repr = json.dumps(no_indent.value, sort_keys=self.__sort_keys)

            # Replace the matched id string with json formatted representation
            # of the corresponding Python object.
            json_repr = json_repr.replace(
                '"{}"'.format(format_spec.format(id)), json_obj_repr)

        return json_repr


#########################
# from https://til.simonwillison.net/python/style-yaml-dump
# via: https://stackoverflow.com/a/8641732 and https://stackoverflow.com/a/16782282
#########################
def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u"tag:yaml.org,2002:map", value)


yaml.add_representer(OrderedDict, represent_ordereddict)


def represent_noindent(dumper, data):
    if isinstance(data.value, list):
        return dumper.represent_sequence("tag:yaml.org,2002:list", data.value, flow_style=True)
    if isinstance(data.value, dict):
        return dumper.represent_mapping("tag:yaml.org,2002:map", data.value, flow_style=True)
    return dumper.represent_data(data.value)


yaml.add_representer(NoIndent, represent_noindent)
######################
# Begin Processing
#####################
parser = argparse.ArgumentParser(description='')
parser.add_argument('-k', '--key-filter', dest='key_filter',
                    help='where to get the input')

args = parser.parse_args()

built_examples = {}
for name, iterations, fragment, pipes in EXAMPLES:
    if args.key_filter and name not in args.key_filter:
        continue
    code = template.replace('FRAGMENT', fragment)
    try:
        log.info(name)
        log.debug(code)
        exec(code)
        # spec should be created when running exec
        data = build_example(name, spec, iterations, pipes)
        built_examples[name] = data
    except (TypeError, SyntaxError) as err:
        print(err)
        print(name)
        print(code)
        raise Exception() from err
        # exit(-1)

print(json.dumps({"examples": built_examples}, cls=MyEncoder, sort_keys=False, indent=2))
