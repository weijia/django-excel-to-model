# -*- coding: utf-8 -*-
from datetime import datetime, tzinfo
import pytz
from xlrd import open_workbook, cellname, XL_CELL_DATE, xldate_as_tuple, XL_CELL_NUMBER
from django.utils import timezone

from field_tools import get_valid_excel_field_name


class Excel(object):
    def __init__(self, full_path):
        self.workbook = open_workbook(full_path, formatting_info=True)

    def get_sheet(self, sheet_name):
        return self.workbook.sheet_by_name(sheet_name)

    def get_sheet_from_index(self, index):
        return self.workbook.sheet_by_index(index)

    def read_sheet(self, sheet_name):
        pass


class Sheet(object):
    def __init__(self, workbook, index=0):
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
            try:
                target_key = mapping[src_key]
            except KeyError:
                target_key = mapping[get_valid_excel_field_name(src_key)]
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
            sheet_columns = self.sheet.ncols
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

    def get_header_raw(self, header_row_index=0):
        self.title_columns = self.get_columns(header_row_index)
        return self.title_columns

    def get_headers(self):
        self.get_header_raw()
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


class ExcelFile(object):
    def __init__(self, full_path, formatting_info=True):
        self.workbook = open_workbook(full_path, formatting_info=formatting_info)
        self.formatting_info = formatting_info

    def get_sheet(self, index):
        s = Sheet(self.workbook, index)
        s.disable_formatting_info()
        return s

    def unload_sheet(self, index):
        self.workbook.unload_sheet(index)
