

class SingleInserter(object):

    def __init__(self, model):
        super(SingleInserter, self).__init__()
        self.model = model

    def insert(self, item_info_dict):
        target, is_created = self.model.objects.get_or_create(**item_info_dict)
        if not is_created:
            print "item duplicated:", item_info_dict

    def commit(self):
        pass
