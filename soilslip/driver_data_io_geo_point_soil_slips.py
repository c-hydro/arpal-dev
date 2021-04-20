"""
Class Features

Name:          driver_data_io_geo_point_soil_slips
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200515'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os
import numpy as np
import pandas as pd

from pandas.tseries import offsets

from lib_utils_shp import read_file_shp
from lib_utils_geo import get_file_raster
from lib_utils_io import read_file_json, read_obj, write_obj, create_darray_2d #, read_file_shp
from lib_utils_system import fill_tags2string, make_folder

# Debug
# import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverGeo
class DriverGeoPoint:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, src_dict, dst_dict=None, group_data=None, flag_point_data='soil_slip_data',
                 flag_geo_updating=True):

        self.flag_point_data = flag_point_data

        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.structure_group_tag_name = 'name'
        self.structure_group_tag_threshold = 'warning_threshold'
        self.structure_group_tag_index = 'warning_index'

        self.column_db_tag_alert_area = 'ZONA_ALLER'
        self.column_db_tag_time = 'DATA'

        self.structure_group_data = group_data

        self.flag_geo_updating = flag_geo_updating

        self.file_name_src = src_dict[self.flag_point_data][self.file_name_tag]
        self.folder_name_src = src_dict[self.flag_point_data][self.folder_name_tag]
        self.file_path_src = os.path.join(self.folder_name_src, self.file_name_src)

        self.file_name_dst = dst_dict[self.flag_point_data][self.file_name_tag]
        self.folder_name_dst = dst_dict[self.flag_point_data][self.folder_name_tag]
        self.file_path_dst = os.path.join(self.folder_name_dst, self.file_name_dst)

        self.dset_geo_point = self.read_geo_point()

        self.dset_time_point = self.set_time_point()

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set soil slips time file
    def set_time_point(self, time_frequency='D'):

        geo_time_db = pd.DatetimeIndex(self.dset_geo_point[self.column_db_tag_time].values).unique().sort_values()

        time_start = geo_time_db[0] - offsets.YearBegin()
        time_end = geo_time_db[-1] + offsets.YearEnd()

        time_range = pd.date_range(start=time_start, end=time_end, freq=time_frequency)
        time_range = pd.DatetimeIndex(time_range.format(formatter=lambda x: x.strftime('%Y-%m-%d')))

        return time_range
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to read soil slips data file
    def read_geo_point(self):

        if os.path.exists(self.file_path_src):
            point_dframe, point_collections, point_geoms = read_file_shp(self.file_path_src)
        else:
            logging.error(' ==> Soil slip database file is not available')
            raise IOError('File not found!')

        return point_dframe

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize data
    def organize_data(self):

        # Starting info
        logging.info(' ----> Organize soil slips point information ... ')

        geo_point_db = self.dset_geo_point
        time_point_expected = self.dset_time_point
        file_path_dst = self.file_path_dst

        if self.flag_geo_updating:
            if os.path.exists(file_path_dst):
                os.remove(file_path_dst)

        if not os.path.exists(file_path_dst):

            soil_slip_collections = {}
            for group_key, group_data in self.structure_group_data.items():
                group_selection = group_data[self.structure_group_tag_name]
                group_threshold = group_data[self.structure_group_tag_threshold]
                group_index = group_data[self.structure_group_tag_index]

                geo_point_selection = geo_point_db.loc[geo_point_db[self.column_db_tag_alert_area] == group_selection]
                # geo_point_selection = geo_point_selection.reset_index()
                # geo_point_selection = geo_point_selection.set_index(self.column_db_tag_time)

                time_point_selection = pd.DatetimeIndex(geo_point_selection[
                                                            self.column_db_tag_time].values).unique().sort_values()

                soil_slip_n = []
                soil_slip_features = []
                soil_slip_threshold = []
                soil_slip_index = []
                for time_point_step in time_point_selection:

                    time_str_step = time_point_step.strftime('%Y-%m-%d')
                    geo_point_step = geo_point_selection.loc[
                        geo_point_selection[self.column_db_tag_time] == time_str_step]

                    geo_point_threshold = find_category(geo_point_step.shape[0], group_threshold)
                    geo_point_index = find_value(geo_point_threshold, group_index)

                    soil_slip_n.append(geo_point_step.shape[0])
                    soil_slip_features.append(geo_point_step)
                    soil_slip_threshold.append(geo_point_threshold)
                    soil_slip_index.append(geo_point_index)

                data_soilslip = {'event_n': soil_slip_n, 'event_threshold': soil_slip_threshold,
                                 'event_index': soil_slip_index, 'event_features': soil_slip_features}
                dframe_soilslip = pd.DataFrame(data_soilslip, index=time_point_selection)

                soil_slip_collections[group_key] = {}
                soil_slip_collections[group_key] = dframe_soilslip

            # Write soil slips collections to disk
            folder_name_dst, file_name_dst = os.path.split(file_path_dst)
            make_folder(folder_name_dst)
            write_obj(file_path_dst, soil_slip_collections)

            # Ending info
            logging.info(' ----> Organize soil slips point information ... DONE')

        else:

            # Read soil slips collections from disk
            soil_slip_collections = read_obj(file_path_dst)
            logging.info(' ----> Organize soil slips point information ... LOADED. Datasets was previously computed.')

        return soil_slip_collections

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to find value
def find_value(category, value):

    if category in list(value.keys()):
        val = value[category]
    else:
        val = np.nan
    return val
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to find category
def find_category(value, category):

    for cat_key, cat_limits in category.items():
        cat_min = cat_limits[0]
        cat_max = cat_limits[1]
        if (cat_min is not None) and (cat_max is not None):
            if (value >= cat_min) and (value <= cat_max):
                break
        elif cat_min and cat_max is None:
            break
    return cat_key
# -------------------------------------------------------------------------------------
