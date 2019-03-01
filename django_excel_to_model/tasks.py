import os
import sys
from background_task import background
from models import ExcelImportTask
from django.contrib.auth.models import User


PROCESS_NUMBER_IN_ONE_TURN = 2000


@background(schedule=10)
def import_excel():
    # lookup user by id and send them a message
    # user = User.objects.get(pk=user_id)
    tasks = ExcelImportTask.objects.filter(is_completed=False)
    for task in tasks:
        # mapping_dict = task.content.model_class().__module__.mapping
        # attr_list = task.content.model_class().__module__.attr_list
        full_path = task.excel_file
        # next = task.next_process_line_numbered_from_1
        # task.content.model_class().__module__
        # task.content.pk
        cmd = "%s manage.py import_excel_according_to_model %s %d %d %d %d" % \
              (sys.executable, full_path, task.content.pk, task.header_row_numbered_from_1,
               task.next_process_line_numbered_from_1, PROCESS_NUMBER_IN_ONE_TURN)
        print 'executing: ', cmd
        res = os.system(cmd)
        print "execute result:", res
        if res != 0:
            task.is_completed = True
            # task.next_process_line_numbered_from_1 = 0
        else:
            task.next_process_line_numbered_from_1 += PROCESS_NUMBER_IN_ONE_TURN
            import_excel()
        task.save()

