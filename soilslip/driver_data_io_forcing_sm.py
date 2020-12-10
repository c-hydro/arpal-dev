"""
Class Features

Name:          driver_data_io_forcing_sm
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
from lib_utils_geo import get_file_raster, convert_cn2s
from lib_utils_io import read_file_json, read_file_csv, read_file_binary, \
    read_obj, write_obj, create_darray_2d, create_dset, write_dset, unzip_filename
from lib_utils_system import fill_tags2string, make_folder, change_extension
from lib_utils_tiff import save_file_tiff

# Debug
import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverForcing for soil moisture datasets
class DriverForcing:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_step, src_dict, ancillary_dict, dst_dict,
                 alg_ancillary=None, alg_template_tags=None,
                 time_data=None, basin_data=None, geo_data=None, group_data=None,
                 flag_forcing_data='soil_moisture_data',
                 flag_ancillary_updating=True):

        self.time_step = pd.Timestamp(time_step)

        self.flag_forcing_data = flag_forcing_data
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.alg_template_tags = alg_template_tags

        self.file_data_basin = basin_data
        self.file_data_geo = geo_data

        self.structure_data_group = group_data

        search_period_list = []
        search_type_list = []
        for group_name, group_fields in self.structure_data_group.items():
            period_tmp = get_dict_nested_value(group_fields, ["sm_datasets", "search_period"])
            type_tmp = get_dict_nested_value(group_fields, ["sm_datasets", "search_type"])
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

        self.file_extension_zip = '.gz'
        self.file_extension_unzip = '.bin'

        self.var_name_terrain = 'terrain'
        self.var_name_curve_number = 'cn'
        self.var_name_channels_network = 'channels_network'
        self.var_name_x = 'west_east'
        self.var_name_y = 'south_north'

        self.flag_ancillary_updating = flag_ancillary_updating

        self.file_metadata = {'description': 'soil_moisture'}
        self.file_epsg_code = 'EPSG:4326'

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

        data_group = self.structure_data_group
        data_time = self.time_range

        file_name_obj = {}
        for group_key, group_data in data_group.items():

            file_name_obj[group_key] = {}

            group_basins = group_data['basin']
            for basin_name in group_basins:

                file_name_list = []
                for time_step in data_time:

                    alg_template_values_step = {'source_sm_sub_path_time': time_step,
                                                'source_sm_datetime': time_step,
                                                'ancillary_sm_sub_path_time': time_step,
                                                'ancillary_sm_datetime': time_step,
                                                'basin_name': basin_name,
                                                'alert_area_name': group_key}

                    folder_name_def = fill_tags2string(
                        folder_name_raw, self.alg_template_tags, alg_template_values_step)
                    file_name_def = fill_tags2string(
                        file_name_raw, self.alg_template_tags, alg_template_values_step)
                    file_path_def = os.path.join(folder_name_def, file_name_def)

                    file_name_list.append(file_path_def)

                file_name_obj[group_key][basin_name] = {}
                file_name_obj[group_key][basin_name] = file_name_list

        return file_name_obj

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize forcing
    def organize_forcing(self, var_name='soil_moisture'):

        logging.info(' ----> Organize soil moisture forcing ... ')

        time_range = self.time_range

        file_data_geo = self.file_data_geo
        file_data_basin = self.file_data_basin
        file_path_src_list = self.file_path_src_list
        file_path_ancillary_list = self.file_path_ancillary_list

        for (group_key_basin, group_basin), (group_key_geo, group_geo), group_file, group_ancillary in zip(
                file_data_basin.items(), file_data_geo.items(),
                file_path_src_list.values(), file_path_ancillary_list.values()):

            logging.info(' -----> Alert Area ' + group_key_basin + ' ... ')

            basin_list = list(group_basin.keys())

            geo_mask_ref = group_geo
            geo_x_ref = group_geo['west_east']
            geo_y_ref = group_geo['south_north']

            basin_collections = {}
            file_ancillary_collections = {}

            if basin_list:
                for basin_name in basin_list:

                    logging.info(' ------> BasinName ' + basin_name + ' ... ')

                    file_basin_geo = group_basin[basin_name]
                    file_basin_list = group_file[basin_name]
                    file_ancillary_list = group_ancillary[basin_name]

                    for time_step, file_basin_step, file_ancillary_step in zip(time_range,
                                                                               file_basin_list, file_ancillary_list):

                        logging.info(' -------> TimeStep: ' + str(time_step) + ' ... ')

                        if self.flag_ancillary_updating:
                            if os.path.exists(file_ancillary_step):
                                os.remove(file_ancillary_step)

                        if not os.path.exists(file_ancillary_step):

                            if file_basin_step.endswith(self.file_extension_zip):
                                file_basin_out = change_extension(file_basin_step, self.file_extension_unzip)
                            else:
                                file_basin_out = file_basin_step

                            if os.path.exists(file_basin_step):
                                unzip_filename(file_basin_step, file_basin_out)

                                data_vtot = read_file_binary(
                                    file_basin_out,
                                    data_geo=file_basin_geo[self.var_name_terrain].values)

                                data_vmax = convert_cn2s(
                                    file_basin_geo[self.var_name_curve_number].values,
                                    file_basin_geo[self.var_name_terrain].values)

                                data_sm = data_vtot / data_vmax
                                data_sm[file_basin_geo[self.var_name_channels_network].values == 1] = -1

                                da_sm_base = create_darray_2d(data_sm,
                                                              file_basin_geo[self.var_name_x], file_basin_geo[self.var_name_y],
                                                              coord_name_x='west_east', coord_name_y='south_north',
                                                              dim_name_x='west_east', dim_name_y='south_north')

                                da_sm_interp = da_sm_base.interp(south_north=geo_y_ref, west_east=geo_x_ref, method='nearest')

                                if time_step not in list(basin_collections.keys()):
                                    basin_collections[time_step] = [da_sm_interp]
                                    file_ancillary_collections[time_step] = [file_ancillary_step]
                                else:
                                    data_tmp = basin_collections[time_step]
                                    data_tmp.append(da_sm_interp)
                                    basin_collections[time_step] = data_tmp

                                    file_tmp = file_ancillary_collections[time_step]
                                    file_tmp.append(file_ancillary_step)
                                    file_tmp = list(set(file_tmp))
                                    file_ancillary_collections[time_step] = file_tmp

                                logging.info(' -------> TimeStep: ' + str(time_step) + ' ... DONE')
                            else:
                                logging.info(' -------> TimeStep: ' + str(time_step) + ' ... FAILED')
                                logging.warning(' ==> File: ' + file_basin_step + ' does not exist')

                        else:
                            logging.info(' -------> TimeStep: ' + str(time_step) + ' ... PREVIOUSLY DONE')

                    logging.info(' ------> BasinName ' + basin_name + ' ... DONE')

                logging.info(' -----> Alert Area ' + group_key_basin + ' ... DONE')

            else:
                logging.info(' -----> Alert Area ' + group_key_basin + ' ... SKIPPED')
                logging.warning(' ==> Datasets are not defined')

            logging.info(' -----> Compose grid datasets from basins to alert area domain ... ')
            for (time_step, data_list), file_path_ancillary in zip(
                    basin_collections.items(), file_ancillary_collections.values()):

                logging.info(' ------> TimeStep: ' + str(time_step) + ' ... ')

                if isinstance(file_path_ancillary, list) and file_path_ancillary.__len__() == 1:
                    file_path_ancillary = file_path_ancillary[0]
                else:
                    logging.error(' ===> Soil moisture ancillary file are not correctly defined.')
                    raise IOError('Ancillary file is not unique')

                if self.flag_ancillary_updating:
                    if os.path.exists(file_path_ancillary):
                        os.remove(file_path_ancillary)

                if not os.path.exists(file_path_ancillary):

                    logging.info(' -------> Merge grid datasets ... ')
                    array_merge = np.zeros([geo_mask_ref.values.shape[0] * geo_mask_ref.values.shape[1]])
                    array_merge[:] = np.nan

                    for data_step in data_list:

                        array_values = data_step.values.ravel()
                        idx_finite = np.isfinite(array_values)

                        array_merge[idx_finite] = array_values[idx_finite]

                    grid_merge = np.reshape(array_merge, [geo_mask_ref.values.shape[0], geo_mask_ref.values.shape[1]])
                    idx_choice = np.where(grid_merge == -1)

                    grid_merge[idx_choice[0], idx_choice[1]] = np.nan

                    idx_filter = np.where((geo_mask_ref.values == 1) & (np.isnan(grid_merge)))
                    grid_merge[idx_filter[0], idx_filter[1]] = np.nanmean(grid_merge)
                    grid_merge[(geo_mask_ref.values == 0)] = np.nan

                    grid_merge[idx_choice[0], idx_choice[1]] = np.nan

                    logging.info(' -------> Merge grid datasets ... DONE')

                    logging.info(' -------> Save grid datasets ... ')

                    dset_merge = create_dset(
                        grid_merge,
                        geo_mask_ref.values, geo_x_ref.values, geo_y_ref.values,
                        var_data_time=time_step,
                        var_data_name=var_name,
                        var_geo_name='mask', var_data_attrs=None, var_geo_attrs=None,
                        coord_name_x='longitude', coord_name_y='latitude', coord_name_time='time',
                        dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                        dims_order_2d=None, dims_order_3d=None)

                    folder_name_ancillary, file_name_ancillary = os.path.split(file_path_ancillary)
                    make_folder(folder_name_ancillary)

                    if file_path_ancillary.endswith('.nc'):

                        write_dset(
                            file_path_ancillary,
                            dset_merge, dset_mode='w', dset_engine='h5netcdf', dset_compression=0, dset_format='NETCDF4',
                            dim_key_time='time', no_data=-9999.0)

                        logging.info(' ------> Save grid datasets ... DONE. [NETCDF]')

                    elif file_path_ancillary.endswith('.tiff'):

                        save_file_tiff(file_path_ancillary,
                                       np.flipud(dset_merge[var_name].values),
                                       geo_x_ref.values, np.flipud(geo_y_ref.values),
                                       file_metadata=self.file_metadata, file_epsg_code=self.file_epsg_code)

                        logging.info(' ------> Save grid datasets ... DONE. [GEOTIFF]')

                    else:
                        logging.info(' ------> Save grid datasets ... FAILED')
                        logging.error(' ===> Filename format is not allowed')
                        raise NotImplementedError('Format is not implemented yet')

                    self.file_path_processed.append(file_path_ancillary)

                    logging.info(' -------> Save grid datasets ... DONE')

                    logging.info(' ------> TimeStep: ' + str(time_step) + ' ... DONE')

                else:
                    logging.info(' ------> TimeStep: ' + str(time_step) + ' ... PREVIOUSLY DONE')

            logging.info(' -----> Compose grid datasets from basins to alert area domain ... DONE')

        logging.info(' ----> Organize soil moisture forcing ... DONE')

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
