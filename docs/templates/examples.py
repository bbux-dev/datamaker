from typing import NamedTuple


class Example(NamedTuple):
    """
    :param name: of example
    :param iterations: number of iterations to run to capture output
    :param fragment: code fragment for api example, excludes import dataspec and spec_builder.build()
    :param pipes: extra args or command line pipes i.e. sort | tail -3, to add to command line
    """
    name: str
    iterations: int
    fragment: str
    pipes: str = ""


EXAMPLES = [
    Example(
        name="overview_example_one",
        iterations=7,
        fragment="""
refs = spec_builder.refs()
one = refs.values('ONE', ["A", "B", "C"])
two = refs.values('TWO', [1, 2, 3])

spec_builder.combine('combine', refs=[one, two])
"""
    ),
    Example(
        name="overview_example_two",
        iterations=12,
        fragment="""
refs = spec_builder.refs()
one = refs.values('ONE', ["A", "B", "C"])
two = refs.values('TWO', [1, 2, 3, 4])

spec_builder.combine('combine', refs=[one, two])
""",
        pipes="\\\n  | sort"),
    Example(
        name="overview_example_three",
        iterations=5,
        fragment="""
refs = spec_builder.refs()
one = refs.values('ONE', ["A", "B", "C"], sample=True)
two = refs.values('TWO', [1, 2, 3, 4], sample="yes")

spec_builder.combine('combine', refs=[one, two])
""",
    ),
    Example(
        name="values_shorthand_one",
        iterations=5,
        fragment="""
spec_builder.add_field('field1', dataspec.builder.values([1, 2, 3, 4, 5]))
spec_builder.add_field('field2', dataspec.builder.values({"A": 0.5, "B": 0.3, "C": 0.2}))
spec_builder.add_field('field3', dataspec.builder.values("CONSTANT"))
""",
    ),
    Example(
        name="values_shorthand_two",
        iterations=5,
        fragment="""
spec_builder.add_field('field1', [1, 2, 3, 4, 5])
spec_builder.add_field('field2', {"A": 0.5, "B": 0.3, "C": 0.2})
spec_builder.add_field('field3', "CONSTANT")
""",
    ),
    Example(
        name="inline_key_example",
        iterations=5,
        fragment="""
spec_builder.add_field("network:ipv4?cidr=192.168.0.0/16", {})
"""),
    Example(
        name="config_example_one",
        iterations=5,
        fragment="""
spec_builder.values('ONE', [1, 2, 3], prefix='TEST', suffix='@DEMO')
spec_builder.values('TWO?prefix=TEST&suffix=@DEMO', [1, 2, 3])
"""),
    Example(
        name="common_config_example_one",
        iterations=5,
        fragment="""
spec_builder.values('field', 
                    ["world", "beautiful", "destiny"], 
                    prefix='hello ')
"""),
    Example(
        name="count_dist_example_one",
        iterations=5,
        fragment="""
spec_builder.char_class(key='field',
                        data='visible',
                        count_dist='normal(mean=5, stddev=2, min=1, max=9)')
"""),
    Example(
        name="constants_example_one",
        iterations=5,
        fragment="""
spec_builder.values('constant1', 42)
spec_builder.add_field('shorthand_constant', "This is simulated data and should not be used for nefarious purposes")
"""),
    Example(
        name="list_values_example_one",
        iterations=5,
        fragment="""
spec_builder.values('list1', [200, 202, 303, 400, 404, 500])
spec_builder.add_field("shorthand_list",  [200, 202, 303, 400, 404, 500])
spec_builder.add_field("random_pet?sample=true", ["dog", "cat", "bunny", "pig", "rhino", "hedgehog"])
"""),
    Example(
        name="weighted_values_example_one",
        iterations=5,
        fragment="""
spec_builder.values('weighted1', {
        "200": 0.4, "202": 0.3, "303": 0.1,
        "400": 0.05, "403": 0.05, "404": 0.05, "500": 0.05
})
spec_builder.add_field("shorthand_weighted", {
        "200": 0.4, "202": 0.3, "303": 0.1,
        "400": 0.05, "403": 0.05, "404": 0.05, "500": 0.05
})
"""),
    Example(
        name="sample_mode_example_one",
        iterations=5,
        fragment="""
refs = spec_builder.refs()
refs.add_field('ONE?sample=true', ["A", "B", "C"])
refs.add_field('TWO?sample=true', [1, 2, 3, 4])

spec_builder.combine('combine', refs=['ONE', 'TWO'])
"""),
    Example(
        name="combine_spec_example_one",
        iterations=5,
        fragment="""
refs = spec_builder.refs()
first = refs.values(key="first",
                    data=["zebra", "hedgehog", "llama", "flamingo"])
last = refs.values(key="last",
                   data=["jones", "smith", "williams"])

spec_builder.combine('combine', refs=[first, last], join_with=" ")
"""),
    Example(
        name="combine_list_spec_example_one",
        iterations=5,
        fragment="""
refs = spec_builder.refs()
first = refs.values(
    key="first",
    data=["zebra", "hedgehog", "llama", "flamingo"])
last = refs.values(
    key="last",
    data=["jones", "smith", "williams"])
middle = refs.values(
    key="middle",
    data=["cloud", "sage", "river"])
middle_initial = refs.values(
    key="middle_initial",
    data={"a": 0.3, "m": 0.3, "j": 0.1, "l": 0.1, "e": 0.1, "w": 0.1})

spec_builder.combine_list(
    key='full_name',
    refs=[
        [first, last],
        [first, middle, last],
        [first, middle_initial, last],
        ],
    join_with=" ")
"""),
    Example(
        name="uniform_date_example_exhaustive",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?duration_days=90&start=15-Dec-2050 12:00&format=%d-%b-%Y %H:%M", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="uniform_date_example_one",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="uniform_date_example_two",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?offset=1", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="uniform_date_example_three",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?duration_days=1", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="uniform_date_example_four",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?duration_days=10", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="uniform_date_example_five",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?duration_days=1&offset=1", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="uniform_date_example_six",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?duration_days=1&offset=-1", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="uniform_date_example_seven",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?duration_days=1&offset=1&start=15-12-2050", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="uniform_date_example_eight",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?duration_days=1&start=15-Dec-2050 12:00&format=%d-%b-%Y %H:%M", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2M -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="centered_date_example_exhaustive",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?center_date=20500601 12:00&format=%Y%m%d %H:%M&stddev_days=2", {})
""",
        pipes="\\\n  | sort -n | uniq | sed -n '1p;$p'"),
    Example(
        name="centered_date_example_one",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?stddev_days=1", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="centered_date_example_two",
        iterations=1000,
        fragment="""
spec_builder.add_field("dates:date?stddev_days=15", {})
""",
        pipes="\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    Example(
        name="range_spec_example_one",
        iterations=5,
        fragment="""
spec_builder.range_spec(key="zero_to_ten", data=[0, 10, 0.5])
spec_builder.add_field(key="range_shorthand1:range", spec={"data": [0, 10, 0.5]})
spec_builder.add_field(key="range_shorthand2:range", spec=[0, 10, 0.5])
"""),
    Example(
        name="range_spec_example_two",
        iterations=5,
        fragment="""
spec_builder.range_spec(
    key="salaries",
    data=[
      [1000, 10000, 1000],
      [10000, 55000, 5000],
      [55000, 155000, 10000]
    ])
"""),
    Example(
        name="rand_range_spec_example_one",
        iterations=5,
        fragment="""
spec_builder.rand_range(
    key="population",
    data=[100, 1000],
    cast="int")
spec_builder.add_field("pop:rand_range?cast=f", [200.2, 1222.7, 2])
""",
        pipes=" --format json -x"),
    Example(
        name="uuid_spec_example_one",
        iterations=5,
        fragment="""
spec_builder.uuid(key="id")
spec_builder.add_field("id_shorthand:uuid", {})
"""),
    Example(
        name="char_class_spec_example_one",
        iterations=5,
        fragment="""
spec_builder.add_field("one_to_five_digits:cc-digits?min=1&max=5", {})
"""),
    Example(
        name="char_class_spec_example_two",
        iterations=10,
        fragment="""
spec_builder.char_class(
    key="password",
    data=[
      "word",
      "special",
      "hex-lower",
      "M4$p3c!@l$@uc3"
    ],
    mean=14,
    stddev=2,
    min=10,
    max=18,
    exclude=["-", "\\\""])
"""),
    Example(
        name="unicode_range_example_one",
        iterations=10,
        fragment="""
spec_builder.unicode_range("text", ["3040", "309f"], mean=5)
"""),
    Example(
        name="geo_point_spec_example_one",
        iterations=5,
        fragment="""
spec_builder.geo_pair("egypt", bbox=[31.33134, 22.03795, 34.19295, 25.00562], precision=3)
"""),
    Example(
        name="ip_spec_example_one",
        iterations=5,
        fragment="""
spec_builder.ipv4(key="network", cidr="2.22.222.0/16")
spec_builder.add_field("network_shorthand:ip?cidr=2.22.222.0/16", {})
spec_builder.add_field("network_with_base:ip?base=192.168.0", {})
"""),
    Example(
        name="ip_precise_example_one",
        iterations=5,
        fragment="""
spec_builder.add_field("network:ip.precise?cidr=10.0.0.0/8", {})
"""),
    Example(
        name="ip_precise_example_two",
        iterations=5,
        fragment="""
spec_builder.add_field("network:ip.precise?cidr=192.168.0.0/14&sample=true", {})
"""),
    Example(
        name="ip_precise_example_three",
        iterations=5,
        fragment="""
spec_builder.add_field("network:ip.precise?cidr=2.22.0.0/22", {})
"""),
    Example(
        name="weighted_ref_example_one",
        iterations=5,
        fragment="""
refs = spec_builder.refs()
refs.add_field('GOOD_CODES', {"200": 0.5, "202": 0.3, "203": 0.1, "300": 0.1})
refs.add_field('BAD_CODES', {"400": 0.5, "403": 0.3, "404": 0.1, "500": 0.1})

spec_builder.weightedref('http_code', data={"GOOD_CODES": 0.7, "BAD_CODES": 0.3})
"""),
    Example(
        name="select_list_example_one",
        iterations=5,
        fragment="""
spec_builder.select_list_subset(
    key="ingredients",
    data=["onions", "mushrooms", "garlic", "bell peppers", "spinach", "potatoes", "carrots"],
    mean=3,
    stddev=1,
    min=2,
    max=4,
    join_with=", ")
"""),
    Example(
        name="select_list_example_two",
        iterations=5,
        fragment="""
spec_builder.select_list_subset(
    key="ingredients",
    data=["onions", "mushrooms", "garlic", "bell peppers", "spinach", "potatoes", "carrots"],
    mean=3,
    stddev=1,
    min=2,
    max=4,
    join_with="\\", \\"",
    quote="\\"")
"""),
    Example(
        name="csv_spec_example_one",
        iterations=5,
        fragment="""
spec_builder.csv(
    key="cities",
    datafile="cities.csv",
    delimiter="~",
    sample=True)
""",
        pipes="--datadir ./data"),
    Example(
        name="csv_spec_example_two",
        iterations=5,
        fragment="""
spec_builder.configref(
    key="tabs_config",
    datafile="tabs.csv",
    delimiter="\\t",
    headers=True)
spec_builder.csv(
    key="status",
    column=1,
    configref="tabs_config")
spec_builder.csv(
    key="description",
    column=2,
    configref="tabs_config")
spec_builder.add_field("status_type:csv?configref=tabs_config&column=3", {})
""",
        pipes="--datadir ./data"),
    Example(
        name="csv_select_example_one",
        iterations=5,
        fragment="""
spec_builder.csv_select(
    key="placeholder",
    data={
        "geonameid": 1,
        "name": 2,
        "latitude": 5,
        "longitude": 6,
        "country_code": 9,
        "population": 15
    },
    datafile="allCountries.txt",
    headers=False,
    delimiter="\t")
""",
        pipes="--datadir ./data"),
    Example(
        name="nested_example_one",
        iterations=1,
        fragment="""
geo_fields = dataspec.spec_builder()
geo_fields.add_field("place_id:cc-digits?mean=5", {})
geo_fields.add_field("coordinates:geo.pair?as_list=true", {})

user_fields = dataspec.spec_builder()
user_fields.uuid("user_id")
user_fields.nested("geo", geo_fields.build())

spec_builder.uuid("id")
spec_builder.nested("user", user_fields.build())
""",
        pipes="--format json-pretty"
    ),
]
