from django_excel_to_model.field_tools import get_db_field


class DataSourceBase(object):

    def __init__(self):
        super(DataSourceBase, self).__init__()
        self._headers = None

    def get_headers(self, row_index_start_from_0=None):
        """
        :param row_index_start_from_0: header row of the data source, start from 0
        :return: list of header column names
        """
        if self._headers:
            return self._headers
        else:
            raise Exception("No header row index given, call set_header_row before calling this function")

    def enumerate(self, start_row_numbered_from_0=1):
        """
        Enumerate rows in data source. Row data will be yield in a list of column values (in unicode)
        :param start_row_numbered_from_0:
        :return: A generator for rows. The format should be as RowRandomlyAccessibleSheet.get_row()
        """
        raise Exception("Not Implemented")

    def enumerate_mapped(self, mapping, start_row_numbered_from_0=1):
        headers = self.get_headers()
        for row in self.enumerate(start_row_numbered_from_0):
            res = {}
            col_index = 0
            for column in row:
                src_key = headers[col_index]
                target_key = get_db_field(mapping, src_key)
                if target_key:
                    res[target_key] = column
                col_index += 1
            yield res

    def get_total_rows(self):
        raise Exception("Not Implemented")


class BaseSheet(DataSourceBase):
    def __init__(self, workbook, index):
        self.workbook = workbook
        self.sheet = None
        self.title_columns = None

    def set_header_row(self, header_row_start_from_0):
        raise Exception("Not Implemented")

    def parse_cell_value(self, cell):
        print ('get cell value according to cell type')


class RowRandomlyAccessibleSheet(DataSourceBase):
    def __init__(self):
        super(RowRandomlyAccessibleSheet, self).__init__()
        self._headers = None
        # self.header_row_start_from_0 = None

    def set_header_row(self, header_row_start_from_0):
        self._headers = []
        for column in self.get_row(header_row_start_from_0):
            self._headers.append(column)

    def get_row(self, row_index_start_from_0):
        """
        :param row_index_start_from_0:
        :return: One row will contain a list of unicode string or int or date.
                E.g. [u"Value for Column1", "Value for Column2", 1, ...]
        """
        raise Exception("Not Implemented")
