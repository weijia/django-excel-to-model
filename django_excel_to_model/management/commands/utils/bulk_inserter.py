from django_excel_to_model.management.commands.utils.counter import Counter


class BulkInserter(object):
    def __init__(self, model, max_insert_number=5000):
        super(BulkInserter, self).__init__()
        self.max_insert_number = max_insert_number
        self.model = model
        self.count = Counter(max_insert_number, notification_interval=None)
        self.obj_list = []

    def insert(self, obj_dict):
        self.count.decrease()
        self.obj_list.append(self.model(**obj_dict))
        if self.count.is_equal_or_below(0):
            self.commit()
            self.count.reset()

    def commit(self):
        self.model.objects.bulk_create(self.obj_list)
        self.obj_list = []
