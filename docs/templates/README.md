## Process for Updating FIELDSPECS.md

Instead of hard coding all the formats for each example, which is prone to error,
we only hard code a small code fragment and some parameters.  These are then used
to execute the DataSpec API and to generate the JSON, YAML, API, and to run the
generated spec to capture the output of the example. This makes it easier to add
new examples and to have all the formats for the example generated.

### Add new Example to `examples.py`

This should be the core piece of code used to populate the spec using the builder.

Example

```python
    Example(
        name="new_example_one",
        iterations=10,
        fragment="""
spec_builder.new_type("name", ["data", "elements"], key1=5, key2="fluffy")
""",
        pipes="--format json-pretty"
    ),
```

### Create the new `field_specs_template_data.json`

Next we need to generate the pieces from the Example and add them to the field_specs_template_data.json
file.

```bash
./build_examples.py > field_specs_template_data.json
```

Or just update the existing data with the new info

```bash
./build_examples.py | tail -20
```

### Apply Updates to the FIELDSPEC.md file

The last step is to apply the updated template data to the FIELDSPEC.md file.
There are several macros in the FIELDSPECS.jinja.md that will format the examples
in a uniform manner.

```bash
./tool.py -i field_specs_template_data.json -m apply
```