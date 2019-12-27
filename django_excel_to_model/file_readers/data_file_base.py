

class DataFileBase(object):
    def get_sheet(self, index):
        raise Exception("Not implemented")


class ExcelBaseFile(object):
    def __init__(self, full_path):
        raise Exception("Failed to get open workbook")

    def get_sheet(self, index):
        raise Exception("Failed to get sheet")
