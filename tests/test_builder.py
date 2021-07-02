import pytest
import dataspec.builder as builder
from dataspec import distributions, DataSpec, SpecException


def test_api_builder():
    # raw data for both specs
    animal_names = ['zebra', 'hedgehog', 'llama', 'flamingo']
    action_list = ['fling', 'jump', 'launch', 'dispatch']
    domain_weights = {
        "gmail.com": 0.6,
        "yahoo.com": 0.3,
        "hotmail.com": 0.1
    }

    # first build uses direct build methods
    builder1 = builder.Builder()
    refs1 = builder1.refs_builder
    domains = refs1.values('DOMAINS', domain_weights)
    animals = refs1.values('ANIMALS', animal_names)
    actions = refs1.values('ACTIONS', action_list, sample=True)
    handles = refs1.combine('HANDLE', refs=[animals, actions], join_with='_')
    builder1.combine('email', refs=[handles, domains])

    spec1 = builder1.build()

    # second builder uses the fluent api style
    builder2 = builder.Builder()

    animals_spec = builder.values(data=animal_names)
    actions_spec = builder.values(data=action_list, sample=True)
    domains_spec = builder.values(data=domain_weights)
    # combines ANIMALS and ACTIONS
    handle_spec = builder.combine(refs=['ANIMALS', 'ACTIONS'], join_with='_')

    builder2.add_ref('DOMAINS', domains_spec) \
        .add_ref('ANIMALS', animals_spec) \
        .add_ref('ACTIONS', actions_spec) \
        .add_ref('HANDLE', handle_spec)

    builder2.add_field('email', builder.combine(refs=['HANDLE', 'DOMAINS']))

    spec2 = builder2.build()

    assert spec1 == spec2


field_spec_build_tests = [
    (builder.values([1, 2, 3], prefix="foo"),
     {"type": "values", "data": [1, 2, 3], "config": {"prefix": "foo"}}),
    (builder.combine(refs=["ONE", "TWO"], join_with='@'),
     {"type": "combine", "refs": ["ONE", "TWO"], "config": {"join_with": "@"}}),
    (builder.combine(fields=["ONE", "TWO"], join_with='-'),
     {"type": "combine", "fields": ["ONE", "TWO"], "config": {"join_with": "-"}}),
    (builder.combine_list(refs=[["A", "B"], ["A", "B", "C"]], join_with=","),
     {"type": "combine-list", "config": {"join_with": ","}, "refs": [["A", "B"], ["A", "B", "C"]]}),
    (builder.range_spec([1, 5, 1], as_list=True, count=2),
     {"type": "range", "config": {"as_list": True, "count": 2}, "data": [1, 5, 1]}),
    (builder.rand_range([20, 44], count=[2, 3, 4]),
     {"type": "rand_range", "config": {"count": [2, 3, 4]}, "data": [20, 44]}),
    (builder.date(duration_days=3, offset=4),
     {"type": "date", "config": {"duration_days": 3, "offset": 4}}),
    (builder.date_iso(duration_days=4, offset=5),
     {"type": "date.iso", "config": {"duration_days": 4, "offset": 5}}),
    (builder.date_iso_us(duration_days=5, offset=6),
     {"type": "date.iso.us", "config": {"duration_days": 5, "offset": 6}}),
    (builder.uuid(quote="'"),
     {"type": "uuid", "config": {"quote": "'"}}),
    (builder.char_class("visible", min=5, max=7),
     {"type": "char_class", "config": {"min": 5, "max": 7}, "data": "visible"}),
    (builder.unicode_range(["3040", "309f"], mean=3),
     {"type": "unicode_range", "config": {"mean": 3}, "data": ["3040", "309f"]}),
    (builder.unicode_range([["3040", "309f"]], mean=3),
     {"type": "unicode_range", "config": {"mean": 3}, "data": [["3040", "309f"]]}),
    (builder.geo_lat(start_lat=75.5),
     {"type": "geo.lat", "config": {"start_lat": 75.5}}),
    (builder.geo_long(bbox=[31.3, 22.0, 34.1, 25.0]),
     {"type": "geo.long", "config": {"bbox": [31.3, 22.0, 34.1, 25.0]}}),
    (builder.geo_pair(join_with=":", as_list="yes"),
     {"type": "geo.pair", "config": {"join_with": ":", "as_list": "yes"}}),
    (builder.ip(base="192.168"),
     {"type": "ip", "config": {"base": "192.168"}}),
    (builder.ipv4(cidr="2.22.222.0/16"),
     {"type": "ipv4", "config": {"cidr": "2.22.222.0/16"}}),
    (builder.ip_precise(cidr="10.0.0.0/8"),
     {"type": "ip.precise", "config": {"cidr": "10.0.0.0/8"}}),
    (builder.weightedref({"One": 0.5, "Two": 0.3, "Three": 0.2}),
     {"type": "weightedref", "data": {"One": 0.5, "Two": 0.3, "Three": 0.2}}),
    (builder.select_list_subset(data=["A", "B", "C"], mean=5, stddev=2),
     {"type": "select_list_subset", "config": {"mean": 5, "stddev": 2}, "data": ["A", "B", "C"]}),
    (builder.select_list_subset(ref="LIST", mean=5, stddev=2),
     {"type": "select_list_subset", "config": {"mean": 5, "stddev": 2}, "ref": "LIST"}),
    (builder.csv(datafile="demo.csv", sample="on"),
     {"type": "csv", "config": {"datafile": "demo.csv", "sample": "on"}}),
    (builder.csv_select(data={"one": 1, "two": 2}, headers=False),
     {"type": "csv_select", "config": {"headers": False}, "data": {"one": 1, "two": 2}}),
    (builder.nested(fields={"one": {"type": "values", "data": 1}}),
     {"type": "nested", "fields": {"one": {"type": "values", "data": 1}}}),
]


