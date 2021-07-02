Data Spec Repository
========================
[![Build Status](https://travis-ci.com/bbux-dev/dataspec.svg?branch=main)](https://travis-ci.com/bbux-dev/dataspec)
[![codecov](https://codecov.io/gh/bbux-dev/dataspec/branch/main/graph/badge.svg?token=QFA9QZTQ05)](https://codecov.io/gh/bbux-dev/dataspec)


1. [Overview](#Overview)
1. [Build](#Build)
1. [Usage](#Usage)
   1. [Example Usage](#ExampleUsage)
   1. [Useful Flags](#UsefulFlags)
1. [Examples](#Examples)
1. [Core Concepts](#Core_Concepts)
    1. [Data Spec](#Data_Spec)
        1. [YAML Format](#YAML_Format)
    1. [Field Specs](#Field_Specs)
    1. [Field Groups](#FieldGroups)
    1. [Notes on CSV Inputs](#CSV_Inputs)
    1. [Templating](#Templating)
        1. [Loops in Templates](#Templating_Loops)
        1. [Dynamic Loop Counters](#Dynamic_Loop_Counters)
    1. [Custom Code Loading](#Custom_Code_Loading)
1. [Programmatic Usage](#Programmatic)
    1. [Building Specs](#BuildSpecs)
    1. [Generating Records](#Generator)

## <a name="Overview"></a>Overview

This is a tool for making data according to specifications. The goal is to separate the structure of the data from the
values that populate it. We do this by defining two core concepts the Data Spec and the Field Spec. A Data Spec is used
to define all of the fields that should be generated for a record. The Data Spec does not care about the structure that
the data will populate. A single Data Spec could be used to generate JSON, XML, or a csv file. Each field in the Data
Spec has its own Field Spec that defines how the values for it should be created. There are a variety of core field
types that are used to generate the data for each field. Where the built-in types are not sufficient, there is an easy
way to create custom types and handlers for them. The tool supports templating using
the [Jinja2](https://pypi.org/project/Jinja2/) templating engine format.

Data is a key part of any application.  Synthetic data can be used to test and exercise a system while it is under
development or modification.  By using a Data Spec to generate this synthetic data, it is more compact and easier to
modify, update and manage.  It also lends itself to sharing. Instead of hosting large data files full of synthetic test
data, you can build Data Specs that encapsulate the information needed to generate the data. If well-designed, these
can be easier to inspect and reason through compared with scanning thousands of lines of a csv file.

## <a name="Build"></a>Build

To Install:

```shell script
pip install git+https://github.com/bbux-dev/dataspec.git
```

This will install the `dataspec` command line utility which should now be on your path. Assumes there is a python
executable on the path.

## <a name="Usage"></a>Usage

```
usage: dataspec [-h] [-s SPEC] [--inline INLINE] [-i ITERATIONS] [-o OUTDIR] [-p OUTFILEPREFIX] [-e EXTENSION] [-t TEMPLATE] [-r RECORDSPERFILE] [-k] [-c CODE [CODE ...]]
                [-d DATADIR] [-l LOG_LEVEL] [-f FORMAT] [--strict] [--apply-raw] [--debug-spec] [--debug-defaults] [-x] [--sample-lists] [--defaults DEFAULTS]

Run dataspec.

optional arguments:
  -h, --help            show this help message and exit
  -i ITERATIONS, --iterations ITERATIONS
                        Number of Iterations to Execute
  -o OUTDIR, --outdir OUTDIR
                        Output directory
  -p OUTFILEPREFIX, --outfile-prefix OUTFILEPREFIX
                        Prefix for output files, default is generated
  -e EXTENSION, --extension EXTENSION
                        Extension to add to generated files
  -t TEMPLATE, --template TEMPLATE
                        Path to template to populate
  -r RECORDSPERFILE, --records-per-file RECORDSPERFILE
                        Number of records to place in each file, default is all, requires -o to be specified
  -k, --printkey        When printing to stdout field name should be printed along with value
  -c CODE [CODE ...], --code CODE [CODE ...]
                        Path to custom defined functions in one or more modules to load
  -d DATADIR, --datadir DATADIR
                        Path to external directory to load external data files such as csvs
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Logging level verbosity, default is info, valid are "debug","info","warn","error","off"
  -f FORMAT, --format FORMAT
                        Formatter for output records, default is none, valid are: ['json', 'json-pretty', 'csv']
  --strict              Enforce schema validation for all registered field specs
  --apply-raw           Data from -s argument should be applied to the template with out treating as a Data Spec
  --debug-spec          Debug spec after internal reformatting
  --debug-defaults      List default values from registry after any external code loading
  -x, --exclude-internal
                        Do not include non data fields in output records
  --sample-lists        Turns on sampling for all list backed types
  --defaults DEFAULTS   Path to defaults overrides

input:
  -s SPEC, --spec SPEC  Spec to Use
  --inline INLINE       Spec as string
```

### <a name="ExampleUsage"></a>Example Usage

The most common way to use `dataspec` is to define the field specifications in a JSON or YAML file and to specify this file with
the --spec command line argument:

```shell
dataspec --spec /path/to/dataspec.json \
  --template /path/to/template.jinja
  --iterations 1000 \
  --output /path/to/output
```

The command above will generate 1000 records and apply the generated values to the supplied template which will be
output to the specified directory. The default is to write all outputs to a single file.  Use the `-r` or
`--records-per-file` command line argument to modify this if desired.

An alternative way to specify the data for a spec is by using the `--inline` argument:

```shell
dataspec \
  --inline '{ "handle": { "type": "cc-word", "config": {"min": 3, "mean": 5, "prefix": "@" } } }' \
  --iterations 5
INFO [12-Mar-2050 06:24:58 PM] Starting Loading Configurations...
INFO [12-Mar-2050 06:24:58 PM] Starting Processing...
@QEWXL_
@0zTDhp
@5hK
@ufqd
INFO [12-Mar-2050 06:24:58 PM] Finished Processing
```

This can be useful for troubleshooting or experimenting

### <a name="UsefulFlags"></a>Useful Flags

#### Inline JSON/YAML

To test small spec fragments, you can use the `--inline <spec>` flag. Example:

```shell
dataspec --inline '{ "handle": { "type": "cc-word", "config": {"min": 3, "mean": 5, "prefix": "@" } } }' \
  --iterations 5 \
  --printkey \
  --log-level off
handle -> @r3Wl
handle -> @cCyfSeU
handle -> @l8n
handle -> @aUb
handle -> @jf7Ax
```
#### Log Levels

You can change the logging levels to one of `debug, info, warn, error, or off` by using the `-l` or `--log-level` flag.
See example above.

#### Formatting Output

Sometimes it may be useful to dump the generated data into a format that is easier to consume or view. Use the `-f` or `--format` flag to specify one
of `json` or `json-pretty` or `csv`. The `json` format will print a flat version of each record that takes up a single line for each iteration. The
`json-pretty` format will print an indented version of each record that will span multiple lines. The `csv` format will output each record as a comma
separated value line.  Examples:

```shell
# NOTE: This inline spec is in YAML
dataspec --inline 'handle: { type: cc-word, config: {min: 3, mean: 5, prefix: "@" } }' \
    --iterations 2 \
    --log-level off \
    --format json
{"handle": "@a2oNt"}
{"handle": "@lLN3i"}

dataspec --inline 'handle: { type: cc-word, config: {min: 3, mean: 5, prefix: "@" } }' \
    --iterations 2 \
    --log-level off \
    --format json-pretty
{
    "handle": "@ZJeE_f"
}
{
    "handle": "@XmJ"
}
dataspec --inline '{"id:uuid": {}, "handle": { "type": "cc-word", "config": {"min": 3, "mean": 5, "prefix": "@" } }' \
41adb77f-d7b3-4a31-a75b-5faff33d5eb8,@U0gI
d97e8dad-8dfd-49f1-b25e-eaaf2d6953fd,@IYn
```

#### <a name="ApplyRaw"></a>Apply Raw `--apply-raw`

The `--apply-raw` command line flag will treat the argument of the `-s` flag as the raw-data that should be applied to
the template. This can be helpful when working on adjusting the template that is being generated. You can dump the
generated data from N iterations using the `--format json` or `--format json-pretty` then use this as raw input to the
template file.

#### Debugging Specifications

There are a bunch of shorthand formats for creating specifications.  These ultimately get turned into a full spec format.
It may be useful to see what the full spec looks like after all the transformations have taken place.  Use the
`--debug-spec` to dump the internal form of the specification for inspection.

```shell
dataspec --inline 'geo:geo.pair?start_lat=-99.0: {}' \
  --log-level off \
  --debug-spec
{
    "geo": {
        "config": {
            "start_lat": "-99.0"
        },
        "type": "geo.pair"
    }
}
```

#### Schema Level Validation

Most of the default supported field spec types have JSON based schemas defined
for them. Schema based validation is turned off by default. Use the `--strict`
command line flag to turn on the strict schema based checks for types that have
schemas defined. Example:

```shell
dataspec --inline 'geo: {type: geo.pair, config: {start_lat: -99.0}}' \
    --iterations 2 \
    --log-level info \
    --format json \
    --strict
INFO [12-Mar-2050 07:24:11 PM] Starting Loading Configurations...
INFO [12-Mar-2050 07:24:11 PM] Starting Processing...
WARNING [12-Mar-2050 07:24:11 PM] -99.0 is less than the minimum of -90
ERROR [12-Mar-2050 07:24:11 PM] Failed to validate spec type: geo.pair with spec: {'type': 'geo.pair', 'config': {'start_lat': -99.0}}
```

#### Default Values

There are some default values used when a given spec does not provide them.
These defaults can be viewed using the `--debug-defaults` flag.

```shell
dataspec --debug-defaults -l off
{
    "sample_mode": false,
    "combine_join_with": "",
    "char_class_join_with": "",
    "geo_as_list": false,
    "combine_as_list": false,
    "geo_lat_first": false,
    "geo_join_with": ",",
    "date_stddev_days": 15,
    "date_format": "%d-%m-%Y",
    "geo_precision": 4,
    "json_indent": 4
}
```

The general convention is to use the type as a prefix for the key that it
effects. You can save this information to disk by specifying the `-o`
or `--outdir` flag. In the output above the default `join_with` config param is
a comma for the `geo` type, but is an empty string for the `combine`
and `char_class` types.

#### Override Defaults

To override the default values, use the `--defaults` /path/to/custom_defaults.json

```shell
dataspec --debug-defaults -l off --defaults /path/to/custom_defaults.json
{
    "sample_mode": true,
    "combine_join_with": ";",
    "char_class_join_with": "-",
    "geo_as_list": true,
    "combine_as_list": false,
    "geo_lat_first": false,
    "geo_join_with": ",",
    "date_stddev_days": 42,
    "date_format": "%Y-%m-%d",
    "geo_precision": 5,
    "json_indent": 2,
    "custom_thing": "foo"
}
```

## <a name="Examples"></a>Examples

See [examples](docs/EXAMPLES.md) to dive into detailed example and practical use case.

## <a name="Core_Concepts"></a>Core Concepts

### <a name="Data_Spec"></a>Data Spec

A Data Spec is a Dictionary where the keys are the names of the fields to
generate and each value is a [Field Spec](docs/FIELDSPECS.md)
that describes how the values for that field are to be generated. There is one
reserved key in the root of the Data Spec: refs. The refs is a special section
of the Data Spec where Field Specs are defined but not tied to any specific
field. These refs can then be used or referenced by other Specs. An example
would be a combine Spec which points to two references that should be joined.
Below is an example Data Spec for creating email addresses.

```json
{
  "email": {
    "type": "combine",
    "refs": ["HANDLE", "DOMAINS"],
    "config": {"join_with": "@"}
  },
  "refs": {
    "HANDLE": {
      "type": "combine",
      "refs": ["ANIMALS", "ACTIONS"],
      "config": {"join_with": "_"}
    },
    "ANIMALS": {
      "type": "values",
      "data": ["zebra", "hedgehog", "llama", "flamingo"]
    },
    "ACTIONS?sample=true": {
      "type": "values",
      "data": ["fling", "jump", "launch", "dispatch"]
    },
    "DOMAINS": {
      "type": "values",
      "data": {"gmail.com": 0.6, "yahoo.com": 0.3, "hotmail.com": 0.1}
    }
  }
}
```

This Data Spec uses two Combine Specs to build up the pieces for the email address. The first Combine Spec lives in the
Refs section. This one creates the user name or handle by combining the values generated by the ANIMALS Ref with the
ACTIONS one. The email field then combines the HANDLE Ref with the DOMAINS one. See [Field Specs](docs/FIELDSPECS.md)
for more details on each of the Field Specs used in this example.

Running dataspec from the command line against this spec:

```shell script
dataspec -s ~/example.json -i 12
zebra_jump@gmail.com
hedgehog_launch@yahoo.com
llama_launch@yahoo.com
flamingo_launch@gmail.com
zebra_jump@hotmail.com
hedgehog_jump@hotmail.com
llama_dispatch@gmail.com
flamingo_fling@yahoo.com
zebra_fling@yahoo.com
hedgehog_launch@gmail.com
llama_jump@gmail.com
flamingo_jump@gmail.com
```

#### <a name="YAML_Format"></a>YAML Format

Data specs can also be created using YAML. Below is the same spec above in YAML.

```yaml
---
email:
  type: combine
  refs:
    - HANDLE
    - DOMAINS
  config:
    join_with: "@"
refs:
  HANDLE:
    type: combine
    refs:
      - ANIMALS
      - ACTIONS
    config:
      join_with: _
  ANIMALS:
    type: values
    data: [ zebra, hedgehog, llama, flamingo ]
  ACTIONS?sample=true:
    type: values
    data: [ fling, jump, launch, dispatch ]
  DOMAINS:
    type: values
    data:
      gmail.com: 0.6
      yahoo.com: 0.3
      hotmail.com: 0.1
```

### <a name="Field_Specs"></a>Field Specs

See [field specs](docs/FIELDSPECS.md) and [schemas](docs/SCHEMAS.md) for details.

### <a name="FieldGroups"></a>Field Groups

Field groups provide a mechanism to generate different subsets of the defined fields together. This can be useful when
modeling data that contains field that are not present in all records. There are several formats that are supported
for Field Groups. Field Groups are defined in a root section of the document named `field_groups`. Below is an example
spec with no `field_groups` defined.

```json
{
  "id": {"type": "range", "data": [1, 100]},
  "name": ["Fido", "Fluffy", "Bandit", "Bingo", "Champ", "Chief", "Buster", "Lucky"],
  "tag": {
    "Affectionate": 0.3, "Agreeable": 0.1, "Charming": 0.1,
    "Energetic": 0.2, "Friendly": 0.4, "Loyal": 0.3,
    "Aloof": 0.1
  }
}
```

If the tag field was only present in 50% of the data, we would want to be able to adjust our output to match this. Here
is an updated version of the spec with the `field_groups` specified to give us our 50/50 output. This uses the first
form of the `field_groups` a List of Lists of field names to output together.

```json
{
  "id": {"type": "range", "data": [1, 100]},
  "name": ["Fido", "Fluffy", "Bandit", "Bingo", "Champ", "Chief", "Buster", "Lucky"],
  "tag": {
    "Affectionate": 0.3, "Agreeable": 0.1, "Charming": 0.1,
    "Energetic": 0.2, "Friendly": 0.4, "Loyal": 0.3,
    "Aloof": 0.1
  },
  "field_groups": [
    ["id", "name"],
    ["id", "name", "tag"]
  ]
}
```

If we need more precise weightings we can use the second format where we specify a weight for each field group along
with the fields that should be output together.

```json
{
  "id": "...",
  "name": "...",
  "tag": "...",
  "field_groups": {
    "thirty_percent": {
      "weight": 0.3,
      "fields": ["id", "name"]
    },
    "two": {
      "weight": 0.7,
      "fields": ["id", "name", "tag"]
    }
  }
}
```

The keys of the `field_groups` dictionary are arbitrary. The `weight` and `fields` element underneath are required.

Running this example:

```shell
dataspec -s pets.json -i 10 -l off -x --format json
{"id": 1, "name": "Fido"}
{"id": 2, "name": "Fluffy", "tag": "Agreeable"}
{"id": 3, "name": "Bandit", "tag": "Affectionate"}
{"id": 4, "name": "Bingo"}
{"id": 5, "name": "Champ", "tag": "Loyal"}
{"id": 6, "name": "Chief"}
{"id": 7, "name": "Buster", "tag": "Friendly"}
{"id": 8, "name": "Lucky", "tag": "Loyal"}
{"id": 9, "name": "Fido", "tag": "Aloof"}
{"id": 10, "name": "Fluffy", "tag": "Affectionate"}
```

The final form is a variation on form 2. Here the `field_groups` value is a dictionary of name to fields list. i.e.:

```json
{ 
  "id": "...",
  "name": "...",
  "tag": "...",
  "field_groups": {
    "no_tag":   ["id", "name"],
    "with_tag": ["id", "name", "tag"]
  }
}
```


### <a name="CSV_Inputs"></a>Notes on CSV Inputs

#### Processing Large CSVs

There are [Field Specs](https://github.com/bbux-dev/dataspec/blob/main/docs/FIELDSPECS.md#CSV_Data) that support using
csv data to feed the data generation process. If the input CSV file is very large, not all features will be supported.
You will not be able to set sampling to true or use a field count > 1. The maximum number of iterations will be equal to
the size of the smallest number of lines for all the large input CSV file. The current size threshold is set to 250 MB.
So, if you are using two different csv files as inputs and one is 300 MB with 5 million entries and another is 500 MB
with 2 million entries, you will be limited to 2 million iterations before an exception will be raised and processing
will cease.

#### More efficient processing using csv_select

A common process is to select subsets of the columns from a csv file to use. The `csv_select` type makes this more
efficient than using the standard `csv` type. Below is an example that will Convert data from
the [Geonames](http://www.geonames.org/) [allCountries.zip](http://download.geonames.org/export/dump/allCountries.zip)
dataset by selecting a subset of the columns from the tab delimited file.

```yaml
---
placeholder:
  type: csv_select
  data:
    geonameid: 1
    name: 2
    latitude: 5
    longitude: 6
    country_code: 9
    population: 15
  config:
    datafile: allCountries.txt
    headers: no
    delimiter: "\t"
```

Running this spec would produce:

```shell
dataspec --spec csv-select.yaml \
         --iterations 5  \
         --datadir ./data \
         --format json \
         --log-level off -x
{"geonameid": "2986043", "name": "Pic de Font Blanca", "latitude": "42.64991", "longitude": "1.53335", "country_code": "AD", "population": "0"}
{"geonameid": "2994701", "name": "Roc M\u00e9l\u00e9", "latitude": "42.58765", "longitude": "1.74028", "country_code": "AD", "population": "0"}
{"geonameid": "3007683", "name": "Pic des Langounelles", "latitude": "42.61203", "longitude": "1.47364", "country_code": "AD", "population": "0"}
{"geonameid": "3017832", "name": "Pic de les Abelletes", "latitude": "42.52535", "longitude": "1.73343", "country_code": "AD", "population": "0"}
{"geonameid": "3017833", "name": "Estany de les Abelletes", "latitude": "42.52915", "longitude": "1.73362", "country_code": "AD", "population": "0"}
```

### <a name="Templating"></a>Templating

To populate a template file with the generated values for each iteration, pass the -t /path/to/template arg to the
dataspec command. We use the [Jinja2](https://pypi.org/project/Jinja2/) templating engine under the hood. The basic
format is to put the field names in {{ field name }} notation wherever they should be substituted. For example the
following is a template for bulk indexing data into Elasticsearch.

```json
{"index": {"_index": "test", "_id": "{{ id }}"}}
{"doc": {"name": "{{ name }}", "age": "{{ age }}", "gender": "{{ gender }}"}}
```

We could then create a spec to populate the id, name, age, and gender fields. Such as:

```json
{
  "id": {"type": "range", "data": [1, 10]},
  "gender": {"M": 0.48, "F": 0.52},
  "name": ["bob", "rob", "bobby", "bobo", "robert", "roberto", "bobby joe", "roby", "robi", "steve"],
  "age": {"type": "range", "data": [22, 44, 2]}
}
```

When we run the tool we get the data populated for the template:

```shell script
dataspec -s es-spec.json -t template.json -i 10 --log-level off -x
{ "index" : { "_index" : "test", "_id" : "1" } }
{ "doc" : {"name" : "bob", "age": "22", "gender": "F" } }
{ "index" : { "_index" : "test", "_id" : "2" } }
{ "doc" : {"name" : "rob", "age": "24", "gender": "F" } }
{ "index" : { "_index" : "test", "_id" : "3" } }
{ "doc" : {"name" : "bobby", "age": "26", "gender": "F" } }
{ "index" : { "_index" : "test", "_id" : "4" } }
...
```

#### <a name="Templating_Loops"></a>Loops in Templates

[Jinja2](https://jinja.palletsprojects.com/en/2.11.x/templates/#list-of-control-structures) supports looping. To provide
multiple values to use in a loop use the `count` parameter. For example modifying the example from the Jinja2
documentation to work with our tool:

```html
<h1>Members</h1>
<ul>
    {% for user in users %}
    <li>{{ user }}</li>
    {% endfor %}
</ul>
```

If we use a regular spec such as `{"users":["bob","bobby","rob"]}` the templating engine will not populate the template
correctly since during each iteration only a single name is returned as a string for the engine to process.

```html
<h1>Members</h1>
<ul>
    <li>b</li>
    <li>o</li>
    <li>b</li>
</ul>
```

The engine requires collections to iterate over. A small change to our spec will address this issue:

```json
{"users?count=2": ["bob", "bobby", "rob"]}
```

Now we get

```html
<h1>Members</h1>
<ul>
    <li>bob</li>
    <li>bobby</li>
</ul>
```

#### <a name="Dynamic_Loop_Counters"></a>Dynamic Loop Counters

Another mechanism to do loops in Jinja2 is by using the python builtin `range` function. For example if we wanted a
variable number of line items we could create a template like the following:

```html
<h1>Members</h1>
<ul>
    {% for i in range(num_users | int) %}
    <li>{{ users[i] }}</li>
    {% endfor %}
</ul>
```

Then we could update our spec to contain a `num_users` field:

```json
{
  "users?count=4?sample=true": ["bob", "bobby", "rob", "roberta", "steve"],
  "num_users": {
    "2": 0.5,
    "3": 0.3,
    "4": 0.2
  }
}
```

In the above spec the number of users created will be weighted so that half the time there are two, and the other half
there are three or four. NOTE: It is important to make sure that the `count` param is equal to the maximum number that
will be indexed. If it is less, then there will be empty line items whenever the num_users exceeds the count.

### <a name="Custom_Code_Loading"></a>Custom Code Loading and Schemas

There are a lot of types of data that are not generated with this tool. Instead of adding them all, there is a mechanism
to bring your own data suppliers. We make use of the handy [catalogue](https://pypi.org/project/catalogue/) package to
allow auto discovery of custom functions using decorators. Use the @dataspec.registry.types('\<type key\>') to register
a function that will create a Value Supplier for the supplied Field Spec. Below is an example of a custom class which
reverses the output of another supplier. Types that are amazing and useful should be nominated for core inclusion.
Please put up a PR if you create or use one that solves many of your data generation issues.

```python
import dataspec
from dataspec import ValueSupplierInterface


class ReverseStringSupplier(ValueSupplierInterface):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def next(self, iteration):
        # value from the wrapped supplier
        value = str(self.wrapped.next(iteration))
        # python way to reverse a string, hehe
        return value[::-1]


@dataspec.registry.types('reverse_string')
def configure_supplier(field_spec, loader):
    # load the supplier for the given ref
    key = field_spec.get('ref')
    wrapped = loader.get(key)
    # wrap this with our custom reverse string supplier
    return ReverseStringSupplier(wrapped)


@dataspec.registry.schemas('reverse_string')
def get_reverse_string_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "reverse_string.schema.json",
        "type": "object",
        "required": ["type", "ref"],
        "properties": {
            "type": {"type": "string", "pattern": "^reverse_string$"},
            "ref": {"type": "string"}
        }
    }
```

Now when we see a type of "reverse_string" like in the example below, we will use the given function to configure the
supplier for it. The function name for the decorated function is arbitrary, but the signature must match. The signature
for the Value Supplier is required to match the interface and have a single `next(iteration)` method that returns the
next value for the given iteration. You can also optionally register a schema for the type. The schema will be applied
to the spec if the `--strict` command line flag is specified, otherwise you will have to perform your own validation in
your code.

```
{
  "backwards": {
    "type": "reverse_string",
    "ref": "ANIMALS"
  },
  "refs": { 
    "ANIMALS": {
      "type": "values",
      "data": ["zebra", "hedgehog", "llama", "flamingo"]
    }
  }
}
```

To supply custom code to the tool use the -c or --code arguments. One or more module files can be imported.

```shell script
.dataspec -s reverse-spec.json -i 4 -c custom.py another.py -x --log-level off
arbez
gohegdeh
amall
ognimalf
```

# <a name="Programmatic"></a>Programmatic Usage

## <a name="BuildSpecs"></a>Building Specs
The `dataspec.builder` module contains tools that can be used to programmatically generate Data Specs. This may be
easier for some who are not as familiar with JSON or prefer to manage their structures in code.  The core object is
the `Builder`. You can add fields, refs, and field groups to this. Each of the core field types has a builder function
that will generate a Field Spec for it. See example below.

This is the email address example from above using the `builder` module.

```python
import dataspec

animal_names = ['zebra', 'hedgehog', 'llama', 'flamingo']
action_list = ['fling', 'jump', 'launch', 'dispatch']
domain_weights = {
    "gmail.com": 0.6,
    "yahoo.com": 0.3,
    "hotmail.com": 0.1
}
# for building the final spec
spec_builder = dataspec.spec_builder()
# for building the references, is it self also a Builder, but with no refs
refs = spec_builder.refs()
# info for each reference added
domains = refs.values('DOMAINS', data=domain_weights)
animals = refs.values('ANIMALS', data=animal_names)
actions = refs.values('ACTIONS', data=action_list, sample=True)
# combines ANIMALS and ACTIONS with an _
handles = refs.combine('HANDLE', refs=[animals, actions], join_with='_')

spec_builder.combine('email', refs=[handles, domains], join_with='@')

spec = spec_builder.build()
```

## <a name="Generator"></a>Generating Records

The `spec.generator` function will create a python generator that can be used to incrementally
generate the records from the DataSpec.

Example:

```python
import dataspec

name_list = ['bob', 'bobby', 'robert', 'bobo']
spec = dataspec.Builder().values('names', name_list).to_spec()

template = 'Name: {{ name }}'

generator = spec.generator(
    iterations=4,
    template=template)

single_record = next(generator)

all_records = list(generator)

# since we only specified 4 iterations our batch of 100 will contain 4 items
batch_of_100 = batch(generator)


def batch(generator, batch_size=100):
    values = []
    for i in range(batch_size):
        try:
            values.append(next(generator))
        except StopIteration:
            pass
    return values
```
