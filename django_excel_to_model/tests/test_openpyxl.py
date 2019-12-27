#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-excel-to-model
------------

Tests for `django-excel-to-model` models module.
"""

from django.test import TestCase
# from unittest import TestCase

from django_excel_to_model.openpyxl_reader import OpenpyxlExcelFile
from sap_asset_master_data20191224.models import mapping


class TestOpenpyxl(TestCase):

    def setUp(self):
        pass

    def test_something(self):
        x = OpenpyxlExcelFile(r"C:\N-PC0WN7R6-Data\q19420\Downloads\sapItems20191223-1.XLSx")
        s = x.get_sheet(0)
        s.set_header_row(0)
        for i in s.enumerate_mapped(mapping, 2):
            print(i)

    def tearDown(self):
        pass
