"""
Module holds output related classes and functions
"""
import os
import json
import logging
import dataspec
from .types import registry

log = logging.getLogger(__name__)


@dataspec.registry.formats('json')
def format_json(record):
    """ formats the record as compressed json """
    return json.dumps(record)


@dataspec.registry.formats('json-pretty')
def format_json_pretty(record):
    """ pretty prints the record as json """
    return json.dumps(record, indent=dataspec.types.get_default('json_indent'))


@dataspec.registry.formats('csv')
def format_csv(record):
    """ formats the values of the record as comma separated valpues """
    return ','.join([str(val) for val in record.values()])


class OutputHandlerInterface:
    """ Interface four handling generated output values """

    def handle(self, key, value):
        """
        This is called each time a new value is generated for a given field
        :param key: the field name
        :param value: the new value for the field
        :return: None
        """

    def finished_record(self,
                        iteration: int,
                        group_name: str,
                        exclude_internal: bool = False):
        """
        This is called whenever all of the fields for a record have been generated for one iteration
        :param iteration: iteration we are on
        :param group_name: group this record is apart of
        :param exclude_internal: if external fields should be excluded from output record
        :return: None
        """


class SingleFieldOutput(OutputHandlerInterface):
    """
    Writes each field as it is created
    """

    def __init__(self, writer, output_key):
        self.writer = writer
        self.output_key = output_key

    def handle(self, key, value):
        if self.output_key:
            self.writer.write('%s -> %s' % (key, value))
        else:
            self.writer.write(value)

    def finished_record(self, iteration=None, group_name=None, exclude_internal=False):
        pass


class RecordLevelOutput(OutputHandlerInterface):
    """
    Class to output after all fields have been generated
    """

    def __init__(self, record_processor, writer):
        """
        :param record_processor: turns the record into a string for writing
        :param writer: to write with
        """
        self.record_processor = record_processor
        self.writer = writer
        self.current = {}

    def handle(self, key, value):
        self.current[key] = value

    def finished_record(self, iteration, group_name, exclude_internal=False):
        current = self.current
        if not exclude_internal:
            current['_internal'] = {
                '_iteration': iteration,
                '_field_group': group_name
            }
        processed = self.record_processor.process(current)
        self.writer.write(processed)
        self.current.clear()


class WriterInterface:
    """
    Interface for classes that write the generated values out
    """

    def write(self, value):
        """
        Write the value to the configured output destination
        :param value: to write
        :return: None
        """


class StdOutWriter(WriterInterface):
    """
    Writes values to stdout
    """

    def write(self, value: str):
        print(value)


class SingleFileWriter(WriterInterface):
    """
    Writes all values to same file
    """

    def __init__(self, outdir: str, outname: str, overwrite: bool):
        self.outdir = outdir
        self.outname = outname
        self.overwrite = overwrite

    def write(self, value):
        outfile = os.path.join(self.outdir, self.outname)
        if self.overwrite:
            mode = 'w'
        else:
            mode = 'a'
        with open(outfile, mode) as handle:
            handle.write(value)
            handle.write('\n')
        log.info('Wrote data to %s', outfile)


class FileWriter(WriterInterface):
    """
    Writes processed output to disk
    """

    def __init__(self, outdir, outname, extension=None, records_per_file=1):
        self.outdir = outdir
        self.outname = outname
        self.extension = extension
        if self.extension and not extension.startswith('.'):
            self.extension = '.' + extension
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.count = 0
        self.records_per_file = records_per_file
        self.record_count = 0

    def write(self, value):
        extension = self.extension if self.extension else ''
        outfile = '%s/%s-%d%s' % (self.outdir, self.outname, self.count, extension)
        if self.record_count == 0:
            mode = 'w'
        else:
            mode = 'a'
        with open(outfile, mode) as handle:
            handle.write(value)
            handle.write('\n')
        self.record_count += 1
        if self.record_count == self.records_per_file:
            self.record_count = 0
            self.count += 1


class FormatProcessor:
    """
    A simple class that wraps a record formatting function
    """

    def __init__(self, key):
        self.format_func = registry.formats.get(key)

    def process(self, record):
        """
        :param record: dictionary of record to format
        :return: The formatted record
        """
        return self.format_func(record)
