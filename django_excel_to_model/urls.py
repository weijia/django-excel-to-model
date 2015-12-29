from django.conf.urls import patterns
from views import create_mapping

urlpatterns = patterns('',
                       # (r'^translate/',
                       #  ExcelMappingGeneratorView.as_view(template_name=
                       #                                    'excel_reader/excel_mapping_generator.html')),
                       (r'^$', create_mapping,
                        ),
                       )
