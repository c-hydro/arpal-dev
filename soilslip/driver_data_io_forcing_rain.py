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
from lib_utils_io import read_file_json, read_file_csv, write_file_csv, read_obj, write_obj, create_darray_2d, \
    create_dset, write_dset
from lib_utils_system import fill_tags2string, make_folder
from lib_utils_data import filter_rain_dataframe, interpolate_rain_dataframe
from lib_utils_tiff import save_file_tiff

# Debug
import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverForcing for rain datasets
class DriverForcing:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_step, src_dict, ancillary_dict, dst_dict, tmp_dict=None,
                 alg_ancillary=None, alg_template_tags=None,
                 time_data=None, geo_data_region=None, geo_data_weather_station=None, group_data=None,
                 flag_forcing_data='rain_data',
                 flag_ancillary_data_map='rain_data_map', flag_ancillary_data_point='rain_data_point',
                 flag_ancillary_updating=True):

        self.time_step = pd.Timestamp(time_step)

        self.flag_forcing_data = flag_forcing_data
        self.flag_ancillary_data_map = flag_ancillary_data_map
        self.flag_ancillary_data_point = flag_ancillary_data_point

        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'
        self.region_tag = 'region'

        self.alg_ancillary = alg_ancillary
        self.alg_template_tags = alg_template_tags

        self.geo_data_region = geo_data_region
        self.geo_data_weather_station = geo_data_weather_station

        self.file_data_geo = self.geo_data_region[self.region_tag]
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

        self.file_columns_sep = ';'
        self.file_scale_factor_longitude = 10
        self.file_scale_factor_latitude = 10
        self.file_scale_factor_rain = 1
        self.file_metadata = {'description': 'rain'}
        self.file_epsg_code = 'EPSG:4326'

        self.month_lut = {'01': 'gennaio', '02': 'febbraio', '03': 'marzo', '04': 'aprile', '05': 'maggio',
                          '06': 'giugno', '07': 'luglio', '08': 'agosto', '09': 'settembre', '10': 'ottobre',
                          '11': 'novembre', '12': 'dicembre'}

        self.time_data = time_data[self.flag_forcing_data]
        self.time_range = self.collect_file_time()

        self.file_name_src_raw = src_dict[self.flag_forcing_data][self.file_name_tag]
        self.folder_name_src_raw = src_dict[self.flag_forcing_data][self.folder_name_tag]

        self.file_path_src_list = self.collect_file_list(
            self.folder_name_src_raw, self.file_name_src_raw)

        self.file_name_ancillary_map_raw = ancillary_dict[self.flag_ancillary_data_map][self.file_name_tag]
        self.folder_name_ancillary_map_raw = ancillary_dict[self.flag_ancillary_data_map][self.folder_name_tag]

        self.file_path_ancillary_map_list = self.collect_file_list(
            self.folder_name_ancillary_map_raw, self.file_name_ancillary_map_raw)

        self.file_name_ancillary_point_raw = ancillary_dict[self.flag_ancillary_data_point][self.file_name_tag]
        self.folder_name_ancillary_point_raw = ancillary_dict[self.flag_ancillary_data_point][self.folder_name_tag]

        self.file_path_ancillary_point_list = self.collect_file_list(
            self.folder_name_ancillary_point_raw, self.file_name_ancillary_point_raw)

        self.flag_ancillary_updating = flag_ancillary_updating

        self.tmp_dict = tmp_dict
        self.file_name_tmp_raw = tmp_dict[self.file_name_tag]
        self.folder_name_tmp_raw = tmp_dict[self.folder_name_tag]

        if self.folder_name_tmp_raw is not None:
            self.file_path_tmp_list = self.collect_file_list(
                self.folder_name_tmp_raw, self.file_name_tmp_raw)

            self.folder_tmp = list(set(self.file_path_tmp_list))[0]
        else:
            self.folder_tmp = None

        self.file_path_processed_map = []
        self.file_path_processed_point = []

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

        month_lut = self.month_lut

        file_name_list = []
        for datetime_step in self.time_range:

            datemonth_step = str(datetime_step.month).zfill(2)

            if datemonth_step in list(month_lut.keys()):
                namemonth_step = month_lut[datemonth_step]
            else:
                logging.error(' ===> Month key is not valid to get month name')
                raise IOError('Check your lut and passed month string')

            alg_template_values_step = {
                'month_name': namemonth_step,
                'source_rain_datetime': datetime_step, 'source_rain_sub_path_time': datetime_step,
                'ancillary_rain_datetime': datetime_step, 'ancillary_rain_sub_path_time': datetime_step,
                'destination_rain_datetime': datetime_step, 'destination_rain_sub_path_time': datetime_step}

            folder_name_def = fill_tags2string(
                folder_name_raw, self.alg_template_tags, alg_template_values_step)
            if file_name_raw is not None:
                file_name_def = fill_tags2string(
                    file_name_raw, self.alg_template_tags, alg_template_values_step)
                file_path_def = os.path.join(folder_name_def, file_name_def)
            else:
                file_path_def = folder_name_def

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
            file_dframe = read_file_csv(file_path_src_def, file_header=self.columns_src,
                                        scale_factor_longitude=self.file_scale_factor_longitude,
                                        scale_factor_latitude=self.file_scale_factor_latitude,
                                        scale_factor_data=self.file_scale_factor_rain)
        else:
            file_dframe = None
            logging.warning(' ===> File datasets of rain weather stations is not available.')

        return file_dframe
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize forcing
    def organize_forcing(self, var_name='rain', var_min=0, var_max=None):

        logging.info(' ----> Organize rain forcing ... ')

        geoy_out_1d = self.file_data_geo['south_north'].values
        geox_out_1d = self.file_data_geo['west_east'].values
        mask_out_2d = self.file_data_geo.values

        point_weather_section = self.geo_data_weather_station

        geox_out_2d, geoy_out_2d = np.meshgrid(geox_out_1d, geoy_out_1d)

        for datetime_step, file_path_src, file_path_ancillary_map, file_path_ancillary_point in zip(
                self.time_range, self.file_path_src_list,
                self.file_path_ancillary_map_list, self.file_path_ancillary_point_list):

            logging.info(' -----> TimeStep: ' + str(datetime_step) + ' ... ')

            if self.flag_ancillary_updating:
                if os.path.exists(file_path_ancillary_map):
                    os.remove(file_path_ancillary_map)
                if os.path.exists(file_path_ancillary_point):
                    os.remove(file_path_ancillary_point)

            if not (os.path.exists(file_path_ancillary_map or os.path.exists(file_path_ancillary_point))):

                if os.path.exists(file_path_src):
                    file_dframe = read_file_csv(file_path_src, datetime_step, file_header=self.columns_src,
                                                file_sep=self.file_columns_sep,
                                                scale_factor_longitude=self.file_scale_factor_longitude,
                                                scale_factor_latitude=self.file_scale_factor_latitude,
                                                scale_factor_data=self.file_scale_factor_rain)

                    # Filter data using variable limits (if defined)
                    if var_min is not None:
                        file_dframe = file_dframe[(file_dframe['data'] >= var_min)]
                    if var_max is not None:
                        file_dframe = file_dframe[(file_dframe['data'] <= var_max)]

                    if file_dframe is not None:
                        file_time_src = file_dframe.index.unique()
                    else:
                        file_time_src = None
                else:
                    file_dframe = None
                    file_time_src = None
                    logging.warning(' ===> File datasets of rain weather stations is not available.')

                if (file_time_src is not None) and (file_time_src.__len__() > 1):
                    logging.warning(' ===> Time step selected are greater than 1. Errors could arise in the script')

                if file_dframe is not None:

                    logging.info(' ------> Interpolate points to map datasets ... ')
                    map_out_2d = interpolate_rain_dataframe(file_dframe,
                                                            mask_out_2d, geox_out_2d, geoy_out_2d,
                                                            folder_tmp=self.folder_tmp)
                    logging.info(' ------> Interpolate points to map datasets ... DONE')

                    logging.info(' ------> Save map datasets ... ')
                    folder_name_map, file_name_map = os.path.split(file_path_ancillary_map)
                    make_folder(folder_name_map)

                    if file_path_ancillary_map.endswith('.nc'):

                        dset_out = create_dset(
                            map_out_2d,
                            mask_out_2d, geox_out_2d, geoy_out_2d,
                            var_data_time=datetime_step,
                            var_data_name=var_name,
                            var_geo_name='mask', var_data_attrs=None, var_geo_attrs=None,
                            coord_name_x='longitude', coord_name_y='latitude', coord_name_time='time',
                            dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                            dims_order_2d=None, dims_order_3d=None)

                        write_dset(
                            file_path_ancillary_map,
                            dset_out, dset_mode='w', dset_engine='h5netcdf', dset_compression=0, dset_format='NETCDF4',
                            dim_key_time='time', no_data=-9999.0)

                        logging.info(' ------> Save map datasets ... DONE. [NETCDF]')

                    elif file_path_ancillary_map.endswith('.tiff'):
                        ### error in saving ERROR 1: Only OGC WKT Projections supported for writing to GeoTIFF.  EPSG:4326 not supported.
                        save_file_tiff(file_path_ancillary_map, map_out_2d, geox_out_2d, geoy_out_2d,
                                       file_metadata=self.file_metadata, file_epsg_code=self.file_epsg_code)

                        logging.info(' ------> Save map datasets ... DONE. [GEOTIFF]')

                    else:
                        logging.info(' ------> Save map datasets ... FAILED')
                        logging.error(' ===> Filename format is not allowed')
                        raise NotImplementedError('Format is not implemented yet')

                    self.file_path_processed_map.append(file_path_ancillary_map)

                    logging.info(' ------> Save points datasets ... ')
                    folder_name_point, file_name_point = os.path.split(file_path_ancillary_point)
                    make_folder(folder_name_point)

                    if file_path_ancillary_point.endswith('.csv'):

                        write_file_csv(file_path_ancillary_point, file_dframe)
                        logging.info(' ------> Save points datasets... DONE')

                    else:
                        logging.info(' ------> Save points datasets ... FAILED')
                        logging.error(' ===> Filename format is not allowed')
                        raise NotImplementedError('Format is not implemented yet')

                    self.file_path_processed_point.append(file_path_ancillary_point)

                    logging.info(' -----> TimeStep: ' + str(datetime_step) + ' ... DONE')

                else:
                    logging.info(' -----> TimeStep: ' + str(datetime_step) + ' ... FAILED')
                    logging.warning(' ===> File datasets of rain weather stations is not available.')
            else:
                logging.info(' -----> TimeStep: ' + str(datetime_step) + ' ... PREVIOUSLY DONE')

        logging.info(' ----> Organize rain forcing ... DONE')

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
