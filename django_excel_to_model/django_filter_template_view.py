from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db.models import Q
from django.views.generic import TemplateView
import django_filters
from django_tables2_reports.tables import TableReport
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor

__author__ = 'weijia'


class DjangoFilterTemplateView(TemplateView):
    template_name = 'django_filter_with_template/filters.html'
    model_class = User
    filter_fields = {"username": ["icontains"]}
    edit_namespace = "admin"

    def __init__(self, **kwargs):
        super(DjangoFilterTemplateView, self).__init__(**kwargs)
        # self.model_class = None
        self.table_to_report = None

    def get_contains_all_keyword_form(self):
        form_class = type(self.model_class.__name__ + "ContainAllKeywordForm", (forms.ModelForm,), {
            "Meta": type("Meta", (), {"model": self.model_class, "fields": []}),
            "keywords": forms.CharField(required=False),
        })
        return form_class

    def render_edit(self):
        return '%d' % next(self.counter)

    def get_table_report_class(self):
        content_type = ContentType.objects.get_for_model(self.model_class)
        table_class = type(self.model_class.__name__ + "AutoTable", (TableReport,), {
            "Meta": type("Meta", (), {"model": self.model_class}),
            # "edit": tables.Column(),
            # "render_edit":
            # "edit": tables.LinkColumn("admin:%s_%s_change" %
            #                           (content_type.app_label, content_type.model), args=[A('pk')])
        })
        return table_class

    def get_filter_class(self):

        filter_class = type(self.model_class.__name__ + "AutoFilter", (django_filters.FilterSet,), {
            "Meta": type("Meta", (),
                         {"model": self.model_class,
                          "form": self.get_contains_all_keyword_form(),
                          # "fields": self.filter_fields
                          })
        })
        return filter_class

    def get_context_data(self, **kwargs):
        context = super(DjangoFilterTemplateView, self).get_context_data(**kwargs)
        keyword_form = self.get_contains_all_keyword_form()(self.request.GET)
        query = Q()
        if keyword_form.is_valid():
            keywords = keyword_form.cleaned_data["keywords"]
            for single_keyword in keywords.split(","):
                queryset = self.model_class.objects.filter(query)
        else:
            queryset = self.model_class.objects.all()

        f = self.get_filter_class()(self.request.GET, queryset=queryset)

        table = self.get_table_report_class()(f.qs)
        # table.paginate(page=request.GET.get('page', 1), per_page=5)
        # RequestConfig(request, paginate={"per_page": 5}).configure(table)
        self.table_to_report = RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        return {"table": table, "filter": f, "admin_base_url": self.get_admin_url()}

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if not (self.table_to_report is None):
            return create_report_http_response(self.table_to_report, self.request)
        return self.render_to_response(context)

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.model_class)
        url_name = "%s:%s_%s_change" % (self.edit_namespace, content_type.app_label, content_type.model)
        return urlresolvers.reverse(url_name, args=("%d",))
