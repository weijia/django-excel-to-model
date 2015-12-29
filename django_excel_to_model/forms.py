from django.utils.translation import ugettext_lazy as _
from django import forms


class ExcelFormatTranslateForm(forms.Form):
    # title = forms.CharField(max_length=50)
    import_file = forms.FileField(
        label=_('File to import')
    )
    header_row_numbered_from_1 = forms.IntegerField()
