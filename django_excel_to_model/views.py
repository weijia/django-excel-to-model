import tempfile
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from django_excel_to_model.django_app_generator import DjangoAppGenerator
from django_excel_to_model.management.commands.dump_excel_to_mapping import ModelCreator
from forms import ExcelFormatTranslateForm
from libtool.string_tools import class_name_to_low_case


@csrf_exempt
def create_mapping(request):
    form = ExcelFormatTranslateForm(request.POST or None,
                                    request.FILES or None)
    context = {}
    data_start_row = 1

    if form.is_valid():
        import_file = form.cleaned_data['import_file']
        header_row_numbered_from_1 = form.cleaned_data['header_row_numbered_from_1']
        spreadsheet_numbered_from_1 = form.cleaned_data['spreadsheet_numbered_from_1']
        class_name = form.cleaned_data['class_name']
        app_name = class_name_to_low_case(class_name).replace("_", "-")

        # first always write the uploaded file to disk as it may be a
        # memory file or else based on settings upload handlers
        with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
            for chunk in import_file.chunks():
                uploaded_file.write(chunk)
            uploaded_file.close()
            m = ModelCreator(uploaded_file.name, header_row_numbered_from_1-1, spreadsheet_numbered_from_1-1, class_name)
            codes = m.create_mapping_for_excel()
            codes += "\n"  # Add an additional line to model file
            codes += m.create_model(data_start_row)

            context['codes'] = codes

            if form.cleaned_data["is_create_app_now"]:
                g = DjangoAppGenerator(app_name)
                g.create_default_structure()
                g.create_module_file("models.py", codes)

    context['form'] = form
    return render_to_response("excel_reader/excel_mapping_generator.html",
                              context, context_instance=RequestContext(request))
