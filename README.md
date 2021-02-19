Data Spec Repository
========================

1. [Overview](#Overview)
1. [Build](#Build)
1. [Examples](#Examples)
1. [Core Concepts](#Core_Concepts)
    1. [Data Spec](#Data_Spec)
        1. [YAML Format](#YAML_Format)
    1. [Field Specs](#Field_Specs)
    1. [Templating](#Templating)
        1. [Loops in Templates](#Templating_Loops)
        1. [Dynamic Loop Counters](#Dynamic_Loop_Counters)
    1. [Custom Code Loading](#Custom_Code_Loading)

## <a name="Overview"></a>Overview

This is a tool for making data according to specifications. The goal is to separate the structure of the data from the
values that populate it. We do this by defining two core concepts the Data Spec and the Field Spec. A Data Spec is used
to define all of the fields that should be generated for a record. The Data Spec does not care about the structure that
the data will populate. A single Data Spec could be used to generate JSON, XML, or a csv file. Each field in the Data
Spec has its own Field Spec that defines how the values for it should be created. There are a variety of core field
types that are used to generate the data for each field. Where the built-in types are not sufficient, there is an easy
way to create custom types and handlers for them. The tool supports templating using
the [Jinja2](https://pypi.org/project/Jinja2/) templating engine format.

## <a name="Build"></a>Build

To Install:

```shell script
pip install git+https://github.com/bbux-dev/dataspec.git
```

The executable will be located in `dataspec` and should now be on your path

## <a name="Examples"></a>Examples

See [examples](docs/EXAMPLES.md) to dive into detailed examples and practical use cases.

## <a name="Core_Concepts"></a>Core Concepts

### <a name="Data_Spec"></a>Data Spec

A Data Spec is a Dictionary where the keys are the names of the fields to generate and each value is
a [Field Spec](docs/FIELDSPECS.md)
that describes how the values for that field are to be generated. There is one reserved key in the root of the Data
Spec: refs. The refs is a special section of the Data Spec where Field Specs are defined but not tied to any specific
field. These refs can then be used or referenced by other Specs. An example would be a combine Spec which points to two
references that should be joined. Below is an example Data Spec for creating email addresses.

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

Dats specs can also be created using YAML. Below is the same spec above in YAML.

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

See [field specs](docs/FIELDSPECS.md) for details.

### <a name="CSV_Inputs"></a>CSV Input

There are [Field Specs](https://github.com/bbux-dev/dataspec/blob/main/docs/FIELDSPECS.md#CSV_Data) that support using
csv data to feed the data generation process. A common process is to select subsets of the columns from a csv file to
use. The `csv_select` type makes this more efficient than using the standard `csv` type. Below is an example that will
Convert data from
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
         --loglevel off
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
dataspec -s ~/scratch/es-spec.json -t ~/scratch/template.json -i 10
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
  "users?count=4": ["bob", "bobby", "rob", "roberta", "steve"],
  "num_users": {
    "2": 0.5,
    "3": 0.3,
    "4": 0.2
  }
}
```

In this spec the number of users created will be weighted so that half the time there are two, and the other half there
are three or four. NOTE: It is important to make sure that the `count` param is equal to the maximum number that will be
indexed. If it is less, then there will be empty line items whenever the num_users exceeds the count.

### <a name="Custom_Code_Loading"></a>Custom Code Loading

There are a lot of types of data that are not generated with this tool. Instead of adding them all, there is a mechanism
to bring your own data suppliers. We make use of the handy [catalogue](https://pypi.org/project/catalogue/) library to
allow auto discovery of custom functions using decorators. Use the @dataspec.registry.types('\<type key\>') to register
a function that will create a Value Supplier for the supplied Field Spec. Below is an example of a custom class which
reverses the output of another supplier. Types that are amazing and useful should be nominated for core inclusion.
Please put up a PR if you create or use one that solves many of your data generation issues.

```python
import dataspec


class ReverseStringSupplier:
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
    spec = loader.refs.get(key)
    wrapped = loader.get_from_spec(spec)
    # wrap this with our custom reverse string supplier
    return ReverseStringSupplier(wrapped)
```

Now when we see a type of "reverse_string" like in the example below, we will use the given function to configure the
supplier for it. The function name for the decorated function is arbitrary, but the signature must match. The signature
for the Value Supplier is required to match the interface and have a single `next(iteration)` method that returns the
next value for the given iteration.

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
.dataspec -s reverse-spec.json -i 4 -c custom.py another.py
arbez
gohegdeh
amall
ognimalf
```
