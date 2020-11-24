"""
Class Features

Name:          driver_data_io_forcing_rain
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

from lib_utils_generic import get_dict_nested_value, find_maximum_delta, split_time_parts
from lib_utils_io import read_file_json, read_file_csv, read_obj, write_obj, create_darray_2d, create_dset, write_dset
from lib_utils_system import fill_tags2string, make_folder
from lib_analysis_interpolation_point import interp_point2grid

# Debug
import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverForcing for rain datasets
class DriverForcing:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_step, src_dict, ancillary_dict, dst_dict,
                 alg_ancillary=None, alg_template_tags=None,
                 time_data=None, geo_data=None, group_data=None,
                 flag_forcing_data='rain_data',
                 flag_ancillary_updating=True):

        self.time_step = pd.Timestamp(time_step)

        self.flag_forcing_data = flag_forcing_data
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'
        self.region_tag = 'region'

        self.alg_template_tags = alg_template_tags

        self.file_data_geo = geo_data[self.region_tag]
        self.structure_data_group = group_data

        search_period_list = []
        search_type_list = []
        for group_name, group_fields in self.structure_data_group.items():
            period_tmp = get_dict_nested_value(group_fields, ["rain_datasets", "search_period"])
            type_tmp = get_dict_nested_value(group_fields, ["rain_datasets", "search_type"])
            search_period_list.extend(period_tmp)
            search_type_list.extend(type_tmp)
        search_period_list = list(set(search_period_list))
        search_type_list = list(set(search_type_list))

        self.search_delta_max = find_maximum_delta(search_period_list)
        self.search_period_max, self.search_frequency_max = split_time_parts(self.search_delta_max)
        if search_type_list.__len__() > 1:
            logging.error(' ===> SearchType is not unique.')
            raise NotImplementedError('Case not allowed.')
        else:
            self.search_period_type = search_type_list[0]

        self.columns_src = ['code', 'name', 'longitude', 'latitude', 'time', 'data']
        self.column_ancillary = ['name', 'longitude', 'latitude', 'data']

        self.time_data = time_data[self.flag_forcing_data]
        self.time_range = self.collect_file_time()

        self.file_name_src_raw = src_dict[self.flag_forcing_data][self.file_name_tag]
        self.folder_name_src_raw = src_dict[self.flag_forcing_data][self.folder_name_tag]

        self.file_path_src_list = self.collect_file_list(
            self.folder_name_src_raw, self.file_name_src_raw)

        self.file_name_ancillary_raw = ancillary_dict[self.flag_forcing_data][self.file_name_tag]
        self.folder_name_ancillary_raw = ancillary_dict[self.flag_forcing_data][self.folder_name_tag]

        self.file_path_ancillary_list = self.collect_file_list(
            self.folder_name_ancillary_raw, self.file_name_ancillary_raw)

        self.flag_ancillary_updating = flag_ancillary_updating

        self.file_path_processed = []
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect time(s)
    def collect_file_time(self):

        time_period = self.time_data["time_period"]
        time_frequency = self.time_data["time_frequency"]
        time_rounding = self.time_data["time_rounding"]

        if time_period < self.search_period_max:
            logging.warning(' ===> TimePeriod is less then SearchPeriodMax. Set TimePeriod == SearchPeriodMax')
            time_period = self.search_period_max
        if time_frequency != self.search_frequency_max:
            logging.error(' ===> TimeFrequency is not equal to SearchFrequencyMax.')
            raise NotImplementedError('Case not allowed.')

        time_step = self.time_step.floor(time_rounding)
        time_start_left = pd.date_range(start=time_step, periods=2, freq=time_frequency)[1]
        time_end_right = time_step

        search_type = self.search_period_type
        if search_type == 'left':
            time_range = pd.date_range(start=time_start_left, periods=time_period, freq=time_frequency)
        elif search_type == 'right':
            time_range = pd.date_range(end=time_end_right, periods=time_period, freq=time_frequency)
        elif search_type == 'both':
            time_range_left = pd.date_range(start=time_start_left, periods=time_period, freq=time_frequency)
            time_range_right = pd.date_range(end=time_end_right, periods=time_period, freq=time_frequency)
            time_range = time_range_right.union(time_range_left)
        else:
            logging.error(' ===> SearchType selection is wrong')
            raise NotImplementedError('Case not allowed.')

        return time_range
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect ancillary file
    def collect_file_list(self, folder_name_raw, file_name_raw):

        file_name_list = []
        for datetime_step in self.time_range:

            alg_template_values_step = {
                'source_rain_datetime': datetime_step, 'source_rain_sub_path_time': datetime_step,
                'ancillary_rain_datetime': datetime_step, 'ancillary_rain_sub_path_time': datetime_step,
                'destination_rain_datetime': datetime_step, 'destination_rain_sub_path_time': datetime_step}

            folder_name_def = fill_tags2string(
                folder_name_raw, self.alg_template_tags, alg_template_values_step)
            file_name_def = fill_tags2string(
                file_name_raw, self.alg_template_tags, alg_template_values_step)
            file_path_def = os.path.join(folder_name_def, file_name_def)

            file_name_list.append(file_path_def)

        return file_name_list

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get source file
    def get_file_src(self):

        time_step = self.time_step

        alg_template_values_step = {'ancillary_datetime': time_step, 'ancillary_sub_path_time': time_step}

        folder_name_src_def = fill_tags2string(
            self.folder_name_src_raw, self.alg_template_tags, alg_template_values_step)
        file_name_src_def = fill_tags2string(
            self.file_name_src_raw, self.alg_template_tags, alg_template_values_step)

        file_path_src_def = os.path.join(folder_name_src_def, file_name_src_def)
        if os.path.exists(file_path_src_def):
            file_dframe = read_file_csv(file_path_src_def, file_header=self.columns_src)
        else:
            file_dframe = None
            logging.warning(' ===> File datasets of rain weather stations is not available.')

        return file_dframe
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize forcing
    def organize_forcing(self, var_name='rain'):

        logging.info(' ----> Organize rain forcing ... ')

        geoy_out_1d = self.file_data_geo['south_north'].values
        geox_out_1d = self.file_data_geo['west_east'].values
        mask_2d = self.file_data_geo.values

        geox_out_2d, geoy_out_2d = np.meshgrid(geox_out_1d, geoy_out_1d)

        for datetime_step, file_path_src, file_path_ancillary in zip(
                self.time_range, self.file_path_src_list, self.file_path_ancillary_list):

            logging.info(' -----> TimeStep: ' + str(datetime_step) + ' ... ')

            if self.flag_ancillary_updating:
                if os.path.exists(file_path_ancillary):
                    os.remove(file_path_ancillary)

            if not os.path.exists(file_path_ancillary):

                if os.path.exists(file_path_src):
                    file_dframe = read_file_csv(file_path_src, datetime_step, file_header=self.columns_src)
                    if file_dframe is not None:
                        file_time_src = file_dframe.index.unique()
                    else:
                        file_time_src = None
                else:
                    file_dframe = None
                    logging.warning(' ===> File datasets of rain weather stations is not available.')

                if (file_time_src is not None) and (file_time_src.__len__() > 1):
                    logging.warning(' ===> Time step selected are greater than 1. Errors could arise in the script')

                if file_dframe is not None:

                    logging.info(' ------> Interpolate points to grid datasets ... ')

                    geox_in_1d = file_dframe['longitude'].values
                    geoy_in_1d = file_dframe['latitude'].values
                    data_in_1d = file_dframe['data'].values

                    data_out_2d = interp_point2grid(
                        data_in_1d, geox_in_1d, geoy_in_1d, geox_out_2d, geoy_out_2d, epsg_code='4326',
                        interp_no_data=-9999.0, interp_radius_x=0.2, interp_radius_y=0.2,
                        interp_method='idw', var_name_data='values', var_name_geox='x', var_name_geoy='y')

                    data_out_2d[mask_2d == 0] = np.nan

                    logging.info(' ------> Interpolate points to grid datasets ... ')

                    logging.info(' ------> Save grid datasets ... ')
                    dset_out = create_dset(
                        data_out_2d,
                        mask_2d, geox_out_2d, geoy_out_2d,
                        var_data_time=datetime_step,
                        var_data_name=var_name,
                        var_geo_name='mask', var_data_attrs=None, var_geo_attrs=None,
                        coord_name_x='longitude', coord_name_y='latitude', coord_name_time='time',
                        dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                        dims_order_2d=None, dims_order_3d=None)

                    folder_name_dst, file_name_dst = os.path.split(file_path_ancillary)
                    make_folder(folder_name_dst)

                    write_dset(
                        file_path_ancillary,
                        dset_out, dset_mode='w', dset_engine='h5netcdf', dset_compression=0, dset_format='NETCDF4',
                        dim_key_time='time', no_data=-9999.0)

                    self.file_path_processed.append(file_path_ancillary)

                    logging.info(' ------> Save grid datasets ... DONE')

                    logging.info(' -----> TimeStep: ' + str(datetime_step) + ' ... DONE')

                else:
                    logging.info(' -----> TimeStep: ' + str(datetime_step) + ' ... FAILED')
                    logging.warning(' ===> File datasets of rain weather stations is not available.')
            else:
                logging.info(' -----> TimeStep: ' + str(datetime_step) + ' ... PREVIOUSLY DONE')

        logging.info(' ----> Organize rain forcing ... DONE')

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
