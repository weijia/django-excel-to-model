# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcelImportTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('excel_file', models.FileField(upload_to=b'data/excel_import_task_files/')),
                ('header_row_numbered_from_1', models.IntegerField(default=1)),
                ('next_process_line_numbered_from_1', models.IntegerField(default=1)),
                ('spreadsheet_numbered_from_1', models.IntegerField(default=1)),
                ('is_completed', models.BooleanField(default=False)),
                ('content', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
    ]
