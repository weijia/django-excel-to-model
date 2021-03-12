# -*- coding: utf-8 -*-
from datetime import datetime
import pytz
import pyxlsb
from xlrd import open_workbook, XL_CELL_DATE, xldate_as_tuple, XL_CELL_NUMBER
from django.utils import timezone
from django_excel_to_model.file_readers.data_file_base import ExcelBaseFile
from django_excel_to_model.file_readers.data_source_base import DataSourceBase, BaseSheet, RowRandomlyAccessibleSheet
from django_excel_to_model.xlsb_reader import XlsbSheet


class Sheet(RowRandomlyAccessibleSheet):
    def __init__(self, workbook, index=0):
        super(Sheet, self).__init__()
        self.workbook = workbook
        self.sheet = workbook.sheet_by_index(index)
        self.title_columns = None
        self.formatting_info = True

    def disable_formatting_info(self):
        self.formatting_info = False

    def _format_number(self, cell):
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

    def _get_format_info(self, cell):
        print ("cell.xf_index is", cell.xf_index)
        fmt = self.workbook.xf_list[cell.xf_index]
        print ("type(fmt) is", type(fmt))
        print ("fmt.dump():")
        fmt.dump()

    def get_total_rows(self):
        return self.sheet.nrows

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
            final_value = self._format_number(cell)
        else:
            final_value = cell.value
        return final_value

    def print_headers(self):
        self.get_headers()
        for column in self.title_columns:
            print(column)

    def get_row(self, row_index_start_from_0):
        """
        Return row as defined in the interface.
        cell is got from self.sheet.cell(row_index_numbered_from_0, col_index_numbered_from_0)
        :param row_index_start_from_0:
        :return:
        """
        row_data = []
        for col_index in range(self.get_total_columns()):
            row_data.append(self.parse_cell_value(self.sheet.cell(row_index_start_from_0, col_index)))
        return row_data

    def enumerate(self, start_row_numbered_from_0=1):
        for row_index_numbered_from_0 in range(start_row_numbered_from_0, self.get_total_rows()):
            yield self.get_row(row_index_numbered_from_0)

    def get_total_columns(self):
        return self.sheet.ncols


class SheetConfig(object):
    def __init__(self):
        self.__has_header = True

    def has_header(self):
        return self.__has_header


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
