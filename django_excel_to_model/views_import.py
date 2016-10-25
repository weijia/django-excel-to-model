from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django_excel_to_model.management.commands.import_excel_according_to_model import ExcelFileFromClassImporter
from django_excel_to_model.tasks import import_excel
from forms import ExcelImportTaskForm


__author__ = 'weijia'


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = ExcelImportTaskForm(request.POST, request.FILES)
        if form.is_valid():
            # file is saved
            instance = form.save()
            # return HttpResponseRedirect('/excel_background_importer/')
            instance.next_process_line_numbered_from_1 = instance.header_row_numbered_from_1+1
            instance.save()
            if form.cleaned_data["is_import_now"]:
                if form.cleaned_data["is_clean_before_import"]:
                    instance.content.model_class().objects.all().delete()
                e = ExcelFileFromClassImporter(instance.content.model_class(), instance.spreadsheet_numbered_from_1)
                first_import_row_numbered_from_1 = instance.header_row_numbered_from_1+1
                import_cnt = 999999999
                e.import_excel(instance.excel_file.path, instance.header_row_numbered_from_1,
                               first_import_row_numbered_from_1, import_cnt)
                instance.is_completed = True
                instance.save()
            else:
                import_excel()
    else:
        form = ExcelImportTaskForm()
    return render(request, 'django_excel_to_model/upload.html',
                  {'file_form': form})
