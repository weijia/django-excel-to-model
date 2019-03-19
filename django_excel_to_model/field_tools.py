import pinyin

from django_excel_to_model.file_readers.file_reader_exceptions import NonUnicodeFieldNameNotSupported

SPECIFIC_CHAR_MAPPING = {
    "%" : 'percentage'
}

def get_target_field_name(col):
    for ch in [" ", ",", "_", ")", "(", ":", "/", "\\", '"', "'", "-", ",", ".", "<", ">", "%", "&", "\r", "\n"]:
        if ch in SPECIFIC_CHAR_MAPPING:
            col = col.replace(ch, SPECIFIC_CHAR_MAPPING[ch])
        else:
            col = col.replace(ch, "_").replace("__", "_")
    # col = filter(lambda x: x in string.printable, col)
    col = get_string_with_only_char_in_list(col)
    col = col.replace("__", "_")
    col = col.strip("_")
    if col == "id":
        return "original_id"
    if col == "global":
        return "global_item"
    return col


var_name_char_list = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"


def get_string_with_only_char_in_list(col, char_list=var_name_char_list):
    col = pinyin.get(col, format="strip")
    res = u""
    for ch in col:
        if ch in char_list:
            res += ch
    col = res
    return col


def get_valid_excel_field_name(col):
    """
    This function will not return the exact string!!!!!!
    :param col:
    :return:
    """
    if not (type(col) is unicode):
        raise NonUnicodeFieldNameNotSupported
    # Only ascii supported here
    return get_string_with_only_char_in_list(col, var_name_char_list + " \t")

