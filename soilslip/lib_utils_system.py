# -------------------------------------------------------------------------------------
# Libraries
import logging
import os

from random import randint
from copy import deepcopy
from datetime import datetime
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to change file extension
def change_extension(file_in, ext_out='bin'):
    file_base, ext_in = os.path.splitext(file_in)
    file_out = ''.join([file_base, ext_out])
    return file_out
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to make folder
def make_folder(path_folder):
    if not os.path.exists(path_folder):
        os.makedirs(path_folder)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to flat list of list
def flat_list(lists):
    return [item for sublist in lists for item in sublist]
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert coupled list to dictionary
def convert_list2dict(list_keys, list_values):
    dictionary = {k: v for k, v in zip(list_keys, list_values)}
    return dictionary
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a random string
def random_string(string_root='temporary', string_separator='_', rand_min=0, rand_max=1000):

    # Generate random number
    rand_n = str(randint(rand_min, rand_max))
    # Generate time now
    time_now = datetime.now().strftime('%Y%m%d-%H%M%S_%f')
    # Concatenate string(s) with defined separator
    rand_string = string_separator.join([string_root, time_now, rand_n])

    return rand_string
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to add format(s) string (path or filename)
def fill_tags2string(string_raw, tags_format=None, tags_filling=None):

    apply_tags = False
    if string_raw is not None:
        for tag in list(tags_format.keys()):
            if tag in string_raw:
                apply_tags = True
                break

    if apply_tags:

        tags_format_tmp = deepcopy(tags_format)
        for tag_key, tag_value in tags_format.items():
            tag_key_tmp = '{' + tag_key + '}'
            if tag_value is not None:
                if tag_key_tmp in string_raw:
                    string_filled = string_raw.replace(tag_key_tmp, tag_value)
                    string_raw = string_filled
                else:
                    tags_format_tmp.pop(tag_key, None)

        dim_max = 1
        for tags_filling_values_tmp in tags_filling.values():
            if isinstance(tags_filling_values_tmp, list):
                dim_tmp = tags_filling_values_tmp.__len__()
                if dim_tmp > dim_max:
                    dim_max = dim_tmp

        string_filled_list = [string_filled] * dim_max

        string_filled_def = []
        for string_id, string_filled_step in enumerate(string_filled_list):
            for tag_format_name, tag_format_value in list(tags_format_tmp.items()):

                if tag_format_name in list(tags_filling.keys()):
                    tag_filling_value = tags_filling[tag_format_name]

                    if isinstance(tag_filling_value, list):
                        tag_filling_step = tag_filling_value[string_id]
                    else:
                        tag_filling_step = tag_filling_value

                    if tag_filling_step is not None:

                        if isinstance(tag_filling_step, datetime):
                            tag_filling_step = tag_filling_step.strftime(tag_format_value)

                        if isinstance(tag_filling_step, (float, int)):
                            tag_filling_step = tag_format_value.format(tag_filling_step)

                        string_filled_step = string_filled_step.replace(tag_format_value, tag_filling_step)

            string_filled_def.append(string_filled_step)

        if dim_max == 1:
            string_filled_out = string_filled_def[0].replace('//', '/')
        else:
            string_filled_out = []
            for string_filled_tmp in string_filled_def:
                string_filled_out.append(string_filled_tmp.replace('//', '/'))

        return string_filled_out
    else:
        return string_raw
# -------------------------------------------------------------------------------------
