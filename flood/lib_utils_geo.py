# -------------------------------------------------------------------------------------
# Libraries
import logging
import os
import numpy as np

from copy import deepcopy

from lib_utils_io import read_mat
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Geographical lookup table
geo_lookup_table = {'Latdem': 'latitude', 'Londem': 'longitude',
                    'a2dArea': 'cell_area', 'a2dCelle': 'cell_n',
                    'a2dDem': 'altitude', 'a2dQindice': 'discharge_idx',
                    'a2iChoice': 'channel_network', 'a2iPunt': 'flow_directions'}
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read geographical file in mat format
def read_file_geo(file_name):
    file_ws = {}
    file_data = read_mat(file_name)
    for file_key, file_values in file_data.items():
        if file_key in list(geo_lookup_table.keys()):
            var_idx = list(geo_lookup_table.keys()).index(file_key)
            var_name = list(geo_lookup_table.values())[var_idx]
            file_ws[var_name] = file_values

    return file_ws
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read drainage area file in mat format
def read_file_drainage_area(file_name, file_excluded_keys=None):

    if file_excluded_keys is None:
        file_excluded_keys = ['__header__', '__version__', '__globals__', '__function_workspace__',
                              'Lat_dominio_UTM32', 'Lon_dominio_UTM32', 'None']

    file_ws = {}
    file_data = read_mat(file_name)
    for file_key, file_values in file_data.items():
        if file_key not in file_excluded_keys:
            file_ws[file_key] = file_values

    return file_ws
# -------------------------------------------------------------------------------------


"""
def drainage_area(cnet_data, point_idx, cnet_map=None):

    if cnet_map is None:
        cnet_map = [3, 6, 9, 2, 0, 8, 1, 4, 7]

    cnet_data = np.float32(cnet_data)
    cnet_data[cnet_data < 0] = np.nan
    rows_data, cols_data = cnet_data.shape

    cnet_extended = np.pad(cnet_data, pad_width=1, mode='constant', constant_values=np.nan)
    rows_extended, cols_extended = cnet_extended.shape

    arr_tmp = np.zeros([1, 3])
    arr_tmp[0, :] = [-1, 0, 1]
    cnet_i = np.ones([3, 1]) * arr_tmp

    arr_tmp = np.zeros([3, 1])
    arr_tmp[:, 0] = [-1, 0, 1]
    cnet_j = arr_tmp * np.ones([1, 3])

    point_value = np.ravel_multi_index((point_idx[0], point_idx[1]), dims=(rows_extended, cols_extended), order='F')

    point_area = deepcopy(point_value)
    point_range_check = np.zeros([1, 1])
    point_range_check[0, 0] = deepcopy(point_value)

    point_area_old = np.zeros([1, 4])
    point_area_old[0, 0] = point_area
    for i in range(1, point_area_old.shape[1]):
        point_area_old[0, i] = i

    while point_range_check.size > 0:
        point_range_update = []
        for i in range(0, point_range_check.shape[1]):

            point_tmp = np.int(point_range_check[i])
            point_xy = np.unravel_index(point_tmp, dims=(rows_extended, cols_extended), order='F')

            point_idx_bounds = [point_xy[0] + cnet_i, point_xy[1] + cnet_j]

            print('ciao')

    print('ciao')

"""
