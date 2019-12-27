import os
# from excel_reader.openpyxl_reader import ExcelFile

from django.core.management.base import BaseCommand, CommandError
from django_excel_to_model.field_tools import get_valid_excel_field_name, get_target_field_name
from django_excel_to_model.file_readers.data_source_factory import DataSourceFactory
from django_excel_to_model.reader import ExcelFile, XlsbFile
from ufs_tools.folder_file_processor import FolderFileProcessor
import re
import random


def rename_if_field_name_starts_with_number(model_attribute_name):
    if not (re.match("^[0-9].+", model_attribute_name) is None):
        model_attribute_name = "n" + model_attribute_name
    return model_attribute_name


class ModelCreator(object):
    reserved_keywords = ["type", "class", "for", "in", "while"]
    MAX_RECORD_LENGTH = 64000/4  # for utf8 there will be multiple byte for one char
    MAX_FIELD_NAME_LENGTH = (64-5)

    def __init__(self, full_path, header_row_start_from_0=0, sheet_index_numbered_from_0=0, class_name="YourClass"):
        super(ModelCreator, self).__init__()
        # self.mapping = mapping_dict
        # self.attr_order = attr_order_list
        self.field_num = 0
        self.indents = u" " * 4
        self.attr_list = []
        self.mapping_dict = {}
        self.model_code_lines = []
        self.invalid_field_name = u"__invalid"
        self.attr_list_code_lines = []
        self.mapping_code_lines = []
        self.worksheet = DataSourceFactory(full_path).get_data_source(
            sheet_index_numbered_from_0, header_row_start_from_0)
        self.header = self.worksheet.get_headers()
        self.class_name = class_name
        self.field_len_definition = 256

    def create_model(self, data_start_row=1):
        code = self.get_mapping_and_attr()
        attr_order = None
        mapping = None
        exec code

        res = [u"", u"", u"# @python_2_unicode_compatible",
               u"class %s(models.Model):" % self.class_name]

        for key in attr_order:
            if key == "":
                continue
            help_text = get_valid_excel_field_name(key)

            first_part = u'%s%s = models.CharField(max_length=%s, help_text=_("""' % \
                         (self.indents, mapping[key], self.field_len_definition)
            declaration = first_part + help_text + u'"""), null=True, blank=True, verbose_name="""'+help_text+'""")'
            res.append(declaration)

        res.append(self.indents + u'data_import_id = models.CharField(max_length=TEXT_LENGTH_128, '
                                  u'help_text=_("Id for this import"), null=True, blank=True)')
        res.append(self.indents + u'')
        res.append(self.indents + u'# def __str__(self):')
        res.append(self.indents + u'# ' + self.indents + u'return "%s" % self.name')
        self.model_code_lines = res
        return u"\n".join(res)

    def get_default_field_len_definition(self):
        max_len_for_each_field = int(self.MAX_RECORD_LENGTH / self.field_num)
        if max_len_for_each_field == 0:
            raise Exception("Too many fields")
        max_target_len = 1024
        while (max_target_len & max_len_for_each_field) == 0:
            max_target_len >>= 1
        field_len_definition = u"TEXT_LENGTH_" + str(max_target_len)
        return field_len_definition

    def create_mapping(self, target_mapping_name="mapping"):
        self.mapping_code_lines = ["%s = {" % target_mapping_name, ]

        self.create_field_title_to_attr_name_mapping()

        for key in self.mapping_dict:
            self.mapping_code_lines.append(self.indents + 'u"""%s""": u"%s",' % (key, self.mapping_dict[key]))
            self.field_num += 1

        self.mapping_code_lines.append("}")

        self.field_len_definition = self.get_default_field_len_definition()

    def create_field_title_to_attr_name_mapping(self):
        for col in self.header:
            if col == "":
                self.mapping_dict[u""] = self.invalid_field_name
            else:
                field_title_str = get_valid_excel_field_name(col)
                model_attribute_name = self.get_attribute_name(col)
                self.mapping_dict[field_title_str] = model_attribute_name

    def get_attribute_name(self, col):
        model_attribute_name = get_target_field_name(col).lower()
        model_attribute_name = self.rename_if_field_name_is_keyword(model_attribute_name)
        model_attribute_name = self.trim_if_field_name_too_long(model_attribute_name)
        model_attribute_name = model_attribute_name.strip("_")
        model_attribute_name = self.add_number_suffix_if_duplicated_field_name(model_attribute_name)
        model_attribute_name = rename_if_field_name_starts_with_number(model_attribute_name)
        return model_attribute_name

    def rename_if_field_name_is_keyword(self, model_attribute_name):
        if model_attribute_name in self.reserved_keywords:
            model_attribute_name += "item_"
        return model_attribute_name

    def trim_if_field_name_too_long(self, model_attribute_name):
        if len(model_attribute_name) > self.MAX_FIELD_NAME_LENGTH:
            model_attribute_name = model_attribute_name[0:self.MAX_FIELD_NAME_LENGTH]
        return model_attribute_name

    def add_number_suffix_if_duplicated_field_name(self, model_attribute_name):
        if model_attribute_name in self.mapping_dict:
            model_attribute_name += "_%d" % random.randint(0, 999)
        return model_attribute_name

    def create_attr_list_code_lines(self):
        self.attr_list_code_lines.append("attr_order = [")
        for col in self.header:
            name = get_valid_excel_field_name(unicode(col))
            if not (name in self.attr_list):
                self.attr_list.append(name)
                self.attr_list_code_lines.append(self.indents + 'u"""%s""",' % name)

        self.attr_list_code_lines.append("]")

    def get_mapping_and_attr(self):
        res = [u"from django.db import models",
               u"from django.utils.translation import ugettext as _",
               u"from six import python_2_unicode_compatible",
               u"from djangoautoconf.model_utils.len_definitions import %s, TEXT_LENGTH_128" % self.field_len_definition,
               u"",
               u""]
        res += self.mapping_code_lines + ["", ""]
        res += self.attr_list_code_lines
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
