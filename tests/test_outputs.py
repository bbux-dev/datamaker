import os
from dataspec import outputs
from dataspec import template_engines as engines

test_dir = f'{os.path.dirname(os.path.realpath(__file__))}'
outdir = f'{test_dir}/../build'


def test_outputs_single_field():
    # for coverage
    writer = outputs.FileWriter(
        outdir=outdir,
        outname='test_single',
        extension='txt',
        records_per_file=1
    )
    output = outputs.SingleFieldOutput(writer, True)
    output.handle('key', 'value')
    output.finished_record()

    _verify_output('test_single-0.txt', 'key -> value\n')


def test_outputs_record_level():
    # for coverage
    writer = outputs.FileWriter(
        outdir=outdir,
        outname='test_record',
        extension='txt',
        records_per_file=1
    )

    engine = engines.for_file(f'{test_dir}/data/template.jinja')
    output = outputs.RecordLevelOutput(engine, writer)

    # template looks like: A:{{ A }}, B:{{ B }}, C:{{ C }}
    output.handle('A', '1')
    output.handle('B', '2')
    output.handle('C', '3')
    output.handle('D', '4')
    output.finished_record(iteration=1,
                           group_name='TEST',
                           exclude_internal=True)

    _verify_output('test_record-0.txt', 'A:1, B:2, C:3\n')


def test_format_json():
    as_json = outputs.format_json({'field': 'value'})
    assert as_json == "{\"field\": \"value\"}"


def test_format_json_pretty():
    as_json = outputs.format_json_pretty({'field': 'value'})
    assert as_json == "{\n    \"field\": \"value\"\n}"


def test_format_csv():
    as_csv = outputs.format_csv({'field1': 'value1', 'field2': 'value2'})
    assert as_csv == "value1,value2"


def test_single_file_writer(tmpdir):
    writer = outputs.SingleFileWriter(
        outdir=tmpdir,
        outname='foo.bar',
        overwrite=True
    )

    writer.write("stuff")
    with open(os.path.join(tmpdir, 'foo.bar')) as handle:
        text = handle.read().strip()
    assert text == 'stuff'


def test_single_file_writer_append(tmpdir):
    writer = outputs.SingleFileWriter(
        outdir=tmpdir,
        outname='single_file_append',
        overwrite=False
    )

    writer.write("stuff1")
    writer.write("stuff2")
    with open(os.path.join(tmpdir, 'single_file_append')) as handle:
        text = handle.read().strip()
    assert text == 'stuff1\nstuff2'


def test_std_out_writer():
    # for coverage
    outputs.StdOutWriter().write("blah")


def _verify_output(fild_name, expected_content):
    with open(f'{outdir}/{fild_name}') as handle:
        content = handle.read()

    assert expected_content == content
