from django.conf.urls import url
from django_excel_to_model.views_import import upload_file
from views import create_mapping

urlpatterns = [
    # (r'^translate/',
    #  ExcelMappingGeneratorView.as_view(template_name=
    #                                    'excel_reader/excel_mapping_generator.html')),
    url(r'^$', create_mapping),
    url(r'^upload/', upload_file),
]
