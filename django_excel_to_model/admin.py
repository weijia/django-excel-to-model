from . import models
from djangoautoconf.auto_conf_admin_tools.admin_register import AdminRegister
factory = AdminRegister()

factory.register_all_model(models)
