import os
# from excel_reader.openpyxl_reader import ExcelFile

from django.core.management.base import BaseCommand, CommandError

from django_excel_to_model.field_tools import get_valid_field_name, get_target_field_name
from django_excel_to_model.reader import ExcelFile
from libtool.folder_file_processor import FolderFileProcessor


class ModelCreator(object):
    def __init__(self, full_path, header_row_start_from_0=0):
        super(ModelCreator, self).__init__()
        # self.mapping = mapping_dict
        # self.attr_order = attr_order_list
        self.attr_list = []
        self.mapping_dict = {}
        self.model_code_lines = []
        self.invalid_field_name = u"__invalid"
        self.attr_list_code_lines = []
        self.mapping_code_lines = []
        excel_file = ExcelFile(full_path, False)
        self.worksheet = excel_file.get_sheet(0)
        self.header = self.worksheet.get_header_raw(header_row_start_from_0)

    def create_model(self, data_start_row=1):
        code = self.get_mapping_and_attr()
        attr_order = None
        mapping = None
        exec code
        res = [u"", u"", u"from django.db import models", u"from django.utils.translation import ugettext as _",
               u"from excel_reader.len_definitions import TEXT_LENGTH_256, TEXT_LENGTH_128", u"", u"",
               u"class YourClassName(models.Model):"]
        for row_data_dict in self.worksheet.enumerate(data_start_row):
            for key in attr_order:
                if key == "":
                    continue
                field_name = get_valid_field_name(key)
                first_part = u'%s%s = models.CharField(max_length=TEXT_LENGTH_256, help_text=_("""' % \
                             (u" " * 4, mapping[key])
                declaration = first_part + field_name + u'"""), null=True, blank=True)'
                res.append(declaration)
            break
        res.append(u'    data_import_id = models.CharField(max_length=TEXT_LENGTH_128, '
                   u'help_text=_("Id for this import"), null=True, blank=True)')
        self.model_code_lines = res
        return u"\n".join(res)

    def create_mapping(self, target_mapping_name="mapping"):
        self.mapping_code_lines = ["%s = {" % target_mapping_name, ]

        for col in self.header:
            if col == "":
                self.mapping_dict[u""] = self.invalid_field_name
            else:
                field_name = get_valid_field_name(col)
                self.mapping_dict[field_name] = (get_target_field_name(col)).lower()

        for key in self.mapping_dict:
            self.mapping_code_lines.append(u" "*4+'u"""%s""": u"%s",' % (key, self.mapping_dict[key]))

        self.mapping_code_lines.append("}")

    def create_attr_list_code_lines(self):
        self.attr_list_code_lines.append("attr_order = [")
        for col in self.header:
            name = get_valid_field_name(col)
            if not (name in self.attr_list):
                self.attr_list.append(name)
                self.attr_list_code_lines.append('    u"""%s""",' % name)

        self.attr_list_code_lines.append("]")

    def get_mapping_and_attr(self):
        res = self.mapping_code_lines + ["", ""] + self.attr_list_code_lines
        return "\n".join(res)

    def create_mapping_for_excel(self):
        self.create_mapping("mapping")
        self.create_attr_list_code_lines()
        return self.get_mapping_and_attr()


class ExcelFileProcessor(FolderFileProcessor):
    def __init__(self, files_folder=""):
        super(ExcelFileProcessor, self).__init__(files_folder)
        self.has_processed_once = False

    def is_need_process(self, file_path):
        return (not self.has_processed_once) and (not ("~" in file_path))

    def process_file(self, full_path):
        self.has_processed_once = True
        m = ModelCreator(full_path)
        print m.create_mapping_for_excel()
        print m.create_model()


def create_model_and_import_script():
    processor = ExcelFileProcessor(os.sep.join(["data", "dumping_excel_file"]))
    processor.process_files()


class Command(BaseCommand):
    help = 'Create model script from excel'

    def handle(self, *args, **options):
        create_model_and_import_script()
