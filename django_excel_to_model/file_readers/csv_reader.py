import io

from django_excel_to_model.field_tools import get_valid_excel_field_name
from django_excel_to_model.reader import ExcelBaseFile


class CsvFile(ExcelBaseFile):
    def __init__(self, full_path):
        self.full_path = full_path
        self.sheet_index = None
        self.title_columns = None
        self.title_column_len = None

    def get_sheet(self, index):
        self.sheet_index = index
        return self

    def get_headers(self, header_index=0):
        header = None
        with io.open(self.full_path, "r", encoding="utf_8_sig", newline='\r\n') as f:
            for idx, line in enumerate(f):
                if idx == header_index:
                    header = line
                    break
        self.title_columns = header.split(';')
        assert self.title_columns is not None
        self.title_column_len = len(self.title_columns)

    def enumerate_mapped(self, mapping, start_row=1):
        with io.open(self.full_path, "r", encoding="utf_8_sig", newline='\r\n') as f:
            it = next(f)
            for line in f:
                yield self.get_mapped_columns(line, mapping)

    def get_mapped_columns(self, line, mapping):

        value_list = line.split(';')
        if len(self.title_columns) != len(value_list):
            raise Exception('Line length is not consistent with header: %s' % line)

        res = {}
        for i in range(self.title_column_len):
            src_key = unicode(self.title_columns[i])
            try:
                mapping_key = mapping[src_key]
            except KeyError:
                mapping_key = mapping[get_valid_excel_field_name(src_key)]
            val = value_list[i]
            res[mapping_key] = val
        return res
