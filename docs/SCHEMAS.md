Built in Field Spec Type Schemas
================================


1. [Definitions](#definitions)
1. [char_class](#char_class)
1. [combine-list](#combine-list)
1. [combine](#combine)
1. [Date types (data, date.iso, date.iso.us)](#date)
1. [geo.lat](#geo.lat)
1. [geo.long](#geo.long)
1. [geo.pair](#geo.pair)
1. [IP types (ip, ipv4)](#ip)
1. [Range types (range, rand_range)](#range)
1. [unicode_range](#unicode_range)
1. [uuid](#uuid)
1. [values](#values)


# <a name="definitions"></a>Definitions

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/definitions.json",
  "definitions": {
    "prefix": {"type": "string"},
    "suffix": {"type": "string"},
    "quote": {"type": "string"},
    "join_with": {"type": "string"},
    "affirmative_check": {
      "description": "Either true, false, 'on', 'off', 'yes', 'no', 'true', 'false', case insensitive",
      "oneOf": [
        {"type": "boolean"},
        {"type": "string", "pattern": "[t|T][r|R][u|U][e|E]|[f|F][a|A][l|L][s|S][e|E]|[y|Y][e|E][s|S]|[n|N][o|O]|[o|O][n|N]|[o|O][f|F][f|F]"}
      ]
    },
    "as_list": {"$ref": "#/definitions/affirmative_check"},
    "cast": {"type": "string", "enum": ["i", "int", "f", "float", "s", "string", "string", "h", "hex"]},
    "count": {
      "oneOf": [
        {"type": "integer"},
        {
          "type": "array",
          "minItems": 1,
          "uniqueItems": false,
          "items": {"type": "integer"}
        },
        {
          "type": "object",
          "minProperties": 1,
          "propertyNames": {
            "pattern": "[0-9]+"
          },
          "additionalProperties": {"type": "number"}
        }
      ]
    },
    "min": {"type": "number"},
    "max": {"type": "number"},
    "mean": {"type": "number"},
    "stddev": {"type": "number"},
    "precision": {"type": "integer"},
    "bbox": {
      "description": "Bounding box for geo related points, describes lower left and upper right coordinates with longitude first",
      "type": "array",
      "minItems": 4,
      "maxItems": 4,
      "items":[
        {"type": "number", "minimum": -180, "maximum": 180},
        {"type": "number", "minimum": -90, "maximum": 90},
        {"type": "number", "minimum": -180, "maximum": 180},
        {"type": "number", "minimum": -90, "maximum": 90}
      ]
    }
  }
}
```
</details>

# <a name="char_class"></a>char_class

Types covered by schema: `char_class`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/char_class.schema.json",
  "type": "object",
  "required": ["type", "data"],
  "properties": {
    "type": {"type": "string", "pattern": "^char_class$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "min": {"$ref": "#/definitions/min"},
        "max": {"$ref": "#/definitions/max"},
        "mean": {"$ref": "#/definitions/mean"},
        "stddev": {"$ref": "#/definitions/stddev"}
      },
      "not": {
        "description": "count should not be present if min max or mean are present",
        "anyOf": [
          {"required": ["count", "min"]},
          {"required": ["count", "max"]},
          {"required": ["count", "mean"]}
        ]
      }
    },
    "data": {
      "oneOf": [
        {
          "description": "arbitrary user defined characters or one of predefined character classes: ascii, lower, upper, digits, letters, word, printable, visible, punctuation, special, hex, hex-lower, hex-upper",
          "type": "string"
        },
        {
          "description": "array of one or more of the above",
          "type": "array",
          "minItems": 1,
          "items": {"type": "string"}
        }
      ]
    }
  }
}
```
</details>

# <a name="combine-list"></a>combine-list

Types covered by schema: `combine-list`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/combine.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^combine-list$"},
    "config": {
      "type": "object",
      "properties": {
        "join_with": {"$ref": "#/definitions/join_with"},
        "as_list": {"$ref": "#/definitions/as_list"}
      }
    },
    "refs": {
      "type": "array",
      "uniqueItems": false,
      "items": {
        "type": "array",
        "minItems": 2,
        "items": {
          "type": "string"
        }
      }
    },
    "fields": {
      "type": "array",
      "uniqueItems": true,
      "items": {
        "type": "array",
        "minItems": 2,
        "items": {
          "type": "string"
        }
      }
    }
  },
  "oneOf": [
    {"required": ["refs"]},
    {"required": ["fields"]}
  ]
}
```
</details>

# <a name="combine"></a>combine

Types covered by schema: `combine`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/combine.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^combine$"},
    "config": {
      "type": "object",
      "properties": {
        "join_with": {"$ref": "#/definitions/join_with"},
        "as_list": {"$ref": "#/definitions/as_list"}
      }
    },
    "refs": {
      "type": "array",
      "minItems": 2,
      "uniqueItems": true,
      "items": {
        "type": "string"
      }
    },
    "fields": {
      "type": "array",
      "minItems": 2,
      "uniqueItems": true,
      "items": {
        "type": "string"
      }
    }
  },
  "oneOf": [
    {"required": ["refs"]},
    {"required": ["fields"]}
  ]
}
```
</details>

# <a name="date"></a>Date types (data, date.iso, date.iso.us)

Types covered by schema: `date, date.iso, date.iso.us`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/date.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^date(\\.iso|\\.iso\\.us)?$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "format": {
          "description": "Valid date format string",
          "type": "string"
        },
        "duration_days": {
          "oneOf": [
            {"type": "integer"},
            {
              "type": "array",
              "minItems": 2,
              "maxItems": 2,
              "items": { "type": "integer" }
            }
          ]
        },
        "start": {"type": "string"},
        "offset": {"type": "integer"}
      }
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="geo.lat"></a>geo.lat

Types covered by schema: `geo.lat`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/geo.lat.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {"type": "string", "pattern": "^geo\\.lat$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "precision": {"$ref": "#/definitions/precision"},
        "bbox": {"$ref": "#/definitions/bbox"},
        "start_lat": {"type": "number", "minimum": -90, "maximum": 90},
        "end_lat": {"type": "number", "minimum": -90, "maximum": 90}
      },
      "additionalProperties": false
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="geo.long"></a>geo.long

Types covered by schema: `geo.long`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/geo.lat.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^geo\\.long$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "precision": {"$ref": "#/definitions/precision"},
        "bbox": {"$ref": "#/definitions/bbox"},
        "start_long": {"type": "number", "minimum": -180, "maximum": 180},
        "end_long": {"type": "number", "minimum": -180, "maximum": 180}
      },
      "additionalProperties": false
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="geo.pair"></a>geo.pair

Types covered by schema: `geo.pair`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/geo.lat.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^geo\\.pair$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "precision": {"$ref": "#/definitions/precision"},
        "bbox": {"$ref": "#/definitions/bbox"},
        "start_lat": {"type": "number", "minimum": -90, "maximum": 90},
        "end_lat": {"type": "number", "minimum": -90, "maximum": 90},
        "start_long": {"type": "number", "minimum": -180, "maximum": 180},
        "end_long": {"type": "number", "minimum": -180, "maximum": 180},
        "join_with": {"$ref": "#/definitions/join_with"},
        "as_list": {"$ref": "#/definitions/as_list"},
        "lat_first": {"$ref": "#/definitions/affirmative_check"}
      },
      "additionalProperties": false
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="ip"></a>IP types (ip, ipv4)

Types covered by schema: `ip, ipv4`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/date.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^ip(v4)?$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "base": {
          "description": "base of ip address",
          "examples": ["192", "10.", "100.100", "192.168.", "10.10.10"],
          "type": "string",
          "pattern": "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.?){1,4}$"
        },
        "cidr": {
          "description": "cidr notation i.e. 192.168.0.0/16, only /8 /16 /24 supported",
          "examples": ["192.168.0.0/24", "10.0.0.0/16", "100.0.0.0/8"],
          "type": "string",
          "pattern": "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])/(8|16|24)$"
        }
      },
      "not": {
        "description": "cidr and base should not both be specified",
        "anyOf": [
          {"required": ["cidr", "base"]}
        ]
      }
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="range"></a>Range types (range, rand_range)

Types covered by schema: `range, rand_range`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/range.schema.json",
  "type": "object",
  "required": ["type", "data"],
  "properties": {
    "type": {  "type": "string", "pattern": "^(rand_)?range$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "cast": {"$ref": "#/definitions/cast"}
      }
    },
    "data": {
      "oneOf": [
        {
          "type": "array",
          "minItems": 1,
          "maxItems": 3,
          "uniqueItems": false,
          "items": { "type": "number" }
        },
        {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "uniqueItems": false,
            "items": { "type": "number" }
          }
        }
      ]
    }
  }
}
```
</details>

# <a name="unicode_range"></a>unicode_range

Types covered by schema: `unicode_range`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/char_class.schema.json",
  "type": "object",
  "required": ["type", "data"],
  "properties": {
    "type": {"type": "string", "pattern": "^unicode_range$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "min": {"$ref": "#/definitions/min"},
        "max": {"$ref": "#/definitions/max"},
        "mean": {"$ref": "#/definitions/mean"},
        "stddev": {"$ref": "#/definitions/stddev"}
      },
      "not": {
        "description": "count should not be present if min max or mean are present",
        "anyOf": [
          {"required": ["count", "min"]},
          {"required": ["count", "max"]},
          {"required": ["count", "mean"]}
        ]
      }
    },
    "data": {
      "oneOf": [
        {
          "type": "array",
          "minItems": 2,
          "maxItems": 2,
          "uniqueItems": false,
          "items": {
            "oneOf": [
              {"type": "string", "pattern": "(0x)?[0-9a-fA-F]{4}"},
              {"type": "integer"}
            ]
          }
        },
        {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "uniqueItems": false,
            "items": {
              "oneOf": [
                {"type": "string", "pattern": "(0x)?[0-9a-fA-F]{4}"},
                {"type": "integer"}
              ]
            }
          }
        }
      ]
    }
  }
}
```
</details>

# <a name="uuid"></a>uuid

Types covered by schema: `uuid`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/uuid.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^uuid$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"}
      }
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="values"></a>values

Types covered by schema: `values`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/dataspec/schemas/values.schema.json",
  "type": "object",
  "required": ["data"],
  "properties": {
    "type": {  "type": "string", "pattern": "^values$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"}
      }
    },
    "data": {
      "oneOf": [
        { "type":  "string"},
        { "type":  "number"},
        { "type":  "boolean"},
        {
          "type": "array",
          "minItems": 1,
          "uniqueItems": false
        },
        {
          "type": "object",
          "minProperties": 1,
          "additionalProperties": { "type": "number" }
        }
      ]
    }
  }
}
```
</details>

