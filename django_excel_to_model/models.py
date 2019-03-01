# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ExcelImportTask(models.Model):
    excel_file = models.FileField(upload_to="data/excel_import_task_files/")
    header_row_numbered_from_1 = models.IntegerField(default=1,  # help_text="Header row number (start from 1)")
                                                     )
    next_process_line_numbered_from_1 = models.IntegerField(default=1)
    spreadsheet_numbered_from_1 = models.IntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    content = models.ForeignKey(ContentType)
