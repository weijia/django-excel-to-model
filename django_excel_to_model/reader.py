# -*- coding: utf-8 -*-
from datetime import datetime
import pytz
import pyxlsb
from xlrd import open_workbook, XL_CELL_DATE, xldate_as_tuple, XL_CELL_NUMBER
from django.utils import timezone
from django_excel_to_model.field_tools import get_db_field


class ExcelReaderBaseException(Exception):
    pass


class InconsistentLineLength(ExcelReaderBaseException):
    pass


class Excel(object):
    def __init__(self, full_path):
        self.workbook = open_workbook(full_path, formatting_info=True)

    def get_sheet(self, sheet_name):
        return self.workbook.sheet_by_name(sheet_name)

    def get_sheet_from_index(self, index):
        return self.workbook.sheet_by_index(index)

    def read_sheet(self, sheet_name):
        pass


class BaseSheet(object):
    def __init__(self, workbook, index):
        self.workbook = workbook
        self.sheet = None
        self.title_columns = None

    def format_number(self, cell):
        print 'format number'

    def parse_cell_value(self, cell):
        print 'get cell value according to cell type'

    def get_mapped_column(self, row_index, mapping):
        print 'get mapped column'

    def enumerate_mapped(self, mapping, start_row=1):
        print 'enumerate mapped column'

    def init_header_raw(self, header_row_index=0):
        print 'init title column'

    def get_columns(self, row_index):
        print 'get column'


class XlsbSheet(BaseSheet):
    def __init__(self, workbook, index=0):
        self.workbook = workbook
        self.sheet = workbook.get_sheet(index+1)
        self.title_columns = None

    def format_number(self, cell):
        if cell.v == int(cell.v):
            return int(cell.v)
        return cell.v

    def parse_cell_value(self, cell):
        try:
            final_value = int(cell.v)
        except ValueError:
            final_value = cell.v
        return final_value

    def get_mapped_columns(self, row_index, mapping):
        res = {}
        for row in self.sheet.rows(sparse=True):
            for r in row:
                if r.v is not None and r.r== row_index:
                    src_key = unicode(self.title_columns[r.c])
                    target_key = get_db_field(mapping, src_key)
                    cell = r
                    res[target_key] = self.parse_cell_value(cell)
        return res

    def enumerate_mapped(self, mapping, start_row=1):
        for row in self.sheet.rows(sparse=True):
            res = {}
            for r in row:
                if r.v is not None and r.v not in self.title_columns:
                    if r.r % 1000 == 0:
                        print r, r.r
                    src_key = unicode(self.title_columns[r.c])
                    target_key = get_db_field(mapping, src_key)
                    res[target_key] = self.parse_cell_value(r)
            yield res

    def init_header_raw(self, header_row_index=0):
        self.title_columns = self.get_columns(header_row_index)
        return self.title_columns

    def get_columns(self, row_index):
        res = []
        for row in self.sheet.rows(sparse=True):
            for r in row:
                if r.r == row_index and r.v is not None:
                    res.append((str(r.v)))
        return res


