from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django import forms
from models import ExcelImportTask
from django.forms import ModelForm


class ExcelFormatTranslateForm(forms.Form):
    # title = forms.CharField(max_length=50)
    import_file = forms.FileField(
        label=_('File to import')
    )
    header_row_numbered_from_1 = forms.IntegerField()
    spreadsheet_numbered_from_1 = forms.IntegerField()
    class_name = forms.CharField()
    is_create_app_now = forms.BooleanField(required=False)


class ExcelImportTaskForm(ModelForm):
    content = forms.ModelChoiceField(queryset=ContentType.objects.order_by('model'))

    class Meta:
        model = ExcelImportTask
        fields = ['excel_file', 'content', "header_row_numbered_from_1", "spreadsheet_numbered_from_1"]

    is_import_now = forms.BooleanField(required=False)
    is_clean_before_import = forms.BooleanField(required=False)
