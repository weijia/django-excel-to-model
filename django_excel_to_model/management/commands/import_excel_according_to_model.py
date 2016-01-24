import argparse
import importlib
import os

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django_excel_to_model.reader import ExcelFile
from libtool.inspect_utils import class_enumerator


class DictTranslator(object):
    # noinspection PyMethodMayBeStatic
    def translate(self, item_dict):
        for ignored in ["__invalid"]:
            if ignored in item_dict:
                del item_dict["__invalid"]
        return item_dict


class ExcelFileFromClassImporter(object):
    def __init__(self, class_instance, sheet_numbered_from_1=1):
        super(ExcelFileFromClassImporter, self).__init__()
        self.model_module = importlib.import_module(class_instance.__module__)
        self.class_instance = class_instance
        self.translator = DictTranslator()
        self.sheet_numbered_from_1 = sheet_numbered_from_1

    def import_excel(self, full_path, header_row_numbered_from_1, first_import_row_numbered_from_1=1, count=1000):
        excel_file = ExcelFile(full_path, False)
        filename = os.path.basename(full_path)
        sheet = excel_file.get_sheet(self.sheet_numbered_from_1-1)
        header = sheet.get_header_raw(header_row_numbered_from_1 - 1)
        # for class_instance in class_enumerator(self.model_module):
        #     new_item_class = class_instance
        cnt = 0

        for item_info_dict in sheet.enumerate_mapped(self.model_module.mapping,
                                                     start_row=first_import_row_numbered_from_1 - 1):
            self.translator.translate(item_info_dict)
            item_info_dict["data_import_id"] = filename
            self.class_instance.objects.get_or_create(**item_info_dict)
            cnt += 1
            # If count = 1, when 1 processed, cnt will become 1
            if cnt > count:
                return 0
        return -1


def import_excel_according_to_model(full_path, content_type_id, header_row_numbered_from_1,
                                    first_import_row_numbered_from_1, count=1000):
    content = ContentType.objects.get(pk=content_type_id)
    e = ExcelFileFromClassImporter(content.model_class())
    e.import_excel(full_path, header_row_numbered_from_1, first_import_row_numbered_from_1, count)


class Command(BaseCommand):
    help = 'Import excel according to model info'

    def handle(self, *args, **options):
        parser = argparse.ArgumentParser(description='Import excel file according to model info')

        subparsers = parser.add_subparsers(help='sub-command help')

        # create the parser for the "a" command
        parser_import_excel_according_to_model = subparsers.add_parser(
            'import_excel_according_to_model', help='import_excel_according_to_model help')

        # parser_import_excel_according_to_model.add_argument(
        #     '--content-type-id', type=int, help='content type pk')
        # parser_import_excel_according_to_model.add_argument(
        #     '--start', default=1,
        #     help='start line for importing excel, default=1 (second line)')
        parser_import_excel_according_to_model.add_argument(
            'file-path', nargs=1, help='path of the excel file')
        parser_import_excel_according_to_model.add_argument(
            'content-type-id', nargs=1, help='path of the excel file', type=int)
        parser_import_excel_according_to_model.add_argument(
            'header_row_numbered_from_1', nargs=1, help='header row number (start from 1)', type=int)
        parser_import_excel_according_to_model.add_argument(
            'start', nargs=1, help='path of the excel file', type=int)
        parser_import_excel_according_to_model.add_argument(
            'count', nargs="?", help='process line count', default=[1000], type=int)

        arg_result = parser.parse_args()
        print vars(arg_result)["file-path"][0]
        print vars(arg_result)["content-type-id"][0]
        print vars(arg_result)["start"][0]
        print vars(arg_result)["count"][0]

        file_path = vars(arg_result)["file-path"][0]
        content_type_id = vars(arg_result)["content-type-id"][0]
        header_row_numbered_from_1 = vars(arg_result)["header_row_numbered_from_1"][0]
        first_import_row_numbered_from_1 = vars(arg_result)["start"][0]
        count = vars(arg_result)["count"][0]

        return import_excel_according_to_model(
            file_path, content_type_id, header_row_numbered_from_1, first_import_row_numbered_from_1, count)
