from django_excel_to_model.management.commands.model_create_utils.attribute_generator import ClassAttributeCreator
import django_tables2 as tables


def get_django_tables2_from_dict(data_dict):
    c = ClassAttributeCreator()
    table_meta_class = type("Meta", (), {
        "attrs": {'class': 'table table-striped table-bordered table-advance table-hover'},
        "orderable": False,
    })
    table_attributes = {"Meta": table_meta_class}
    table_data = {}
    for data_key in data_dict.keys():
        attr_name = c.refine_attr_name(data_key)
        table_attributes[attr_name] = tables.Column(verbose_name=data_key)
        table_data[attr_name] = data_dict[data_key]

    item_table_class = type("Item" + "DictTableClass", (tables.Table,), table_attributes)

    return item_table_class([table_data])
