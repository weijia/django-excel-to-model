from openpyxl import Workbook


class ExcelFile(object):
    def __init__(self, full_path, flag):
        super(ExcelFile, self).__init__()
        self.excel_file = Workbook(guess_types=True)

    def get_sheet(self, index):
        return self

    def get_header_raw(self, index):
        ws = self.excel_file.get_active_sheet()

        for row in ws.iter_rows():
            for cell in row:
                print cell
            break