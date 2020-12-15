# -------------------------------------------------------------------------------------
# Libraries
import logging
import os
import re

from datetime import datetime

import numpy as np
import pandas as pd
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read info file in ascii format
def read_file_info(file_name, file_id, file_header=None, file_skip_rows=1,
                    index_name=0, index_group_start=1, index_group_end=10):

    df_data_raw = pd.read_table(file_name, header=file_header, skiprows=file_skip_rows)

    name_list = list(df_data_raw.iloc[:, index_name])
    id_list = [file_id] * name_list.__len__()

    data_tmp = df_data_raw.iloc[:, index_group_start:index_group_end].values

    data_collections = []
    for data_step in data_tmp:

        data_parsed = []
        for data_tmp in data_step:
            if isinstance(data_tmp, str):
                data_str = data_tmp.split(' ')
                for data_char in data_str:
                    data_parsed.append(int(data_char))
            else:
                data_parsed.append(data_tmp)

        data_collections.append(data_parsed)

    dict_data = {}
    for name_step, id_step, data_step in zip(name_list, id_list, data_collections):
        dict_data[name_step] = {}
        dict_data[name_step]['id'] = id_step
        dict_data[name_step]['dataset'] = data_step

    return dict_data
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create file tag
def create_file_tag(section_ts_start, section_ts_end, section_ens, time_format='%Y%m%d%H%M', tag_sep=':'):
    if section_ens is not None:
        section_tag = section_ts_start.strftime(time_format) + '_' + section_ts_end.strftime(time_format) + \
                      tag_sep + section_ens
    else:
        section_tag = section_ts_start.strftime(time_format) + '_' + section_ts_end.strftime(time_format)
    return section_tag
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to parse filename in parts
def parse_file_parts(file_name):

    file_parts = re.findall(r'\d+', file_name)

    if file_parts.__len__() == 3:
        file_part_datetime_start = datetime.strptime(file_parts[0], "%y%j%H%M")
        file_part_datetime_end = datetime.strptime(file_parts[1][:-2], "%y%j%H%M")
        file_part_mask = file_parts[1][-2:]
        file_part_n_ens = file_parts[2]
    elif file_parts.__len__() == 2:
        file_part_datetime_start = datetime.strptime(file_parts[0], "%y%j%H%M")
        file_part_datetime_end = datetime.strptime(file_parts[1][:-2], "%y%j%H%M")
        file_part_mask = file_parts[1][-2:]
        file_part_n_ens = None
    else:
        logging.error(' ===> Parser of filename ' + file_name + ' fails for unknown format')
        raise NotImplementedError('Case not implemented yet')

    file_part_timestamp_start = pd.Timestamp(file_part_datetime_start)
    file_part_timestamp_end = pd.Timestamp(file_part_datetime_end)

    return file_part_timestamp_start, file_part_timestamp_end, file_part_mask, file_part_n_ens
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read hydro file in ascii format
def read_file_hydro(section_name, file_name, column_time_idx=0):

    file_data = pd.read_table(file_name)

    file_cols_tmp = list(file_data.columns)[0].split(' ')
    file_cols_filtered = list(filter(None, file_cols_tmp))

    if section_name in file_cols_filtered:

        column_section_idx = file_cols_filtered.index(section_name)
        file_data_table = list(file_data.values)

        section_period = []
        section_data = []
        for file_data_row in file_data_table:
            file_data_parts = list(file_data_row)[0].split(' ')
            file_data_parts = list(filter(None, file_data_parts))

            section_time = pd.Timestamp(file_data_parts[column_time_idx])
            section_point = float(file_data_parts[column_section_idx])

            section_period.append(section_time)
            section_data.append(section_point)

        section_series = pd.Series(index=section_period, data=section_data)

    else:
        section_series = np.nan

    return section_series

# -------------------------------------------------------------------------------------