@pytest.mark.parametrize("generated_spec,expected_spec", field_spec_build_tests)
def test_spec_builder(generated_spec, expected_spec):
    assert generated_spec == expected_spec


full_spec_build_tests = [
    (builder.Builder().values('name', [1, 2, 3], prefix="foo"),
     {"name": {"type": "values", "data": [1, 2, 3], "config": {"prefix": "foo"}}}),
    (builder.Builder().combine('name', refs=["ONE", "TWO"], join_with='@'),
     {"name": {"type": "combine", "refs": ["ONE", "TWO"], "config": {"join_with": "@"}}}),
    (builder.Builder().combine('name', fields=["ONE", "TWO"], join_with='-'),
     {"name": {"type": "combine", "fields": ["ONE", "TWO"], "config": {"join_with": "-"}}}),
    (builder.Builder().combine_list('name', refs=[["A", "B"], ["A", "B", "C"]], join_with=","),
     {"name": {"type": "combine-list", "config": {"join_with": ","}, "refs": [["A", "B"], ["A", "B", "C"]]}}),
    (builder.Builder().range_spec('name', [1, 5, 1], as_list=True, count=2),
     {"name": {"type": "range", "config": {"as_list": True, "count": 2}, "data": [1, 5, 1]}}),
    (builder.Builder().rand_range('name', [20, 44], count=[2, 3, 4]),
     {"name": {"type": "rand_range", "config": {"count": [2, 3, 4]}, "data": [20, 44]}}),
    (builder.Builder().date('name', duration_days=3, offset=4),
     {"name": {"type": "date", "config": {"duration_days": 3, "offset": 4}}}),
    (builder.Builder().date_iso('name', duration_days=4, offset=5),
     {"name": {"type": "date.iso", "config": {"duration_days": 4, "offset": 5}}}),
    (builder.Builder().date_iso_us('name', duration_days=5, offset=6),
     {"name": {"type": "date.iso.us", "config": {"duration_days": 5, "offset": 6}}}),
    (builder.Builder().uuid('name', quote="'"),
     {"name": {"type": "uuid", "config": {"quote": "'"}}}),
    (builder.Builder().char_class('name', "visible", min=5, max=7),
     {"name": {"type": "char_class", "config": {"min": 5, "max": 7}, "data": "visible"}}),
    (builder.Builder().char_class_abbrev('name', "visible", min=3, max=10),
     {"name": {"type": "cc-visible", "config": {"min": 3, "max": 10}}}),
    (builder.Builder().unicode_range('name', ["3040", "309f"], mean=3),
     {"name": {"type": "unicode_range", "config": {"mean": 3}, "data": ["3040", "309f"]}}),
    (builder.Builder().unicode_range('name', [["3040", "309f"]], mean=3),
     {"name": {"type": "unicode_range", "config": {"mean": 3}, "data": [["3040", "309f"]]}}),
    (builder.Builder().geo_lat('name', start_lat=75.5),
     {"name": {"type": "geo.lat", "config": {"start_lat": 75.5}}}),
    (builder.Builder().geo_long('name', bbox=[31.3, 22.0, 34.1, 25.0]),
     {"name": {"type": "geo.long", "config": {"bbox": [31.3, 22.0, 34.1, 25.0]}}}),
    (builder.Builder().geo_pair('name', join_with=":", as_list="yes"),
     {"name": {"type": "geo.pair", "config": {"join_with": ":", "as_list": "yes"}}}),
    (builder.Builder().ip('name', base="192.168"),
     {"name": {"type": "ip", "config": {"base": "192.168"}}}),
    (builder.Builder().ipv4('name', cidr="2.22.222.0/16"),
     {"name": {"type": "ipv4", "config": {"cidr": "2.22.222.0/16"}}}),
    (builder.Builder().ip_precise('name', cidr="10.0.0.0/8"),
     {"name": {"type": "ip.precise", "config": {"cidr": "10.0.0.0/8"}}}),
    (builder.Builder().weightedref('name', {"One": 0.5, "Two": 0.3, "Three": 0.2}),
     {"name": {"type": "weightedref", "data": {"One": 0.5, "Two": 0.3, "Three": 0.2}}}),
    (builder.Builder().select_list_subset('name', data=["A", "B", "C"], mean=5, stddev=2),
     {"name": {"type": "select_list_subset", "config": {"mean": 5, "stddev": 2}, "data": ["A", "B", "C"]}}),
    (builder.Builder().select_list_subset('name', ref="LIST", mean=5, stddev=2),
     {"name": {"type": "select_list_subset", "config": {"mean": 5, "stddev": 2}, "ref": "LIST"}}),
    (builder.Builder().csv('name', datafile="demo.csv", sample="on"),
     {"name": {"type": "csv", "config": {"datafile": "demo.csv", "sample": "on"}}}),
    (builder.Builder().csv_select('name', data={"one": 1, "two": 2}, headers=False),
     {"name": {"type": "csv_select", "config": {"headers": False}, "data": {"one": 1, "two": 2}}}),
    (builder.Builder().nested('name', fields={"one": {"type": "values", "data": 1}}),
     {"name": {"type": "nested", "fields": {"one": {"type": "values", "data": 1}}}}),
]


