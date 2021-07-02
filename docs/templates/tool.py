#!/bin/env python
"""
Utiltity to validate json and yaml example specs and apply them to templates for the READMEs
"""
import os
import glob
import json
import argparse
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-i', '--input', default="",
                        required=True, help='where to get the input')
    parser.add_argument('-t', '--template', default="FIELDSPECS.jinja.md",
                        help='where to get the input')
    parser.add_argument('-k', '--key-filter', dest='key_filter',
                        help='where to get the input')
    parser.add_argument('-m', '--mode', default="verify",
                        choices=['verify', 'test', 'apply', 'dump', 'dump-yaml', 'all'],
                        help='what mode to run in')
    parser.add_argument('-d', '--debug-data', dest='debug_data', action='store_true',
                        help='Dump out the combined data with schemas')

    args = parser.parse_args()

    with open(args.input, encoding='utf-8') as f:
        data = json.load(f)

    data = append_schemas(data)
    if args.debug_data:
        print(json.dumps(data, indent=4))
        return

    if args.mode == 'verify' or args.mode == 'all':
        verify_data(data.get('examples', {}), args.key_filter)
    if args.mode == 'apply' or args.mode == 'all':
        apply_template(data, args.template)
    if args.mode == 'dump':
        dump_data(data.get('examples', {}), args.key_filter)
    if args.mode == 'dump-yaml':
        dump_yaml(data.get('examples', {}), args.key_filter)


def append_schemas(data):
    for f in glob.glob(os.sep.join(['..', '..', 'dataspec', 'schema', '*.schema.json'])):
        with open(f) as handle:
            name = f.split(os.sep)[-1].replace('.schema.json', '')
            schema = json.load(handle)
            schemas = data.get('schemas', {})
            schemas[name] = schema
            data['schemas'] = schemas
    with open(os.sep.join(['..', '..', 'dataspec', 'schema', 'definitions.json'])) as handle:
        definitions = json.load(handle)
        schemas = data.get('schemas', {})
        schemas[name] = schema
        data["definitions"] = definitions["definitions"]
    return data


def dump_yaml(data, specific_keys):
    """
    Dumps the data for as yaml for inspection
    :param data: with json and yaml example specs
    :param specific_keys: to dump
    :return: None
    """
    for key, value in data.items():
        if specific_keys and key not in specific_keys:
            continue
        print(f'## {key}')
        if 'json' in value:
            data = json.loads(value['json'])
            print(yaml.dump(data))
        print()


def dump_data(data, specific_keys):
    """
    Dumps the data for inspection
    :param data: with json and yaml example specs
    :param specific_keys: to dump
    :return: None
    """
    for key, value in data.items():
        if specific_keys and key not in specific_keys:
            continue
        print(f'## {key}')
        if 'json' in value:
            print('```')
            print(value['json'])
            print('```')
            print()
        if 'yaml' in value:
            print('```')
            print(value['yaml'])
            print('```')
            print()
        if 'api' in value:
            print('```')
            print(value['api'])
            print('```')
            print()
        print()


def verify_data(data, specific_keys):
    """
    Performs validation to make sure the json and yaml specs can be parsed and are identical when evaluated
    :param data: with json and yaml specs
    :param specific_keys: to filter on
    :return: None
    """
    any_errors = False
    for key, value in data.items():
        if specific_keys and key not in specific_keys:
            continue
        jdata = None
        ydata = None
        if 'json' in value:
            try:
                jdata = json.loads(value['json'])
            except json.decoder.JSONDecodeError as err:
                any_errors = True
                print(f'{key}: error: {str(err)}')
                print(value)
        if 'yaml' in value:
            try:
                ydata = yaml.load(value['yaml'], Loader=yaml.FullLoader)
            except Exception as err:
                any_errors = True
                print(f'{key}: error: {str(err)}')
                print(value)
        if jdata is None:
            print(f"Unable to parse: {value.get('json')}")
        if ydata is None:
            print(f"Unable to parse: {value.get('yaml')}")
        if jdata != ydata:
            print(f'json and yaml data for key: {key} differ')
            print(json.dumps(jdata))
            print(json.dumps(ydata))
    if any_errors:
        print('Not all specs parsed successfully!')


def apply_template(data, template_name):
    """
    Apply the data to the template and print
    :param data: to apply
    :param template_name: name of template file to apply to, should be in current directory
    :return: None
    """
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_name)
    with open('..' + os.sep + 'FIELDSPECS.md', 'w', encoding='utf-8') as handle:
        handle.write(template.render(data))
    print('Updated ..' + os.sep + 'FIELDSPECS.md')


if __name__ == '__main__':
    main()
