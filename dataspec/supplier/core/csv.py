"""
Module for handling csv related data, deals with data typed as 'csv'
"""
from typing import Dict
import csv
import json
import os
import random
from typing import Union

import dataspec

# 250 MB
ONE_MB = 1024 * 1024
SMALL_ENOUGH_THRESHOLD = 250 * ONE_MB
_DEFAULT_BUFFER_SIZE = 1000000


class CsvDataBase:
    """
    Class for encapsulating the data for a single CSV file so that multiple suppliers
    only need one copy of the underlying data
    """

    def __init__(self, has_headers: bool):
        self.data = self._load_data()
        if has_headers:
            first_row = self.data.pop(0)
            self.mapping = {first_row[i]: i for i in range(len(first_row))}
        else:
            self.mapping = {}
        self.valid_keys = list(self.mapping.keys())
        if len(self.valid_keys) == 0:
            self.valid_keys = [i + 1 for i in range(len(self.data[0]))]

    def next(self, field: Union[int, str], iteration: int, sample: bool, count: int):
        """
        Obtains the next value(s) for the field for the given iteration
        :param field: key or one based index number
        :param iteration: current iteration
        :param sample: if sampling should be used
        :param count: number of values to return
        :return: array of values if count > 1 else the next value
        """

    def _load_data(self) -> list:
        """
        Method for subclass to load initial data
        :return: the loaded data
        """
        raise NotImplementedError()

    def _get_column_index(self, field: Union[int, str]):
        """
        Resolve the column index
        :param field: key or one based index number
        :return: the column index for the field
        """
        # if we had headers we can use that name, otherwise field should be one based index
        colidx = self.mapping.get(field)
        if colidx is None and not str(field).isdigit():
            raise dataspec.SpecException(f'Invalid field name: {field} for csv, known keys: {self.valid_keys}')
        if colidx is None:
            colidx = int(field) - 1
        return colidx


class SampleEnabledCsv(CsvDataBase):
    """
    CSV Data that reads whole file into memory. Supports Sampling of columns and counts greater than 1.
    """
    def __init__(self, csv_path: str, delimiter: str, quotechar: str, has_headers: bool):
        self.csv_path = csv_path
        self.delimiter = delimiter
        self.quotechar = quotechar
        super().__init__(has_headers)

    def _load_data(self):
        with open(self.csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter, quotechar=self.quotechar)
            return list(reader)

    def next(self, field, iteration, sample, count):
        colidx = self._get_column_index(field)

        values = []
        for i in range(count):
            if sample:
                idx = random.randint(0, len(self.data) - 1)
            else:
                idx = iteration % len(self.data) + i
            values.append(self.data[idx][colidx])
        if count == 1:
            return values[0]
        return values


class BufferedCsvData(CsvDataBase):
    """
    CSV Data that buffers in a section of the CSV file at a time. Does NOT support sampling or counts greater than 1 for
    columns.
    """
    def __init__(self, csv_path: str, delimiter: str, quotechar: str, has_headers: bool, buffer_size: int):
        self.csv_path = csv_path
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.size = buffer_size
        self.increment = -1
        self.data = None  # type: ignore
        self.fill_buffer(0)
        # need to populate data before super constructor call
        super().__init__(has_headers)

    def _load_data(self):
        self.fill_buffer(0)
        return self.data

    def fill_buffer(self, iteration: int) -> None:
        """
        Fills the buffer of data for this iteration
        :param iteration: current record number being processed
        :return: None
        """
        new_increment = int(iteration / self.size)
        if new_increment == self.increment:
            return

        self.increment = new_increment
        start = self.size * self.increment + 1
        end = start + self.size + 1
        buff = []
        with open(self.csv_path) as handle:
            rows = csv.reader(handle, delimiter=self.delimiter, quotechar=self.quotechar)
            for line in rows:
                if rows.line_num == end:
                    break
                if rows.line_num >= start:
                    buff.append(line)
        self.data = buff

    def next(self, field, iteration, sample, count):
        if sample:
            raise dataspec.SpecException('Large CSV files do not support sample mode')
        if count > 1:
            raise dataspec.SpecException('Large CSV files only support count of 1')
        self.fill_buffer(iteration)
        colidx = self._get_column_index(field)

        idx = iteration % self.size
        if idx >= len(self.data):
            raise dataspec.SpecException("Exceeded end of CSV data, unable to proceed with large CSV files")
        return self.data[idx][colidx]


class CsvSupplier(dataspec.ValueSupplierInterface):
    """
    Class for supplying data from a specific field in a csv file
    """

    def __init__(self, csv_data, field_name, sample, count_supplier: dataspec.ValueSupplierInterface):
        self.csv_data = csv_data
        self.field_name = field_name
        self.sample = sample
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        return self.csv_data.next(self.field_name, iteration, self.sample, count)


# to keep from reloading the same CsvData
_csv_data_cache: Dict[str, CsvDataBase] = {}


@dataspec.registry.types('csv')
def configure_csv(field_spec, loader):
    """ Configures the csv value supplier for this field """
    config = dataspec.utils.load_config(field_spec, loader)

    field_name = config.get('column', 1)
    sample = dataspec.utils.is_affirmative('sample', config)
    count_supplier = dataspec.suppliers.count_supplier_from_data(config.get('count', 1))

    csv_data = _load_csv_data(field_spec, config, loader.datadir)
    return CsvSupplier(csv_data, field_name, sample, count_supplier)


def _load_csv_data(field_spec, config, datadir):
    """
    Creates the CsvData object, caches the object by file path so that we can share this object across fields
    :param field_spec: that triggered the creation
    :param config: to use to do the creation
    :param datadir: where to look for data files
    :return: the configured CsvData object
    """
    datafile = config.get('datafile', 'data.csv')
    csv_path = f'{datadir}/{datafile}'
    if csv_path in _csv_data_cache:
        return _csv_data_cache.get(csv_path)

    if not os.path.exists(csv_path):
        raise dataspec.SpecException(f'Unable to locate data file: {datafile} in data dir: {datadir} for spec: '
                            + json.dumps(field_spec))
    delimiter = config.get('delimiter', ',')
    # in case tab came in as string
    if delimiter == '\\t':
        delimiter = '\t'
    quotechar = config.get('quotechar', '"')
    has_headers = dataspec.utils.is_affirmative('headers', config)

    size_in_bytes = os.stat(csv_path).st_size
    if size_in_bytes <= SMALL_ENOUGH_THRESHOLD:
        csv_data = SampleEnabledCsv(csv_path, delimiter, quotechar, has_headers)
    else:
        csv_data = BufferedCsvData(csv_path, delimiter, quotechar, has_headers, _DEFAULT_BUFFER_SIZE)
    _csv_data_cache[csv_path] = csv_data
    return csv_data
