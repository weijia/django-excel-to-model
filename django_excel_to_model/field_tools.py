import pinyin


def get_target_field_name(col):
    col = pinyin.get(col, format="strip")
    for ch in [" ", ",", "_", ")", "(", ":", "/", "\\", '"', "'", "-", ",", ".", "<", ">", "%", "&", "\r", "\n"]:
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
        raise "Non-unicode not supported"
    # Only ascii supported here
    return get_string_with_only_char_in_list(col, var_name_char_list + " \t")
    #
    # for ch in [u"'", u'"']:
    #     col = col.replace(ch, u"\\"+ch)
    #
    # # col = col.encode("utf8", errors="ignore")
    # # col = col.decode("utf8")
    # # for ch in [u"\r", u"\n"]:
    # #     col = col.replace(ch, "")
    # # col = col.replace(u"\xa0\xa0", "")
    # # col = unicode(col.encode("ascii", errors="ignore"))
    # return col