@pytest.mark.parametrize("field_info,expected_spec", full_spec_build_tests)
def test_full_spec_builder(field_info, expected_spec):
    generated_spec = field_info.builder.build().raw_spec
    assert generated_spec == expected_spec


invalid_spec_build_tests = [
    builder.Builder().values('name', data=[1, 2, 3], count={}),  # invalid count
    builder.Builder().combine('name', refs=["ONE", "TWO"], join_with='@'),  # no refs defined
    builder.Builder().combine('name', fields=["ONE", "TWO"], join_with='-'),  # no refs defined
    builder.Builder().combine_list('name', refs=[["A", "B"], ["A", "B", "C"]], join_with=","),
    builder.Builder().range_spec('name', [1, 5, 1], as_list=True, count={}),  # invalid count
    builder.Builder().rand_range('name', [20, 44], count=None),  # invalid count
    builder.Builder().date('name', duration_days={1: 0.5, 2: 0.5}, offset=4),  # invalid duration_days
    builder.Builder().date_iso('name', duration_days=4, offset="1"),  # invalid offset
    builder.Builder().date_iso_us('name', duration_days=5, offset=6, start=42),  # invalid start
    builder.Builder().char_class('name', "visible", min="5", max=7),  # min should be number
    builder.Builder().char_class_abbrev('name', "visible", min=3, max="10"),  # max should be number
    builder.Builder().unicode_range('name', ["3040", "309f"], count=4, mean=3),  # can't have count and mean
    builder.Builder().unicode_range('name', [["3040", "309f"]], count=5, max=6),  # can't have count and max
    builder.Builder().geo_lat('name', start_lat=175.5),  # lat out of range
    builder.Builder().geo_long('name', bbox=[31.3, 22.0]),  # bbox wrong dimensions
    builder.Builder().geo_pair('name', join_with=":", precision="yes"),  # invalid precision
    builder.Builder().ip('name', base="192.1680"),  # type in base
    builder.Builder().ipv4('name', cidr="2.22.222.0/22"),  # not one of supported bases
    # TODO: when schemas for these are created
    # builder.Builder().weightedref('name', {"One": 0.5, "Two": 0.3, "Three": 0.2}),
    # builder.Builder().select_list_subset('name', data=["A", "B", "C"], mean=5, stddev=2),
    # builder.Builder().select_list_subset('name', ref="LIST", mean=5, stddev=2),
    # builder.Builder().csv('name', datafile="demo.csv", sample="on"),
    # builder.Builder().csv_select('name', data={"one": 1, "two": 2}, headers=False),
    # builder.Builder().nested('name', fields={"one": {"type": "values", "data": 1}}),
]