class Sheet(BaseSheet):
    def __init__(self, workbook, index = 0):
        self.workbook = workbook
        self.sheet = workbook.sheet_by_index(index)
        self.title_columns = None
        self.formatting_info = True

    def disable_formatting_info(self):
        self.formatting_info = False

    def get_columns(self, row_index):
        res = []
        for col_index in range(self.sheet.ncols):
            # print cellname(row_index, col_index), '-',
            # print self.sheet.cell(row_index, col_index).value
            res.append(self.sheet.cell(row_index, col_index).value)
        return res

    def get_mapped_columns(self, row_index, mapping):
        res = {}
        for col_index in range(self.sheet.ncols):
            # print self.sheet.cell(row_index, col_index).value
            src_key = unicode(self.title_columns[col_index])
            # print "___________________", src_key
            target_key = get_db_field(mapping, src_key)
            cell = self.sheet.cell(row_index, col_index)
            res[target_key] = self.parse_cell_value(cell)
        return res

    def format_number(self, cell):
        if self.formatting_info:
            xf = self.workbook.xf_list[cell.xf_index]
            fmt_key = xf.format_key
            fmt = self.workbook.format_map[fmt_key]
            if fmt.format_key == 0:
                # Its format is General, so no additional fractional part should be displayed
                if cell.value == float(int(cell.value)):
                    return int(cell.value)
        elif cell.value == int(cell.value):
            return int(cell.value)
        return cell.value

    def get_format_info(self, cell):
        print "cell.xf_index is", cell.xf_index
        fmt = self.workbook.xf_list[cell.xf_index]
        print "type(fmt) is", type(fmt)
        print
        print "fmt.dump():"
        fmt.dump()

    def enumerate_raw(self):
        start_row = 1
        for row_index in range(start_row, self.sheet.nrows):
            row_data = []
            for col_index in range(self.sheet.ncols):
                # print self.sheet.cell(row_index, col_index).value
                src_key = unicode(self.title_columns[col_index])
                # print "___________________", src_key
                row_data.append(self.sheet.cell(row_index, col_index))
            yield row_data

    def get_total_rows(self):
        return self.sheet.nrows

    def enumerate_mapped(self, mapping, start_row=1):
        for self.row_index in range(start_row, self.sheet.nrows):
            # sheet_columns = self.sheet.ncols
            if self.row_index % 1000 == 0:
                print self.sheet.nrows, self.row_index
            yield self.get_mapped_columns(self.row_index, mapping)

    def get_current_row_index(self):
        return self.row_index

    def enumerate(self, start_row=1):
        for row_index in range(start_row, self.sheet.nrows):
            sheet_columns = self.sheet.ncols
            print self.sheet.nrows, row_index
            yield self.get_header_to_column_dict(row_index)

    def parse_cell_value(self, cell):
        if cell.ctype == XL_CELL_DATE:
            date_for_cell = xldate_as_tuple(cell.value, 0)
            native_date = datetime(date_for_cell[0], date_for_cell[1], date_for_cell[2], date_for_cell[3],
                                   date_for_cell[4], date_for_cell[5])
            try:
                time_zone_aware = timezone.make_aware(native_date, timezone.get_current_timezone())
            except OverflowError:
                time_zone_aware = native_date.replace(tzinfo=pytz.UTC)
            final_value = time_zone_aware
        elif cell.ctype == XL_CELL_NUMBER:
            # self.get_format_info(cell)
            final_value = self.format_number(cell)
        else:
            final_value = cell.value
        return final_value

    def get_header_to_column_dict(self, row_index):
        res = {}
        for col_index in range(self.sheet.ncols):
            # print self.sheet.cell(row_index, col_index).value
            src_key = unicode(self.title_columns[col_index])
            # print "___________________", src_key
            cell = self.sheet.cell(row_index, col_index)
            res[src_key] = self.parse_cell_value(cell)
        return res

    def init_header_raw(self, header_row_index=0):
        if self.title_columns is None:
            self.title_columns = self.get_columns(header_row_index)
        return self.title_columns

    def get_headers(self):
        self.init_header_raw()
        for column in self.title_columns:
            print column,
        print ""

    def get_title_columns(self):
        return self.title_columns


class SheetConfig(object):
    def __init__(self):
        self.__has_header = True

    def has_header(self):
        return self.__has_header


class ExcelBaseFile(object):
    def __init__(self, full_path):
        raise "Failed to get open workbook"

    def get_sheet(self, index):
        raise "Failed to get sheet"


class ExcelFile(ExcelBaseFile):
    def __init__(self, full_path):
        self.workbook = open_workbook(full_path)

    def get_sheet(self, index):
        s = Sheet(self.workbook, index)
        s.disable_formatting_info()
        return s


class XlsbFile(ExcelBaseFile):
    def __init__(self, full_path):
        self.workbook = pyxlsb.open_workbook(full_path)

    def get_sheet(self, index):
        sheet = XlsbSheet(self.workbook, index)
        return sheet

