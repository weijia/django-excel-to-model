from ufs_tools.short_decorator.ignore_exception import ignore_exc, ignore_exc_with_result

from django_excel_to_model.file_readers.csv_reader import CsvFile
from django_excel_to_model.openpyxl_reader import OpenpyxlExcelFile
from django_excel_to_model.reader import XlsbFile, ExcelFile


class DataSourceFactory(object):
    def __init__(self, full_path):
        """
        :param full_path: full path of the data file
        """
        super(DataSourceFactory, self).__init__()
        self.full_path = full_path

    def get_data_source(self, sheet_index_numbered_from_0, header_row_start_from_0):
        """
        :param sheet_index_numbered_from_0: integer, index of the sheet
        :param header_row_start_from_0:
        :return: DataSourceBase object
        """
        for excel_file_reader in [self.get_xlrd_file,
                                  self.get_openpyxl_file, self.get_xlsb_file]:
            excel_file = excel_file_reader()
            if excel_file:
                sheet = excel_file.get_sheet(sheet_index_numbered_from_0)
                sheet.set_header_row(header_row_start_from_0)
                return sheet

        return CsvFile(self.full_path)

    @ignore_exc_with_result(is_notification_needed=True)
    def get_xlrd_file(self):
        return ExcelFile(self.full_path)

    @ignore_exc_with_result(is_notification_needed=True)
    def get_openpyxl_file(self):
        return OpenpyxlExcelFile(self.full_path)

    @ignore_exc_with_result(is_notification_needed=True)
    def get_xlsb_file(self):
        return XlsbFile(self.full_path)

