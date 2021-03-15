import os

from ufs_tools.app_tools import get_executable_folder
from ufs_tools.folder_tool import ensure_dir


class DjangoAppGenerator(object):
    def __init__(self, app_name):
        super(DjangoAppGenerator, self).__init__()
        self.app_name = app_name
        self.app_module_name = app_name.replace("-", "_")
        self.module_path = None
        self.admin_file_content = '''from . import models
from djangoautoconf.auto_conf_admin_tools.admin_register import AdminRegister
factory = AdminRegister()
factory.register_all_model(models)
'''
        self.urls_content = '''from djangoautoconf.model_utils.url_for_models import add_all_urls
from django.conf.urls import patterns
from . import models

urlpatterns = patterns('',)

add_all_urls(urlpatterns, models)
'''

    def create_default_structure(self):
        repo_root = os.path.abspath(get_executable_folder())
        target_repo_folder = os.path.join(repo_root, "external_app_repos/auto-generated-apps")
        target_app_folder = os.path.join(target_repo_folder, self.app_name)
        ensure_dir(target_repo_folder)
        if os.path.exists(target_app_folder):
            raise "Folder exists"
        else:
            os.mkdir(target_app_folder)
            self.module_path = os.path.join(target_app_folder, self.app_module_name)
            os.mkdir(self.module_path)
            os.mkdir(os.path.join(self.module_path, "migrations"))

            self.create_module_file("admin.py", self.admin_file_content)
            self.create_module_file("urls.py", self.urls_content)
            self.create_module_file("default_settings.py")
            self.create_module_file("__init__.py")
            self.create_module_file("migrations/__init__.py")

    def create_module_file(self, target_file, file_content=""):
        admin_file_path = os.path.join(self.module_path, target_file)
        admin_file = open(admin_file_path, "w")
        admin_file.write(file_content)
        admin_file.close()