@pytest.mark.parametrize("field_info", invalid_spec_build_tests)
def test_invalid_spec_builder(field_info):
    spec = field_info.builder.build()
    with pytest.raises(SpecException):
        next(spec.generator(1, enforce_schema=True))


def test_api_change():
    animal_names = ['zebra', 'hedgehog', 'llama', 'flamingo']
    action_list = ['fling', 'jump', 'launch', 'dispatch']
    domain_weights = {
        "gmail.com": 0.6,
        "yahoo.com": 0.3,
        "hotmail.com": 0.1
    }

    # for building the final spec
    spec_builder = builder.Builder()

    # for building the regs section of the spec
    refs = spec_builder.refs_builder

    # spec for each field and reference
    animals = refs.values('ANIMALS', data=animal_names)
    actions = refs.values('ACTIONS', data=action_list)
    domains = refs.values('DOMAINS', data=domain_weights)
    # combines ANIMALS and ACTIONS
    handles = refs.combine('HANDLE', refs=[animals, actions], join_with='_')

    spec_builder.combine('email', refs=[handles, domains], join_with='@')

    spec = spec_builder.build()

    first = next(spec.generator(1))
    assert first['email'].startswith('zebra_fling@')


def test_create_key_list():
    entries = [builder.FieldInfo('key1', 'value1'), builder.FieldInfo('key2', 'value2')]
    keys = builder._create_key_list(entries)
    assert keys == ['key1', 'key2']


short_hand_tests = [
    ("network:ipv4?cidr=192.168.0.0/16", "network", "192.168."),
    ("dates:date?duration_days=1&start=15-Dec-2050 12:00&format=%d-%b-%Y %H:%M", "dates", "-Dec-2050")
]


@pytest.mark.parametrize("key_as_spec,field_name,first_value_contains", short_hand_tests)
def test_shorthand_key_support(key_as_spec, field_name, first_value_contains):
    spec_builder = builder.Builder()
    spec_builder.add_field(key_as_spec, {})
    spec = spec_builder.build()
    first = next(spec.generator(1, enforce_schema=True))
    assert field_name in first
    assert first_value_contains in str(first[field_name])


def test_spec_builder():
    spec_builder = builder.spec_builder()
    spec = spec_builder.values('name', ['a', 'b', 'c']).to_spec()
    assert isinstance(spec, DataSpec)

    single = next(spec.generator(1))
    assert single == {'name': 'a'}


def test_distribution_as_count():
    spec_builder = builder.spec_builder()
    distribution = distributions.uniform(1, 3)
    spec = spec_builder.values('name', ['a', 'b', 'c'], count=distribution).to_spec()
    assert isinstance(spec, DataSpec)

    single = next(spec.generator(1))
    assert 1 <= len(single['name']) < 3
