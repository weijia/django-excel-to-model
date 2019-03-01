from django_excel_to_model.field_tools import get_target_field_name
from django_excel_to_model.management.commands.dump_excel_to_mapping import rename_if_field_name_starts_with_number


class ClassAttributeCreator(object):
    reserved_keywords = ["type", "class", "for", "in", "while"]
    MAX_FIELD_NAME_LENGTH = (64-5)

    def rename_if_field_name_is_keyword(self, model_attribute_name):
        if model_attribute_name in self.reserved_keywords:
            model_attribute_name += "item_"
        return model_attribute_name

    def trim_if_field_name_too_long(self, model_attribute_name):
        if len(model_attribute_name) > self.MAX_FIELD_NAME_LENGTH:
            model_attribute_name = model_attribute_name[0:self.MAX_FIELD_NAME_LENGTH]
        return model_attribute_name

    def refine_attr_name(self, attr_name):
        model_attribute_name = get_target_field_name(attr_name).lower()
        model_attribute_name = self.rename_if_field_name_is_keyword(model_attribute_name)
        model_attribute_name = self.trim_if_field_name_too_long(model_attribute_name)
        model_attribute_name = model_attribute_name.strip("_")
        # model_attribute_name = self.add_number_suffix_if_duplicated_field_name(model_attribute_name)
        model_attribute_name = rename_if_field_name_starts_with_number(model_attribute_name)
        return model_attribute_name
