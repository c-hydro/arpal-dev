"""
Library Features:

Name:          lib_utils_generic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200515'
Version:       '1.0.0'
"""
#######################################################################################
# Library
import logging
import re
import pandas as pd

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to get nested value
def get_dict_nested_value(input_dict, nested_key):
    internal_dict_value = input_dict
    for k in nested_key:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to split time delta
def split_time_parts(time_delta):
    time_period = re.findall(r'\d+', time_delta)
    if time_period.__len__() > 0:
        time_period = int(time_period[0])
    else:
        time_period = 1
    time_frequency = re.findall("[a-zA-Z]+", time_delta)[0]

    return time_period, time_frequency

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to find maximum delta
def find_maximum_delta(time_delta_list):
    delta_string_max = None
    delta_seconds_max = 0
    for delta_string_step in time_delta_list:

        delta_seconds_step = pd.to_timedelta(delta_string_step).total_seconds()

        if delta_seconds_step > delta_seconds_max:
            delta_seconds_max = delta_seconds_step
            delta_string_max = delta_string_step

    return delta_string_max
# -------------------------------------------------------------------------------------
