if 'INSTALLED_APPS' not in locals()["__builtins__"]:
    INSTALLED_APPS = []

INSTALLED_APPS += (
    'bootstrap3',
    'django_admin_bootstrapped',
    'jquery',
    'pinax.eventlog',  # Not mandatory
    'bootstrapform',
    'django.contrib.staticfiles',
    'django_tables2',
    'background_task',
    'django_tables2_reports',
    'django_excel_to_model',
)

# TEMPLATE_CONTEXT_PROCESSORS += (
#     "django.core.context_processors.request",
#     'django.core.context_processors.static',
# )
