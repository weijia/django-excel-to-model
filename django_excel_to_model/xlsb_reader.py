from django_excel_to_model.field_tools import get_db_field
from django_excel_to_model.file_readers.data_source_base import BaseSheet


class XlsbSheet(BaseSheet):
    def __init__(self, workbook, index=0):
        self.workbook = workbook
        self.sheet = workbook.get_sheet(index+1)
        self.title_columns = None

    def set_header_row(self, header_row_start_from_0):
        self.title_columns = self.get_columns(header_row_start_from_0)

    def _format_number(self, cell):
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
        for mapped_data in self.enumerate_mapped(mapping, row_index):
            return mapped_data

    def enumerate_mapped(self, mapping, start_row_numbered_from_0=1):
        for row in self.sheet.rows(sparse=True):
            res = {}
            for cell in row:
                if cell.v is not None and cell.r < start_row_numbered_from_0:
                    break
                if cell.v is not None and cell.v not in self.title_columns:
                    src_key = unicode(self.title_columns[cell.c])
                    target_key = get_db_field(mapping, src_key)
                    if target_key:
                        res[target_key] = self.parse_cell_value(cell)
            yield res

    def get_columns(self, row_index):
        res = []
        for row in self.sheet.rows(sparse=True):
            for r in row:
                if r.r == row_index and r.v is not None:
                    res.append((str(r.v)))
        return res

    def get_total_rows(self):
        return len(self.sheet.rows)

