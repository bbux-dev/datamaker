Field Spec Definitions
========================
{% macro show_example(example, expand_json=True) -%}
{% if example.description is defined -%}
**{{ example.description | wordwrap(78) }}**

{% endif -%}
{% if example.json is defined -%}
{% if expand_json -%}
<details open>
{%- else %}
<details>
{%- endif %}
  <summary>JSON Spec</summary>

```json
{{ example.json }}
```

</details>
{%- endif %}
{% if example.yaml is defined -%}

<details>
  <summary>YAML Spec</summary>

```yaml
{{ example.yaml }}
```

</details>

{%- endif %}
{% if example.api is defined -%}

<details>
  <summary>API Example</summary>

```python
{{example.api}}
```

</details>

{%- endif %} 
{%- endmacro %} 
{% macro show_command_and_output(example, expand=False) -%}
{% if example.command is defined -%}
{% if expand -%}
<details open>
{%- else %}
<details>
{%- endif %}
  <summary>Example Command and Output</summary>

```shell
{{ example.command }}
{{ example.output }}
```

</details>

{%- endif %} 
{%- endmacro %} 
{% macro format_examples(def) -%}
{% if def.examples is defined -%} 
{% for example in def.examples -%} 
{{ example }}</br>
{%- endfor %}
{%- endif %}
{%- endmacro %} 
{% macro format_description(def) -%}
{% if def.description is defined -%}
{{ def.description |wordwrap(40)|replace('\n','</br>') }}
{%- endif %}
{%- endmacro %} 
{% macro show_params(schema, definitions) -%}

### Parameters

<details>

<summary>Parameter Details</summary>

param | type | description                                  | default | examples
------|------|----------------------------------------------|---------|---------

{%- for param, def in schema.properties.config.properties.items() if param not in ['prefix', 'suffix', 'quote', 'count']%} 
{%- if param in definitions %} 
{{ param }}|{{definitions[param].type}} |{{ format_description(definitions[param]) }}|{{definitions[param].default }} |{{ format_examples(definitions[param]) }}
{%- else %} 
{{ param }}|{{def.type}} |{{ format_description(def) }} |{{ def.default }} |{{ format_examples(def) }}
{%- endif %} 
{%- endfor %}
</details>

