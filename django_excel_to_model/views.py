import tempfile

from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from django_excel_to_model.management.commands.dump_excel_to_mapping import ModelCreator
from forms import ExcelFormatTranslateForm


@csrf_exempt
def create_mapping(request):
    form = ExcelFormatTranslateForm(request.POST or None,
                                    request.FILES or None)
    context = {}
    data_start_row = 1

    if form.is_valid():
        import_file = form.cleaned_data['import_file']
        header_row_numbered_from_1 = form.cleaned_data['header_row_numbered_from_1']

        # first always write the uploaded file to disk as it may be a
        # memory file or else based on settings upload handlers
        with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
            for chunk in import_file.chunks():
                uploaded_file.write(chunk)
            uploaded_file.close()
            m = ModelCreator(uploaded_file.name, header_row_numbered_from_1-1)
            codes = m.create_mapping_for_excel()
            codes += m.create_model(data_start_row)

            context['codes'] = codes

    context['form'] = form
    return render_to_response("excel_reader/excel_mapping_generator.html", context)
