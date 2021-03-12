import argparse
import importlib
import os
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from django_excel_to_model.field_tools import get_valid_excel_field_name
from django_excel_to_model.file_readers.csv_reader import CsvFile
from django_excel_to_model.file_readers.data_source_factory import DataSourceFactory
from django_excel_to_model.management.commands.utils.bulk_inserter import BulkInserter
from django_excel_to_model.management.commands.utils.counter import Counter
from django_excel_to_model.models import ExcelImportTask
from django_excel_to_model.reader import ExcelFile, XlsbFile

try:
    from pinax.eventlog.models import log
except ImportError:
    log = None


class MandatoryColumnMissing(Exception):
    pass


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
        self.inserter = BulkInserter(self.class_instance)
        self.mandatory_column_headers = None
        self.is_clean_before_import = False

    def set_clean_before_import(self):
        self.is_clean_before_import = True

    def import_excel(self, full_path, header_row_numbered_from_1=1, first_import_row_numbered_from_1=2, count=1000):
        filename = os.path.basename(full_path)
        data_source = DataSourceFactory(full_path).get_data_source(
            sheet_index_numbered_from_0=self.sheet_numbered_from_1 - 1,
            header_row_start_from_0=header_row_numbered_from_1 - 1)
        count = min(data_source.get_total_rows(), count)
        c = Counter(count)

        self.validate_existence_of_mandatory_columns(data_source)

        if self.is_clean_before_import:
            self.class_instance.objects.all().delete()

        column_to_db_field_mapping = self._get_column_to_db_field_mapping(data_source)

        for item_info_dict in data_source.enumerate_mapped(column_to_db_field_mapping,
                                                           start_row_numbered_from_0=first_import_row_numbered_from_1 - 1):
            # print item_info_dict
            self.translator.translate(item_info_dict)
            item_info_dict["data_import_id"] = filename
            self.inserter.insert(item_info_dict)
            # If count = 1, when 1 processed, cnt will become 0
            c.decrease()
            if c.is_equal_or_below(0):
                self.commit_and_log(filename)
                return 0
        self.commit_and_log(filename)
        return -1

    def _get_column_to_db_field_mapping(self, data_source):
        column_to_db_field_mapping = {}
        for column_name in data_source.get_headers():
            if column_name in self.model_module.mapping:
                column_to_db_field_mapping[column_name] = self.model_module.mapping[column_name]
            else:
                converted_field_name = get_valid_excel_field_name(column_name)
                if converted_field_name in self.model_module.mapping:
                    column_to_db_field_mapping[column_name] = \
                        self.model_module.mapping[converted_field_name]
        return column_to_db_field_mapping

    def validate_existence_of_mandatory_columns(self, sheet):
        if self.mandatory_column_headers is not None:
            if not all(spreadsheet_column_header in sheet.get_headers()
                       for spreadsheet_column_header in self.mandatory_column_headers):
                raise MandatoryColumnMissing()

    def commit_and_log(self, filename):
        self.inserter.commit()
        if log is not None:
            log(
                user=None,
                action=filename,
                extra={
                    "filename": filename
                },
                obj=ContentType.objects.get_for_model(ExcelImportTask)
            )


def import_excel_according_to_model(full_path, content_type_id, header_row_numbered_from_1,
                                    first_import_row_numbered_from_1, count=1000):
    content = ContentType.objects.get(pk=content_type_id)
    e = ExcelFileFromClassImporter(content.model_class())
    e.import_excel(full_path, header_row_numbered_from_1, first_import_row_numbered_from_1, count)


class Command(BaseCommand):
    help = 'Import excel according to model info'

    def add_arguments(self, parser):
        parser.add_argument('file-path')
        parser.add_argument('content-type-id')
        parser.add_argument('header_row_numbered_from_1')
        parser.add_argument('start')
        parser.add_argument('count', nargs='?')

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
            'content-type-id', nargs=1, help='content id of the model', type=int)
        parser_import_excel_according_to_model.add_argument(
            'header_row_numbered_from_1', nargs=1, help='header row number (start from 1)', type=int)
        parser_import_excel_according_to_model.add_argument(
            'start', nargs=1, help='path of the excel file', type=int)
        parser_import_excel_according_to_model.add_argument(
            'count', nargs="?", help='process line count', default=[1000], type=int)

        arg_result = parser.parse_args()
        print(vars(arg_result)["file-path"][0])
        print(vars(arg_result)["content-type-id"][0])
        print(vars(arg_result)["start"][0])
        print(vars(arg_result)["count"])

        file_path = vars(arg_result)["file-path"][0]
        content_type_id = vars(arg_result)["content-type-id"][0]
        header_row_numbered_from_1 = vars(arg_result)["header_row_numbered_from_1"][0]
        first_import_row_numbered_from_1 = vars(arg_result)["start"][0]
        count = vars(arg_result)["count"]

        return import_excel_according_to_model(
            file_path, content_type_id, header_row_numbered_from_1, first_import_row_numbered_from_1, count)