{%- endmacro %}
1. [Quick Reference](#Quick_Reference)
1. [Overview](#Overview)
1. [Field Spec Structure](#Field_Spec_Structure)
    1. [The Full Format](#The_full_format.)
    1. [Values Shorthand](#Values_Shorthand)
    1. [Inline Key Type Shorthand](#Inline_Key_Type_Shorthand)
    1. [Inline Key Config Shorthand](#Inline_Key_Config_Shorthad)
1. [Spec Configuration](#Spec_Configuration)
    1. [Common Configurations](#Common_Configurations)
    1. [Count Config Parameter](#CountsField)
1. [Field Spec Types](#Field_Spec_Types)
    1. [Values](#Values)
        1. [Constant Values](#Constant_Values)
        1. [List Values](#List_Values)
        1. [Weighted Values](#Weighted_Values)
        1. [Sample Mode](#Sample_Mode)
    1. [Combine](#Combine)
    1. [Combine List](#CombineList)
    1. [Date](#Date)
    1. [Range](#Range)
    1. [Random Range](#RandRange)
    1. [Uuid](#Uuid)
    1. [Character Class](#CharClass)
       1. [Built In Classes](#SupportedClasses)
    1. [Unicode Ranges](#UnicodeRange)
    1. [Geo](#Geo)
    1. [IP Addresses](#IP_Addresses)
        1. [Precise CIDR Addresses](#Precise_IP)
    1. [Weighted Ref](#Weighted_Ref)
    1. [Select List Subset](#Select_List_Subset)
        1. [Quoting Sublist Elements](#quoting_sublist)
    1. [CSV Data](#CSV_Data)
    1. [CSV Select](#CSV_Select)
    1. [nested](#Nested)

# <a name="Quick_Reference"></a>Quick Reference

type                         | description                            | config params
-----------------------------|----------------------------------------|------------------------------
[values](#Values)            | constant, list, or weighted dictionary |
[range](#Range)              | range of values                        |
[rand_range](#RandRange)     | random value in a range                |
[combine](#Combine)          | refs or fields                         | join_with
[combine-list](#CombineList) | list of lists of refs to combine       | join_with
[date](#Date)                | date strings                           | many see details below
[date.iso](#Date)            | date strings in ISO8601 format no microseconds| many see details below
[date.iso.us](#Date)         | date strings in ISO8601 format w/ microseconds| many see details below
[uuid](#Uuid)                | generates valid uuid                   |
[char_class](#CharClass)     | generates strings from character classes| many see details below
[unicode_range](#UnicodeRange)| generates strings from unicode ranges | many see details below
[geo.lat](#Geo)              | generates decimal latitude             | start_lat,end_lat,precision
[geo.long](#Geo)             | generates decimal longitude            | start_long,end_long,precision
[geo.pair](#Geo)             | generates long,lat pair                | join_with,start_lat,end_lat,</br>start_long,end_long,precision
[ip/ipv4](#IP_Addresses)     | generates ip v4 addresses              | base, cidr /8,/16,/24 only
[ip.precise](#IP_Addresses)  | generates ip v4 addresses              | cidr(required) i.e. 192.168.1.0/14
[weightedref](#Weighted_Ref) | produces values from refs in weighted fashion |
[select_list_subset](#Select_List_Subset) | selects subset of fields that are</br> combined to create the value for the field | join_with
[csv](#CSV_Data)             | Uses external csv file to supply data  | many see details below
[csv_select](#CSV_Select)    | Efficient way to select multiple csv columns | many see details below
[nested](#Nested)            | For nested fields                      |

# <a name="Overview"></a>Overview

Each field that should be generated needs a specification that describes the way
the values for it should be created. We refer to this as a Field Spec. The
simplest type of Field Spec is a values spec. The main format of a values spec
is a list of values to use. By default, these values are rotated through
incrementally. If the number of increments is larger than the number of values
in the list, the values start over from the beginning of the list. When
combining values from two values providers that are lists, they will be combined
in incrementing order. For example, the spec below will produce the values A1,
B2, C3 continuously.

{{ show_example(examples.overview_example_one) }}

{{ show_command_and_output(examples.overview_example_one, True) }}

If an additional number is added to TWO, we now get 12 distinct values:

{{ show_example(examples.overview_example_two) }}

{{ show_command_and_output(examples.overview_example_two, True) }}

If we want our values to be generated randomly from the provided lists, we set
the config param `sample` to true:

{{ show_example(examples.overview_example_three) }}

# <a name="Field_Spec_Structure"></a>Field Spec Structure

There are several ways to define a Field Spec. There is the full spec format,
and a variety of short hand notations.

## <a name="The_full_format."></a>The Full Format.

The only required element is type. Each Type Handler requires different pieces
of information. See the Field Type reference below for details on each type.
Below is the general structure.

```
{
  "type": "<the type>",
  "config": {
    "key1": "value1",
    ...</br>
    "keyN": "valueN"
  },
  "data": ["the data"],
  "ref": "REF_POINTER_IF_USED",
  "refs": ["USES", "MORE", "THAN", "ONE"],
  "fields": { "for": {}, "nested": {}, "types": {} }
}
```

## <a name="Values_Shorthand"></a>Values Shorthand

The values type is very common and so has a shorthand notation. Below is an
example full Field Spec for some values types fields and the same spec in
shorthand notation.

{{ show_example(examples.values_shorthand_one) }}

Shorthand Format:

{{ show_example(examples.values_shorthand_two) }}

The value after the field name is just the value of the data element from the
full Field Spec. Config params can be added to the key using the URL syntax
described below.

## <a name="Inline_Key_Type_Shorthand"></a>Inline Key Type Shorthand

Some specs lend themselves to being easily specified with few parameters. One
short hand way to do this is the use a colon in the key to specify the type
after the field name. For example `{"id:uuid":{}}`. This says the field `id` is
of type `uuid` and has no further configuration. If no type is specified, the
field is assumed to be a `values` type.

## <a name="Inline_Key_Config_Shorthad"></a>Inline Key Config Shorthand

It is also possible to specify configuration parameters in the key by using URL
style parameters. For example.

{{ show_example(examples.inline_key_example) }}

The `network` field is of type `ipv4` and the required `cidr` param is specified
in the key.

# <a name="Spec_Configuration"></a>Spec Configuration

There are two ways to configure a spec. One is by providing a `config` element
in the Field Spec and the other is by using a URL parameter format in the key.
For example, the following two fields will produce the same values:

{{ show_example(examples.config_example_one) }}

## <a name="Common_Configurations"></a>Common Configurations

There are some configuration values that can be applied to all or a subset of
types. These are listed below

key      | argument  |effect 
---------|-----------|-------
prefix   | string    |Prepends the value to all results 
suffix   | string    |Appends the value to all results  
quote    | string    |Wraps the resulting value on both sides with the</br> provided string 
cast     | i,int,f,float,s,str,string|For numeric types, will cast results</br> the provided type
join_with|string     |For types that produce multiple values, use this</br> string to join them   
as_list  |yes,true,on|For types that produce multiple values, return as</br> list without joining 

Example:

{{ show_example(examples.common_config_example_one) }}

## <a name="CountsField"></a>Count Config Parameter

Several types support a `count` config parameter. The value of the count
parameter can be any of the supported values specs formats. For example a
constant `3`, list `[2, 3, 7]`, or weighted
map `{"1": 0.5, "2": 0.3, "3": 0.2 }`. This will produce the number of values by
creating a value supplier for the count based on the supplied parameter. Most of
the time if the count is greater that 1, the values will be returned as an
array. Some types support joining the values by specifying the `join_with`
parameter. Some types will let you explicitly set the `as_list` parameter to
force the results to be returned as an array and not the default for the given
type.

### Count Distributions

Another way to specify a count is to use a count distribution. This is done with
the `count_dist` param.  The param takes a string argument which is the
distribution along with its required arguments in function call form with
parameters explicitly named.  See the table below.

distribution|required arguments|optional args|examples
------------|------------------|-------------|---
uniform     |start</br>end     |             |"uniform(start=10, end=30)"
</i>        |                  |             |"uniform(start=1, end=3)"
guass       |mean</br>stddev   |min</br>max  |"gauss(mean=2, stddev=1)"
guassian    |                  |             |"guassian(mean=7, stddev=1, min=4)"
normal      |                  |             |"normal(mean=25, stddev=10, max=40)"

`normal`, `guassian`, and `gauss` are all aliases for a
[Normal Distribution](https://en.wikipedia.org/wiki/Normal_distribution).

Example:

{{ show_example(examples.count_dist_example_one) }}

# <a name="Field_Spec_Types"></a>Field Spec Types

These are the built-in types

## <a name="Values"></a>Values

There are three types of values specs: Constants, List, and Weighted. Values
specs have a shorthand notation where the value of the data element replaces the
full spec. See examples below.

### <a name="Constant_Values"></a>Constant Values

A Constant Value is just a single value that is used in every iteration

{{ show_example(examples.constants_example_one) }}

### <a name="List_Values"></a>List Values

List values are rotated through in order. If the number of iterations is larger
than the size of the list, we start over from the beginning of the list. Use
the `sample` config param to specify that the values should be selected at
random from the provided list.

{{ show_example(examples.list_values_example_one) }}

### <a name="Weighted_Values"></a>Weighted Values

Weighted values are generated according to their weights.

{{ show_example(examples.weighted_values_example_one) }}

The example above will generate 200 40% of the time and 400 and 403 5%. The
higher the number of iterations the more likely the values will match their
specified weights.

### <a name="Sample_Mode"></a>Sample Mode

To increase the randomness of the data being generated, you can configure a
FieldSpec that contains a list of values to be sampled instead of iterated
through incrementally. Normally the spec below would create the repeating
sequence: `A1 B2 C3`, but since both fields `ONE` and `TWO` are in sample mode,
we will get all nine combinations of values after a significant number of
iterations. This would also be true if only one was set to sample mode. To turn
sample mode on either use a URL param or config entry with one of `on`,  `yes`,
or `true`. NOTE: Sample mode is only valid with entries that are lists.

{{ show_example(examples.sample_mode_example_one) }}

#### Sample All

If running from the command line, you cas specify the `--sample-lists` flag to
make all list backed data to have sampling turned on by default. If using the
python API, do `dataspec.types.set_default('sample_mode', True)`

## <a name="Combine"></a>Combine

A combine Field Spec is used to concatenate or append two or more fields or
reference to one another.

The combine Field Spec structure is:

```
{
  "<field name>": {
    "type": "combine",
    "fields": ["valid field name1", "valid field name2"],
    OR
    "refs": ["valid ref1", "valid ref2"],
    "config": {
      "join_with": "<optional string to use to join fields or refs, default is none>"
    }
  }
}
```

Example below uses the first and last refs to create a full name field.

{{ show_example(examples.combine_spec_example_one) }}

## <a name="CombineList"></a>Combine List

A combine-list Field Spec is used to specify a list of lists of refs to combine.
This is useful if there are a lot of variations on the values that should be
combined. This allows all the variations to be specified in one place. Note:
This approach requires the same join_with param for each set of refs.

The combine Field Spec structure is:

```
{
  "<field name>": {
    "type": "combine-list",
    "refs": [
      ["valid ref1", "valid ref2"],
      ["valid ref1", "valid ref2", "valid_ref3", ...], ...
      ["another_ref", "one_more_ref"]
    ],
    "config": {"join_with": "<optional string to use to join fields or refs, default is none>"}
  }
}
```

This is a slight modification to the above combine Example.

{{ show_example(examples.combine_list_spec_example_one) }}

## <a name="Date"></a>Date

A Date Field Spec is used to generate date strings. The default format is
day-month-year i.e. Christmas 2050 would be: 25-12-2050. There is also
a `date.iso` type that generates ISO8601 formatted date strings without
microseconds and a `date.iso.us` for one that generates them with microseconds.
We use the
[format specification](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
from the datetime module.

### Uniformly Sampled Dates

The default strategy is to create random dates within a 30 day range, where the
start date is today. You can use the `start` parameter to set a specific start
date for the dates. You can also explicitly specify an `end` date. The `start`
and `end` parameters should conform to the specified date format, or the default
if none is provided. The `offset` parameter can be used to shift the dates by a
specified number of days. A positive
`offset` will shift the start date back. A negative `offset` will shift the date
forward. The `duration_days`
parameter can be used to specify the number of days that should be covered in
the date range, this parameter can take the place of the `end` parameter to make
specifying the number of days the dates should cover. This parameter is usually
specified as an integer constant.

```
       start                              end (default start + 30 days)
          |--------------------------------|
  |+offset|                           start+duration_days
  |--------------------------------|
          |-offset|
                  |--------------------------------|    
```

### Dates Distributed around a Center Point

An alternative strategy is to specify a `center_date` parameter with an
optional `stddev_days`. This will create a normal or gaussian distribution of
dates around the center point.

```  
                   |
                   |
                |  |  |
             |  |  |  |  |
          |  |  |  |  |  |  |  
 |  |  |  |  |  |  |  |  |  |  |  |  |
|-------------------------------------|
|         | stddev | stddev |         |
                center
```

There are a lot of configuration parameters for the date type. Each are
described below.

{{ show_params(schemas.date, definitions) }}

The date Field Spec structure is:

```
{
  "<field name>": {
    "type": "date",
    OR,
    "type": "date.iso",
    OR,
    "type": "date.iso.us",
    "config": {"...": "..."}
  }
}
```

### Examples

To help with the number of variations of date formats, there are a number of
examples below. They all assume today is 15 Jan 2050, so the default date
formatted for today would be 15-01-2050. Click More Examples to see all
examples.

#### Uniform Dates Examples

{{show_example(examples.uniform_date_example_exhaustive)}}

{{show_command_and_output(examples.uniform_date_example_exhaustive, True)}}

<details>
<summary>More Examples</summary>

{{show_example(examples.uniform_date_example_one, False)}}

{{show_command_and_output(examples.uniform_date_example_one, True)}}

{{show_example(examples.uniform_date_example_two, False)}}

{{show_command_and_output(examples.uniform_date_example_two, True)}}

{{show_example(examples.uniform_date_example_three, False)}}

{{show_command_and_output(examples.uniform_date_example_three, True)}}

{{show_example(examples.uniform_date_example_four, False)}}

{{show_command_and_output(examples.uniform_date_example_four, True)}}

{{show_example(examples.uniform_date_example_five, False)}}

{{show_command_and_output(examples.uniform_date_example_five, True)}}

{{show_example(examples.uniform_date_example_six, False)}}

{{show_command_and_output(examples.uniform_date_example_six, True)}}

{{show_example(examples.uniform_date_example_seven, False)}}

{{show_command_and_output(examples.uniform_date_example_seven, True)}}

{{show_example(examples.uniform_date_example_eight, False)}}

{{show_command_and_output(examples.uniform_date_example_eight, True)}}


</details>

#### Centered Dates Examples

{{show_example(examples.centered_date_example_exhaustive)}}

{{show_command_and_output(examples.centered_date_example_exhaustive, True)}}

<details>
<summary>More Examples</summary>

{{show_example(examples.centered_date_example_one, False)}}

{{show_command_and_output(examples.centered_date_example_one, True)}}

{{show_example(examples.centered_date_example_two, False)}}

{{show_command_and_output(examples.centered_date_example_two, True)}}

</details>

### ISO8601 formatted dates

The type `date.iso` will produce a ISO8601 formatted date in the bounds
configured without milliseconds. Use the `date.iso.us` type to generate them
with microseconds.

## <a name="Range"></a>Range

A `range` spec is used to generate a range of values. The ranges are inclusive
for start and end. The start, stop, and step can be integers or floating-point
numbers.

{{ show_params(schemas.range, definitions) }}

The range Field Spec structure is:

```
{
  "<field name>": {
    "type": "range",
    "data": [<start>, <end>, <step> (optional)],
    or
    "data": [
      [<start>, <end>, <step> (optional)],
      [<start>, <end>, <step> (optional)],
      ...
      [<start>, <end>, <step> (optional)],
    ],
  }
}
```

Example: Range 0 to 10 with a step of 0.5

{{ show_example(examples.range_spec_example_one) }}

Example: Multiple Ranges One Field

{{ show_example(examples.range_spec_example_two) }}

This spec produces integer values for three different ranges each with different
step sizes.

## <a name="RandRange"></a>Random Range

A `rand_range` spec is used to generate a number with in a range. Use the `cast`
param to explicitly cast the value to one of int, float, or string. The default
is to return value as a string.

The range Field Spec structure is:

```
{
  "<field name>": {
    "type": "rand_range",
    "data": [<upper>],
    or
    "data": [<lower>, <upper>],
    or
    "data": [<lower>, <upper>, <precision> (optional)]
  }
}
```

If a single element is provided in the `data` array, it will be used as the
upper bound and 0 will be the lower.

### Config Params

|param    |description|
|---------|-----------|
|precision|How many digits after decimal point to include|
|cast     |Type to cast result to, default is to return as string|

Example:

In this example we have two different population fields. The first generates an
integer uniformly between 100 and 1000. The second generates a float between
200.2 and 1222.7 with two values after the decimal place.

{{ show_example(examples.rand_range_spec_example_one) }}

{{show_command_and_output(examples.rand_range_spec_example_one, True)}}

## <a name="Uuid"></a>Uuid

A standard uuid.

The uuid Field Spec structure is:

```
{
  "<field name>": {
    "type": "uuid"
  }
}
```

Example Spec

{{ show_example(examples.uuid_spec_example_one) }}

## <a name="CharClass"></a>Character Classes

A `char_class` type is used to create strings that are made up of characters
from specific character classes. The strings can be of fixed or variable length.
There are several built in character classes. You can also provide your own set
of characters to sample from. Below is the list of supported character classes:

### <a name="SupportedClasses"></a>Built In Classes

|class      |description|
|-----------|--------------------------------------------|
|ascii      |All valid ascii characters including control|
|lower      |ascii lowercase|
|upper      |ascii uppercase|
|digits     |Numbers 0 through 9|
|letters    |lowercase and uppercase|
|word       |letters + digits + '_'|
|printable  |All printable ascii chars including whitespace|
|visible    |All printable ascii chars excluding whitespace|
|punctuation|local specific punctuation|
|special    |local specific punctuation|
|hex        |Hexadecimal digits including upper and lower case a-f|
|hex-lower  |Hexadecimal digits only including lower case a-f|
|hex-upper  |Hexadecimal digits only including upper case A-F|

Helpful Links:

* https://en.wikipedia.org/wiki/ASCII#Character_groups
* https://www.cs.cmu.edu/~pattis/15-1XX/common/handouts/ascii.html
* https://docs.python.org/3/library/string.html

{{ show_params(schemas.char_class, definitions) }}

### Usage

A `char_class` Field Spec takes the form

```
{
  "<field>": {
    # type definition
    "type": "char_class":
    or
    "type": "cc-<char_class_name>",
    # data definition
    "data": <char_class_name>,
    or
    "data": <string with custom set of characters to sample from>
    or
    "data": [<char_class_name1>, <char_class_name2>, ..., <custom characters>]
    # configuration
    "config":{
      # General Parameters
      "exclude": <string of characters to exclude from output>,
      # String Size Based Config Parameters
      "min": <min number of characters in string>,
      "max": <max number of characters in string>,
      or
      "count": <exact number of characters in string>
      or
      "mean": <mean number of characters in string>
      "stddev": <standard deviation from mean for number of characters in string>
      "min": <optional min>
      "max": <optional max>
    }    
  }
}
```

### Shorthand Notation for Single Character Classes

If a single character class is needed, the type can be specified with a `cc-`
prefix: `cc-<char_class_name>` e.g. `"type": "cc-visible"` would only use
characters from the `visible` class. If this format is used, the `data` element
is ignored and only characters from the single character class are sampled from.

{{ show_example(examples.char_class_spec_example_one) }}

### Examples

Below is an example selecting several character classes along with a set of
custom ones to use to generate passwords. The generated passwords are between 10
and 18 characters in length with a mean size of 14 characters and a standard
deviation of 2.

{{ show_example(examples.char_class_spec_example_two) }}

{{ show_command_and_output(examples.char_class_spec_example_two) }}

The `stddev` config parameters is not required, but without it the sizes will
tend to stack on the edges of the allowed size range.

<details>
  <summary>Detailed Example</summary>

```shell
# no stddev specified
for p in $(dataspec -l off -x --inline "password:cc-word?mean=5&min=1&max=9: {}" -i 1000);
do
  echo $p | tr -d '\n' | wc -m
done | sort | uniq -c | sort -n -k2,2
# count num chars
    163 1
     59 2
     91 3
     92 4
    100 5
    110 6
     94 7
     71 8
    220 9
# with stddev of 3 specified
for p in $(dataspec -l off -x --inline "password:cc-word?mean=5&stddev=3&min=1&max=9: {}" -i 1000);
do
  echo $p | tr -d '\n' | wc -m
done | sort | uniq -c | sort -n -k2,2
# count num chars
     98 1
     72 2
     96 3
    126 4
    133 5
    128 6
    113 7
     90 8
    144 9
```

</details>

## <a name="UnicodeRange"></a>Unicode Ranges

The `unicode_range` type is similar to the `char_class` type, but it is used to
generate characters from valid unicode ranges.
See [UnicodeRanges](https://www.ling.upenn.edu/courses/Spring_2003/ling538/UnicodeRanges.html)
for a list of the different valid ranges. One or more ranges can be specified in
the `data` element by providing a list or list of lists with two elements each
specifying the start and end hex code points. If we wanted to generate Japanese
Hiragana (Code points 0x3040 to 0x30FF) characters as one of our fields we could
use the following spec:

{{ show_example(examples.unicode_range_example_one) }}

{{ show_command_and_output(examples.unicode_range_example_one) }}

### Usage

A `unicode_range` Field Spec takes the form

```
{
  "<field>": {
    # type definition
    "type": "unicode_range":
    # data definition
    "data": [<start_code_point_in_hex>, <end_code_point_in_hex>],
    or
    "data": [
        [<start_code_point_in_hex>, <end_code_point_in_hex>],
        [<start_code_point_in_hex>, <end_code_point_in_hex>],
        ...
        [<start_code_point_in_hex>, <end_code_point_in_hex>],
    ],
    # configuration
    "config":{
      # String Size Based Config Parameters
      "min": <min number of characters in string>,
      "max": <max number of characters in string>,
      or
      "count": <exact number of characters in string>
      or
      "mean": <mean number of characters in string>
      "stddev": <standard deviation from mean for number of characters in string>
      "min": <optional min>
      "max": <optional max>
    }    
  }
}
```

## <a name="Geo"></a>Geo Related Types

There are three main geo types: `geo.lat`, `geo.long`, and `geo.pair`. The
defaults will create decimal string values in the valid ranges: -90 to 90 for
latitude and -180 to 180 for longitude. You can bound the ranges in several
ways. The first is with the `start_lat`, `end_lat`, `start_long`, `end_long`
config params. These will set the individual bounds for each of the segments.
You can use one or more of them. The other mechanism is by defining a `bbox`
array which consists of the lower left geo point and the upper right one.
See: [Bounding_Box](https://wiki.openstreetmap.org/wiki/Bounding_Box#)

Config Params:

|type    |param     |description
|--------|----------|---------------------------------------------
|all     |precision |number of decimal places for lat or long, default is 4
|        |bbox      |array of \[min Longitude, min Latitude, max Longitude,</br> max Latitude\]
|geo.lat |start_lat |lower bound for latitude
|        |end_lat   |upper bound for latitude
|geo.long|start_long|lower bound for longitude
|        |end_long  |upper bound for longitude
|geo.pair|join_with |delimiter to join long and lat with, default is comma
|        |as_list   |One of yes, true, or on if the pair should be returned</br> as a list instead of as a joined string|
|        |lat_first |if latitude should be first in the generated pair,</br> default is longitude first|
|        |start_lat |lower bound for latitude
|        |end_lat   |upper bound for latitude
|        |start_long|lower bound for longitude
|        |end_long  |upper bound for longitude

Examples:

Generates a `longitude,latitude` pair with in the bounding box defining Egypt
with 3 decimal points of precision.

{{ show_example(examples.geo_point_spec_example_one) }}

## <a name="IP_Addresses"></a>IP Addresses

Ip addresses can be generated
using [CIDR notation](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
or by specifying a base. For example, if you wanted to generate ips in the
10.0.0.0 to 10.0.0.255 range, you could either specify a `cidr` param of
10.0.0.0/24 or a `base` param of 10.0.0.

{{ show_params(schemas.ip, definitions) }}

### Usage

The ipv4 Field Spec structure is:

```
{
  "<field name>": {
    "type": "ipv4",
    "config": {
      "cidr": "<cidr value /8 /16 /24 only>",
      OR
      "base": "<beginning of ip i.e. 10.0>"
    }
  }
}
```

Example Spec:

{{ show_example(examples.ip_spec_example_one) }}

### <a name="Precise_IP"></a> Precise CIDR Addresses

The default ip type only supports cidr masks of /8 /16 and /24. If you want more
precise ip ranges you need to use the `ip.precise` type. This type requires a
cidr as the single config param. For some cidr values the number of generated
ips becomes large, and the underlying module used becomes preventatively slow.
Even with a /16 address it can take multiple seconds to generate only 1000 ips.
Anything smaller than that may not be worth it. The default mode
for `ip.precise` is to increment the ip addresses. Set config param `sample` to
on of `true`, `on`, or `yes` to enable random ip addresses selected from the
generated ranges.

#### Examples

Ips in the 10.n.n.n range, extremely slow, this is around 16 Million unique ip
addresses

{{ show_example(examples.ip_precise_example_one) }}

Ips in the 192.168.0.0 to 192.171.255.255 range, relatively slow, creates around
250K addresses

{{ show_example(examples.ip_precise_example_two) }}

Ips in the 2.22.220.0 to 2.22.223.255 range, speed is tolerable

{{ show_example(examples.ip_precise_example_three) }}

## <a name="Weighted_Ref"></a>Weighted Ref

A weighted ref spec is used to select the values from a set of refs in a
weighted fashion.

The weightedref Field Spec structure is:

```
{
  "<field name>": {
    "type": "weightedref",
    "data": {"valid_ref_1": 0.N, "valid_ref_2": 0.N, ...}
  }
}
```

For example if we want to generate a set of HTTP response codes, but we want
mostly success related codes we could use the follow spec.

{{ show_example(examples.weighted_ref_example_one) }}

## <a name="Select_List_Subset"></a>Select List Subset

A select list subset spec is used to select multiple values from a list to use
as the value for a field.

The select_list_subset Field Spec structure is:

```
{
  "<field name>": {
    "type": "select_list_subset",
    "config": {
      "mean": N,
      "stddev": N,
      "min": N,
      "max": N,
      or
      "count": N,
      "join_with": "<delimiter to join with>"
    },
    "data": ["data", "to", "select", "from"],
    OR
    "ref": "REF_WITH_DATA_AS_LIST"
  }
}
```

The join_with config option is used to specify how the selected values should be
combined. The mean and stddev config options tell how many items should be
chosen. For example a mean of 2 and stddev of 1, would mostly choose 2 items
then sometimes 1 or 3 or more. There are two ways to produce an exact number of
elements.  The first is to use the `count` param by itself.  The second is to set
the stddev to 0. You can also set a min and max. Example:

{{ show_example(examples.select_list_example_one) }}

{{ show_command_and_output(examples.select_list_example_one) }}

### <a name='quoting_sublist'></a> Quoting Sublist Elements

The default `quote` parameter will only quote the whole combined list of
elements. To quote each individual element of the sublist you need to use a
special form of `join_with` along with the `quote` param. For example if we
wanted all of our ingredients surrounded with double quotes. We would update our
spec this way.

{{ show_example(examples.select_list_example_two) }}

{{ show_command_and_output(examples.select_list_example_two) }}

## <a name='CSV_Data'></a> CSV Data

If you have an existing large set of data in a tabular format that you want to
use, it would be burdensome to copy and paste the data into a spec. To make use
of data already in a tabular format you can use a `csv` Field Spec. These specs
allow you to identify a column from a tabular data file to use to provide the
values for a field. Another advantage of using a csv spec is that it is easy to
have fields that are correlated be generated together. All rows will be selected
incrementally, unless any of the fields are configured to use `sample` mode. You
can use `sample` mode on individual columns, or you can use it across all
columns by creating a `configref` spec. See [csv_select](#csv_select) for an
efficient way to select multiple columns from a csv file.

The `csv` Field Spec structure is:

```
{
  "<field name>": {
    "type": "csv",
    "config": {
      "datafile": "filename in datedir",
      "headers": "yes, on, true for affirmative",
      "column": "1 based column number or field name if headers are present",
      "delimiter": "how values are separated, default is comma",
      "quotechar": "how values are quoted, default is double quote",
      "sample": "If the values should be selected at random, default is false",
      "count": "Number of values in column to use for value"
    }
  }
}
```

#### Params

|param      |required?|default |description|
|-----------|---------|--------|-----------|
|datafile   |no       |data.csv|filename in datandir to use|
|headers    |no       |false   |yes, on, true for affirmative|
|column     |no       |1       |1 based column number or field name if headers</br> are present|
|delimiter  |no       |,       |how values are separated|
|quotechar  |no       |"       |how values are quoted, default is double quote|
|sample     |no       |False   |If the values should be selected at random|
|count      |no       |1       |Number of values in column to use for value|

#### Examples

##### Single Field

The simplest example is a file with a single field that contains the values to
generate for a field. For example if we have a known list of cities, we can put
this in a file and reference it from our spec. The advantage of this approach is
that it is easy to add new data points and to use small sets of data for testing
by creating directories that have smaller input files.

{{ show_example(examples.csv_spec_example_one) }}

```shell
dataspec --spec cities.json --datadir ./data -i 5
Tokyo
Los Angeles
New York
Chicage
London
```

Note that if your data might have commas in it (the default delimiter), you
should specify a delimiter that will not be found in your data.

##### Multiple Fields Non Comma Separated

In this example we have a tab delimited file with multiple columns that we want
to use.

```
status	status_description	status_type
100	Continue	Informational
101	Switching Protocols	Informational
200	OK	Successful
201	Created	Successful
202	Accepted	Successful
...
```

Our Data Spec looks like:

{{ show_example(examples.csv_spec_example_two) }}

The `configref` exist so that we don't have to repeat ourselves for common
configurations across multiple fields. If we use the following template {% raw
%}`{{ status }},{{ description }},{{ status_type }}`{% endraw %} and run this
spec we will get output similar to:

```shell
dataspec --spec tabs.yaml --datadir ./data -t template.jinja -i 5
100,Continue,Informational
101,Switching Protocols,Informational
200,OK,Successful
201,Created,Successful
202,Accepted,Successful
```

## <a name="CSV_Select"></a>CSV Select

A common process is to select subsets of the columns from a csv file to use.
The `csv_select` type makes this more efficient than using the standard `csv`
type. Below is an example that will Convert data from the
[Geonames](http://www.geonames.org/)
[allCountries.zip](http://download.geonames.org/export/dump/allCountries.zip)
dataset by selecting a subset of the columns from the tab delimited file. The
key in the data element is the new name for the field. The value can either be
the 1 indexed column number, or the name of the field if the data has `headers`.
Our example doesn't have headers, so we are using the 1 based indexes.

{{ show_example(examples.csv_select_example_one) }}

## <a name="nested"></a>Nested Fields

Nested types are used to create fields that contain subfields. Nested types can
also contain nested fields to allow multiple levels of nesting. Use the `nested`
type to generate a field that contains subfields. The subfields are defined in
the `fields` element of the nested spec. The `fields` element will be treated
like a top level dataspec and has access to the `refs` and other elements of the
root.

The `nested` Field Spec structure is:

```
{
  "<field name>": {
    "type": "nested",
    "config": {
      "count": "Values Spec for Counts, default is 1"
    },
    "fields": {
      "<sub field one>": { spec definition here },
      "<sub field two>": { spec definition here },
      ...
    }
  }
}
```

### Example:

Below is an example of the data we wish to generate:

```json
{
  "id": "abc123efg456",
  "user": {
    "user_id": "bad135dad987",
    "geo": {
      "place_id": 12345,
      "coordinates": [
        118.2,
        34.0
      ]
    }
  }
}
```

The `user` is a nested object, which has a subfield `geo`, which is also a
nested object. The `id` and `user_id` fields are uuids. The coordinates field is
a list of longitude followed by latitude. Below are the specs that will generate
data that matches this schema.

{{ show_example(examples.nested_example_one) }}

{{ show_command_and_output(examples.nested_example_one) }}