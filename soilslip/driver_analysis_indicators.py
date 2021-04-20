"""
Class Features

Name:          driver_analysis_indicators
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
import xarray as xr

from copy import deepcopy

from lib_utils_generic import get_dict_nested_value, find_maximum_delta, split_time_parts
from lib_utils_system import fill_tags2string, make_folder
from lib_utils_io import read_obj, write_obj, create_dset
from lib_utils_tiff import read_file_tiff

from lib_analysis_interpolation_grid import interp_grid2map

# Debug
import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverAnalysis for indicators
class DriverAnalysis:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_step, ancillary_dict, dst_dict,
                 file_list_rain_map, file_list_rain_point, file_list_sm,
                 alg_ancillary=None, alg_template_tags=None,
                 time_data=None,
                 geo_data_region=None,
                 geo_data_alert_area=None, index_data_alert_area=None,
                 geo_data_weather_station=None,
                 group_data=None,
                 flag_forcing_data_rain='rain_data',
                 flag_ancillary_data_rain_map='rain_data_map', flag_ancillary_data_rain_point='rain_data_point',
                 flag_forcing_data_sm='soil_moisture_data', flag_ancillary_data_sm='soil_moisture_data',
                 flag_indicators_time='time',
                 flag_indicators_event='indicators_event', flag_indicators_data='indicators_data',
                 flag_dest_updating=True):

        self.time_step = pd.Timestamp(time_step)

        self.ancillary_dict = ancillary_dict
        self.dst_dict = dst_dict

        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'
        self.region_tag = 'region'

        self.flag_forcing_data_rain = flag_forcing_data_rain
        self.flag_ancillary_data_rain_map = flag_ancillary_data_rain_map
        self.flag_ancillary_data_rain_point = flag_ancillary_data_rain_point
        self.flag_forcing_data_sm = flag_forcing_data_sm
        self.flag_ancillary_data_sm = flag_ancillary_data_sm

        self.flag_indicators_time = flag_indicators_time
        self.flag_indicators_event = flag_indicators_event
        self.flag_indicators_data = flag_indicators_data

        self.file_list_rain_map = file_list_rain_map
        self.file_list_rain_point = file_list_rain_point
        self.file_list_sm = file_list_sm

        self.geo_data_region = geo_data_region[self.region_tag]
        self.geo_data_alert_area = geo_data_alert_area
        self.index_data_alert_area = index_data_alert_area
        self.geo_data_weather_station = geo_data_weather_station

        self.alg_template_tags = alg_template_tags

        self.time_data_rain = time_data[self.flag_forcing_data_rain]
        self.time_data_sm = time_data[self.flag_forcing_data_sm]

        self.var_name_x = 'west_east'
        self.var_name_y = 'south_north'

        self.structure_data_group = group_data

        self.file_name_ancillary_rain_map_raw = ancillary_dict[self.flag_ancillary_data_rain_map][self.file_name_tag]
        self.folder_name_ancillary_rain_map_raw = ancillary_dict[self.flag_ancillary_data_rain_map][self.folder_name_tag]
        self.file_name_ancillary_rain_point_raw = ancillary_dict[self.flag_ancillary_data_rain_point][self.file_name_tag]
        self.folder_name_ancillary_rain_point_raw = ancillary_dict[self.flag_ancillary_data_rain_point][self.folder_name_tag]
        self.file_name_ancillary_sm_raw = ancillary_dict[self.flag_ancillary_data_sm][self.file_name_tag]
        self.folder_name_ancillary_sm_raw = ancillary_dict[self.flag_ancillary_data_sm][self.folder_name_tag]

        self.file_name_dest_indicators_raw = dst_dict[self.flag_indicators_data][self.file_name_tag]
        self.folder_name_dest_indicators_raw = dst_dict[self.flag_indicators_data][self.folder_name_tag]

        self.flag_dest_updating = flag_dest_updating

        file_path_dest_indicators_expected = []
        for group_data_key in self.structure_data_group.keys():

            file_path_dest_step = collect_file_list(
                time_step, self.folder_name_dest_indicators_raw, self.file_name_dest_indicators_raw,
                self.alg_template_tags, alert_area_name=group_data_key)[0]

            if self.flag_dest_updating:
                if os.path.exists(file_path_dest_step):
                    os.remove(file_path_dest_step)

            file_path_dest_indicators_expected.append(file_path_dest_step)

        self.file_path_dest_indicators_expected = file_path_dest_indicators_expected

        self.template_struct_ts = 'data_time_series'
        self.template_struct_obj = 'data_obj'

        self.template_rain_point_accumulated = 'rain_accumulated_{:}'
        self.template_rain_point_avg = 'rain_average_{:}'
        self.template_rain_point_peak = 'rain_peak_{:}'

        self.template_sm_point_first = 'sm_value_first'
        self.template_sm_point_last = 'sm_value_last'
        self.template_sm_point_max = 'sm_value_max'
        self.template_sm_point_avg = 'sm_value_avg'

        self.analysis_event_undefined = {'event_n': 0, 'event_threshold': 'white', 'event_index': 0}

        self.tag_sep = ':'
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to dump analysis
    def save_analysis(self, group_analysis_sm, group_analysis_rain_map, group_analysis_rain_point, group_soilslip):

        logging.info(' ----> Save analysis [' + str(self.time_step) + '] ... ')

        time_step = self.time_step
        geo_data_alert_area = self.geo_data_alert_area
        group_data_alert_area = self.structure_data_group

        for (group_data_key, group_data_items), geo_data_dframe in zip(group_data_alert_area.items(),
                                                                       geo_data_alert_area.values()):

            logging.info(' -----> Alert Area ' + group_data_key + '  ... ')

            file_path_dest = collect_file_list(
                time_step, self.folder_name_dest_indicators_raw, self.file_name_dest_indicators_raw,
                self.alg_template_tags, alert_area_name=group_data_key)[0]

            if not os.path.exists(file_path_dest):

                group_soilslip_select = group_soilslip[group_data_key]

                if group_analysis_sm[group_data_key] is not None:
                    group_analysis_sm_select = group_analysis_sm[group_data_key][self.template_struct_obj]
                else:
                    group_analysis_sm_select = None
                if group_analysis_rain_map[group_data_key] is not None:
                    group_analysis_rain_map_select = group_analysis_rain_map[group_data_key][self.template_struct_obj]
                else:
                    group_analysis_rain_map_select = None
                if group_analysis_rain_point[group_data_key] is not None:
                    group_analysis_rain_point_select = group_analysis_rain_point[group_data_key]
                else:
                    group_analysis_rain_point_select = None

                if group_analysis_sm_select is not None:
                    if time_step in list(group_soilslip_select.index):
                        soilslip_select = group_soilslip_select.loc[time_step.strftime('%Y-%m-%d 00:00:00')]
                    else:
                        soilslip_select = None
                else:
                    soilslip_select = None

                if (group_analysis_sm_select is not None) and (
                        (group_analysis_rain_map_select is not None) and (group_analysis_rain_point_select is not None)):
                    analysis_sm = self.unpack_analysis(group_analysis_sm_select)
                    analysis_rain_map = self.unpack_analysis(group_analysis_rain_map_select)
                    analysis_rain_point = self.unpack_analysis(group_analysis_rain_point_select)
                    analysis_data = {**analysis_sm, **analysis_rain_map, **analysis_rain_point}
                else:
                    analysis_data = None
                    if (group_analysis_sm_select is None) and (
                            (group_analysis_rain_map_select is not None) and (group_analysis_rain_point_select is not None)):
                        logging.warning(' ===> SoilMoisture datasets is undefined')
                    elif (group_analysis_rain_map_select is None) and (group_analysis_sm_select is not None):
                        logging.warning(' ===> Rain map datasets is undefined')
                    elif (group_analysis_rain_point_select is None) and (group_analysis_sm_select is not None):
                        logging.warning(' ===> Rain point datasets is undefined')
                    else:
                        logging.warning(' ===> Rain and SoilMoisture datasets are undefined')

                if soilslip_select is not None:
                    analysis_event = self.unpack_analysis(soilslip_select,
                                                          ['event_n', 'event_threshold', 'event_index'])
                else:
                    analysis_event = self.analysis_event_undefined
                    logging.warning(' ===> SoilSlip datasets is null. No events reported')

                if (analysis_data is not None) and (analysis_event is not None):

                    analysis_obj = {self.flag_indicators_time: time_step,
                                    self.flag_indicators_data: analysis_data,
                                    self.flag_indicators_event: analysis_event}

                    folder_name_dest, file_name_dest = os.path.split(file_path_dest)
                    make_folder(folder_name_dest)

                    write_obj(file_path_dest, analysis_obj)

                    logging.info(' -----> Alert Area ' + group_data_key + ' ... DONE')

                else:

                    logging.info(' -----> Alert Area ' + group_data_key + ' ... SKIPPED. Some datasets are undefined')

            else:
                logging.info(' -----> Alert Area ' + group_data_key + ' ... SKIPPED. Analysis file created previously')

        logging.info(' ----> Save analysis [' + str(self.time_step) + '] ... DONE')
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to unpack analysis in dictionary format
    @staticmethod
    def unpack_analysis(data_obj, data_keys=None):

        data_dict = {}
        if data_keys is None:
            if isinstance(data_obj, pd.Series):
                data_keys = list(data_obj.index)
                create_dict = True
            elif isinstance(data_obj, dict):
                create_dict = False
            else:
                logging.error(' ===> DataType not allowed in case of keys are null')
                raise NotImplementedError('Case not implemented yet')
        elif data_keys is not None:
            if isinstance(data_obj, pd.Series):
                create_dict = True
            else:
                logging.error(' ===> DataType not allowed in case of keys are not null')
                raise NotImplementedError('Case not implemented yet')
        else:
            logging.error(' ===> Columns format not allowed')
            raise NotImplementedError('Case not implemented yet')

        if create_dict:
            for key in data_keys:
                values = data_obj[key]
                data_dict[key] = values
        else:
            data_dict = data_obj

        return data_dict

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize analysis for soil moisture datasets
    def organize_analysis_sm(self, var_name='soil_moisture'):

        logging.info(' ----> Compute soil moisture analysis [' + str(self.time_step) + '] ... ')

        time_step = self.time_step
        geo_data_alert_area = self.geo_data_alert_area
        group_data_alert_area = self.structure_data_group

        group_analysis = {}
        for (group_data_key, group_data_items), geo_data_dframe in zip(group_data_alert_area.items(),
                                                                       geo_data_alert_area.values()):

            logging.info(' -----> Alert Area ' + group_data_key + '  ... ')

            geoy_out_1d = geo_data_dframe['south_north'].values
            geox_out_1d = geo_data_dframe['west_east'].values
            mask_2d = geo_data_dframe.values

            geox_out_2d, geoy_out_2d = np.meshgrid(geox_out_1d, geoy_out_1d)

            time_delta_max = find_maximum_delta(group_data_items['sm_datasets']['search_period'])
            time_period_type = group_data_items['sm_datasets']['search_type'][0]
            time_period_max, time_frequency_max = split_time_parts(time_delta_max)

            time_range = self.compute_time_range(time_step, time_period_max, time_period_type, time_frequency_max)

            file_list = collect_file_list(
                time_range, self.folder_name_ancillary_sm_raw, self.file_name_ancillary_sm_raw,
                self.alg_template_tags, alert_area_name=group_data_key)

            file_path_dest = collect_file_list(
                time_step, self.folder_name_dest_indicators_raw, self.file_name_dest_indicators_raw,
                self.alg_template_tags, alert_area_name=group_data_key)[0]

            if not os.path.exists(file_path_dest):

                file_list_check = []
                time_range_check = []
                for file_step, timestamp_step in zip(file_list, time_range):
                    if os.path.exists(file_step):
                        file_list_check.append(file_step)
                        time_range_check.append(timestamp_step)
                file_analysis = False
                if file_list_check.__len__() >= 1:
                    file_analysis = True

                if file_analysis:

                    analysis_collections = {}
                    if file_list_check[0].endswith('.nc'):
                        file_data_raw = xr.open_mfdataset(file_list_check, combine='by_coords')
                    elif file_list_check[0].endswith('.tiff'):

                        if file_list_check.__len__() == 1:
                            data_2d, proj, geotrans = read_file_tiff(file_list_check[0])
                            file_data_raw = create_dset(
                                data_2d, mask_2d, geox_out_2d, geoy_out_2d,
                                var_data_time=time_step, var_data_name=var_name,
                                var_geo_name='mask', var_data_attrs=None, var_geo_attrs=None,
                                coord_name_x='longitude', coord_name_y='latitude', coord_name_time='time',
                                dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                                dims_order_2d=None, dims_order_3d=None)

                        elif file_list.__len__() > 1:

                            data_3d = np.zeros(shape=[geox_out_2d.shape[0], geoy_out_2d.shape[1], file_list_check.__len__()])
                            data_3d[:, :, :] = np.nan
                            data_time = []
                            for file_id, (file_step, timestamp_step) in enumerate(zip(file_list_check, time_range_check)):
                                data_2d, proj, geotrans = read_file_tiff(file_step)
                                data_3d[:, :, file_id] = data_2d
                                data_time.append(timestamp_step)

                            file_data_raw = create_dset(
                                data_3d, mask_2d, geox_out_2d, geoy_out_2d,
                                var_data_time=data_time, var_data_name=var_name,
                                var_geo_name='mask', var_data_attrs=None, var_geo_attrs=None,
                                coord_name_x='longitude', coord_name_y='latitude', coord_name_time='time',
                                dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                                dims_order_2d=None, dims_order_3d=None)

                        else:
                            logging.error(' ===> Length of file list is not allowed')
                            raise NotImplementedError('Case is not implemented yet')

                    else:
                        logging.error(' ===> Filename format is not allowed')
                        raise NotImplementedError('Format is not implemented yet')

                    file_data_mean = file_data_raw[var_name].mean(dim=['south_north', 'west_east'])

                    file_time = list(file_data_raw.time.values)
                    file_values_mean = file_data_mean.values

                    file_ts = pd.DatetimeIndex(file_time)

                    if file_ts.shape[0] == 1:
                        file_ts = [file_ts]
                        file_values_mean = [file_values_mean]

                    # Soil moisture average time-series
                    analysis_df = pd.DataFrame(index=file_ts, data=file_values_mean,
                                               columns=[self.template_struct_ts]).fillna(value=pd.NA)

                    analysis_collections[self.template_struct_ts] = {}
                    analysis_collections[self.template_struct_ts] = analysis_df

                    # Soil moisture first value in tne selected period
                    tag_sm_point_first = self.template_sm_point_first
                    file_time_first = pd.Timestamp(file_time[0]).strftime('%Y%m%d_%H%M')
                    file_value_first = float(file_values_mean[0])
                    tag_sm_point_first = tag_sm_point_first.format(file_time_first)

                    # Soil moisture last value in tne selected period
                    tag_sm_point_last = self.template_sm_point_last
                    file_time_last = pd.Timestamp(file_time[-1]).strftime('%Y%m%d_%H%M')
                    file_value_last = float(file_values_mean[-1])
                    tag_sm_point_last = tag_sm_point_last.format(file_time_last)

                    # Soil moisture average in tne selected period
                    tag_sm_point_avg = self.template_sm_point_avg
                    file_value_avg = float(analysis_df[self.template_struct_ts].mean())

                    # Soil moisture maximum in tne selected period
                    tag_sm_point_max = self.template_sm_point_max
                    file_value_max = float(analysis_df[self.template_struct_ts].max())

                    #analysis_ts = analysis_df.max()

                    analysis_collections[self.template_struct_obj] = {}
                    analysis_collections[self.template_struct_obj][tag_sm_point_first] = file_value_first
                    analysis_collections[self.template_struct_obj][tag_sm_point_last] = file_value_last
                    analysis_collections[self.template_struct_obj][tag_sm_point_avg] = file_value_avg
                    analysis_collections[self.template_struct_obj][tag_sm_point_max] = file_value_max

                    logging.info(' -----> Alert Area ' + group_data_key + ' ... DONE')

                else:
                    analysis_collections = None
                    logging.warning(' ===> Soil moisture data are not available')
                    logging.info(' -----> Alert Area ' + group_data_key + ' ... SKIPPED. Datasets are not available.')

                group_analysis[group_data_key] = analysis_collections

            else:

                logging.info(' -----> Alert Area ' + group_data_key + ' ... SKIPPED. Analysis file created previously')

        logging.info(' ----> Compute soil moisture analysis [' + str(self.time_step) + '] ... DONE')

        return group_analysis

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define time range
    @staticmethod
    def compute_time_range(time, time_period_lenght=1, time_period_type='both', time_frequency='H'):

        time_start_left = pd.date_range(start=time, periods=2, freq=time_frequency)[1]
        time_end_right = time

        if time_period_type == 'left':
            time_range = pd.date_range(start=time_start_left, periods=time_period_lenght, freq=time_frequency)
        elif time_period_type == 'right':
            time_range = pd.date_range(end=time_end_right, periods=time_period_lenght, freq=time_frequency)
        elif time_period_type == 'both':
            time_range_left = pd.date_range(start=time_start_left, periods=time_period_lenght, freq=time_frequency)
            time_range_right = pd.date_range(end=time_end_right, periods=time_period_lenght, freq=time_frequency)
            time_range = time_range_right.union(time_range_left)
        else:
            logging.error(' ===> Bad definition for time_period_type')
            raise NotImplementedError('Case not allowed.')

        return time_range

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize analysis for rain map datasets
    def organize_analysis_rain_map(self, var_name='rain'):

        logging.info(' ----> Compute rain analysis map [' + str(self.time_step) + '] ... ')

        time_step = self.time_step
        geo_data_region = self.geo_data_region
        geo_data_alert_area = self.geo_data_alert_area
        index_data_alert_area = self.index_data_alert_area
        group_data_alert_area = self.structure_data_group

        geoy_region_1d = geo_data_region['south_north'].values
        geox_region_1d = geo_data_region['west_east'].values
        mask_region_2d = geo_data_region.values
        geox_region_2d, geoy_region_2d = np.meshgrid(geox_region_1d, geoy_region_1d)

        group_analysis = {}
        for (group_data_key, group_data_items), geo_data_dframe in zip(group_data_alert_area.items(),
                                                                       geo_data_alert_area.values()):

            logging.info(' -----> Alert Area ' + group_data_key + '  ... ')

            file_path_dest = collect_file_list(
                time_step, self.folder_name_dest_indicators_raw, self.file_name_dest_indicators_raw,
                self.alg_template_tags, alert_area_name=group_data_key)[0]

            # Get index interpolated data between region and alert area domains
            if group_data_key in list(index_data_alert_area.keys()):
                index_data = index_data_alert_area[group_data_key]
            else:
                index_data = None

            if not os.path.exists(file_path_dest):

                geoy_out_1d = geo_data_dframe['south_north'].values
                geox_out_1d = geo_data_dframe['west_east'].values

                # Get subdomain mask, longitudes and latitudes
                mask_out_2d = geo_data_dframe.values
                geox_out_2d, geoy_out_2d = np.meshgrid(geox_out_1d, geoy_out_1d)

                time_delta_max = find_maximum_delta(group_data_items['rain_datasets']['search_period'])
                time_period_type = group_data_items['rain_datasets']['search_type'][0]
                time_period_max, time_frequency_max = split_time_parts(time_delta_max)

                time_range = self.compute_time_range(time_step, time_period_max, time_period_type, time_frequency_max)

                file_list = collect_file_list(
                    time_range, self.folder_name_ancillary_rain_map_raw, self.file_name_ancillary_rain_map_raw,
                    self.alg_template_tags)

                file_analysis = True
                for file_step in file_list:
                    if not os.path.exists(file_step):
                        logging.warning(' ===> Filename ' + file_step + ' does not exist')
                        file_analysis = False
                        break

                if file_analysis:

                    if file_list[0].endswith('.nc'):
                        file_obj = xr.open_mfdataset(file_list, combine='by_coords')
                    elif file_list[0].endswith('.tiff'):

                        if file_list.__len__() > 1:

                            data_out_3d = np.zeros(shape=[geox_out_2d.shape[0], geoy_out_2d.shape[1], file_list.__len__()])
                            data_out_3d[:, :, :] = np.nan
                            data_time = []
                            for file_id, (file_step, timestamp_step) in enumerate(zip(file_list, time_range)):
                                data_out_2d, proj, geotrans = read_file_tiff(file_step)

                                # Grid datasets over subdomain mask
                                values_out_interp = interp_grid2map(geox_region_2d, geoy_region_2d,
                                                                    data_out_2d.values,
                                                                    geox_out_2d, geoy_out_2d,
                                                                    index_out=index_data)
                                values_out_interp[mask_out_2d == 0] = np.nan

                                data_out_3d[:, :, file_id] = values_out_interp
                                data_time.append(timestamp_step)

                            file_obj = create_dset(
                                data_out_3d, mask_out_2d, geox_out_2d, geoy_out_2d,
                                var_data_time=data_time, var_data_name=var_name,
                                var_geo_name='mask', var_data_attrs=None, var_geo_attrs=None,
                                coord_name_x='longitude', coord_name_y='latitude', coord_name_time='time',
                                dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                                dims_order_2d=None, dims_order_3d=None)

                        else:
                            logging.error(' ===> Length of file list is not allowed')
                            raise NotImplementedError('Case is not implemented yet')

                    else:
                        logging.error(' ===> Filename format is not allowed')
                        raise NotImplementedError('Format is not implemented yet')

                    values_mean = file_obj[var_name].mean(dim=['south_north', 'west_east']).values

                    analysis_df = pd.DataFrame(index=time_range, data=values_mean,
                                               columns=[self.template_struct_ts]).fillna(value=pd.NA)

                    analysis_obj = {}
                    for time_interval_value in group_data_items['rain_datasets']['search_period']:
                        logging.info(' ------> Compute sum and avg values for ' + time_interval_value + ' ... ')

                        time_period, time_frequency = split_time_parts(time_interval_value)

                        tag_rain_accumulated = self.template_rain_point_accumulated.format(time_interval_value)
                        # resample_df_sum = analysis_df[var_name].rolling(time_interval_value, min_periods=time_period).sum()
                        resample_df_sum = analysis_df[self.template_struct_ts].resample(
                            time_interval_value, label='right').sum()[:-1]
                        analysis_df[tag_rain_accumulated] = resample_df_sum

                        tag_rain_avg = self.template_rain_point_avg.format(time_interval_value)
                        # resample_df_avg = analysis_df[var_name].rolling(time_interval_value, min_periods=time_period).mean()
                        resample_df_avg = analysis_df[self.template_struct_ts].resample(
                            time_interval_value, label='right').mean()[:-1]
                        analysis_df[tag_rain_avg] = resample_df_avg

                        analysis_obj[tag_rain_accumulated] = float(resample_df_sum.max())
                        analysis_obj[tag_rain_avg] = float(resample_df_avg.max())

                        logging.info(' ------> Compute sum and avg values for ' + time_interval_value + ' ... DONE')

                    analysis_collections = {self.template_struct_ts: analysis_df, self.template_struct_obj: analysis_obj}

                    logging.info(' -----> Alert Area ' + group_data_key + ' ... DONE')

                else:
                    analysis_collections = None
                    logging.warning(' ===> Rain data are not available')
                    logging.info(' -----> Alert Area ' + group_data_key + ' ... SKIPPED. Datasets are not available.')

                group_analysis[group_data_key] = analysis_collections

            else:

                logging.info(' -----> Alert Area ' + group_data_key + ' ... SKIPPED. Analysis file created previously')

        logging.info(' ----> Compute rain analysis map [' + str(self.time_step) + '] ... DONE')

        return group_analysis

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize analysis for rain map datasets
    def organize_analysis_rain_point(self, var_name='rain'):

        logging.info(' ----> Compute rain analysis point [' + str(self.time_step) + '] ... ')

        time_step = self.time_step

        group_data_alert_area = self.structure_data_group
        geo_data_weather_station = self.geo_data_weather_station

        group_analysis = {}
        for (group_data_key, group_data_items), geo_data_obj in zip(group_data_alert_area.items(),
                                                                    geo_data_weather_station.values()):

            logging.info(' -----> Alert Area ' + group_data_key + '  ... ')

            file_path_dest = collect_file_list(
                time_step, self.folder_name_dest_indicators_raw, self.file_name_dest_indicators_raw,
                self.alg_template_tags, alert_area_name=group_data_key)[0]

            if not os.path.exists(file_path_dest):

                # Point located in the selected area
                points_code_aa = list(geo_data_obj.keys())

                # Points located both in the selected area and in neighbours areas
                points_code_extended = []
                for point_code_ref, point_code_df in geo_data_obj.items():
                    point_code_tmp = point_code_df['code'].values
                    points_code_extended.extend(point_code_tmp)
                points_code_extended = list(set(points_code_extended))

                if set(points_code_aa) != set(points_code_extended):
                    logging.info(' ------> Some points are located in the neighbours areas')

                time_delta_max = find_maximum_delta(group_data_items['rain_datasets']['search_period'])
                time_period_type = group_data_items['rain_datasets']['search_type'][0]
                time_period_max, time_frequency_max = split_time_parts(time_delta_max)

                time_range = self.compute_time_range(time_step, time_period_max, time_period_type, time_frequency_max)

                file_list = collect_file_list(
                    time_range, self.folder_name_ancillary_rain_point_raw, self.file_name_ancillary_rain_point_raw,
                    self.alg_template_tags)

                file_analysis = True
                for file_step in file_list:
                    if not os.path.exists(file_step):
                        logging.warning(' ===> Filename ' + file_step + ' does not exist')
                        file_analysis = False
                        break

                if file_analysis:

                    if file_list[0].endswith('.csv'):

                        if file_list.__len__() > 1:

                            point_collections = None
                            point_time = []
                            for file_id, (file_step, timestamp_step) in enumerate(zip(file_list, time_range)):

                                logging.info(' ------> Timestep ' + str(timestamp_step) + ' ... ')

                                point_obj_raw = pd.read_csv(file_step)

                                point_obj_timestamp = pd.Timestamp(list(set(point_obj_raw['time'].values))[0])

                                point_obj_aa = point_obj_raw[point_obj_raw['code'].isin(points_code_extended)]
                                point_obj_aa = point_obj_aa.drop(columns=['time', 'index', 'name',
                                                                          'longitude', 'latitude'])

                                point_obj_aa = point_obj_aa.set_index('code')
                                point_obj_aa.index.name = 'code'

                                if point_collections is None:
                                    point_collections = deepcopy(point_obj_aa)
                                else:
                                    point_collections = pd.concat([point_collections, point_obj_aa],
                                                                  1, ignore_index=True)
                                point_time.append(point_obj_timestamp)

                                logging.info(' ------> Timestep ' + str(timestamp_step) + ' ... DONE')

                            point_values = point_collections.values.T
                            point_code = point_collections.index.values
                            point_datetime_idx = pd.DatetimeIndex(point_time)

                            point_df = pd.DataFrame(data=point_values, index=point_time, columns=point_code)

                        else:
                            logging.error(' ===> Length of file list is not allowed')
                            raise NotImplementedError('Case is not implemented yet')
                    else:
                        logging.error(' ===> Filename format is not allowed')
                        raise NotImplementedError('Format is not implemented yet')

                    analysis_obj = {}
                    for geo_key, geo_neighbour in geo_data_obj.items():
                        logging.info(' ------> Weather Station ' + geo_key + ' ... ')

                        geo_codes_nb = list(geo_neighbour['code'])
                        geo_codes_filter = list(set(geo_codes_nb).intersection(list(point_df.columns)))

                        for time_interval_value in group_data_items['rain_datasets']['search_period']:

                            logging.info(' -------> Compute peak for ' + time_interval_value + ' ... ')

                            tag_rain_peak = self.template_rain_point_peak.format(time_interval_value)

                            point_df_select = point_df[geo_codes_filter]
                            point_df_resample = point_df_select.resample(time_interval_value, label='right').max()[:-1]
                            point_max_value = point_df_resample.to_numpy().max()

                            if tag_rain_peak not in list(analysis_obj.keys()):
                                analysis_obj[tag_rain_peak] = {}
                                analysis_obj[tag_rain_peak][geo_key] = point_max_value
                            else:
                                point_max_tmp = analysis_obj[tag_rain_peak]
                                point_max_tmp[geo_key] = point_max_value
                                analysis_obj[tag_rain_peak] = point_max_tmp

                            logging.info(' -------> Compute peak for ' + time_interval_value + ' ... DONE')

                        logging.info(' ------> Weather Station ' + geo_key + ' ... DONE')

                    peak_obj = {}
                    for analysis_time, analysis_dataset in analysis_obj.items():
                        value_max = pd.Series(analysis_dataset).max()
                        peak_obj[analysis_time] = value_max

                    logging.info(' -----> Alert Area ' + group_data_key + ' ... DONE')

                else:
                    peak_obj = None
                    logging.warning(' ===> Rain data are not available')
                    logging.info(' -----> Alert Area ' + group_data_key + ' ... SKIPPED. Datasets are not available.')

                group_analysis[group_data_key] = peak_obj

            else:

                logging.info(' -----> Alert Area ' + group_data_key + ' ... SKIPPED. Analysis file created previously')

        logging.info(' ----> Compute rain analysis point [' + str(self.time_step) + '] ... DONE')

        return group_analysis

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute time interval
    @staticmethod
    def compute_time_interval(time_step, time_delta_max, time_delta_list):

        time_period_max, time_frequency_max = split_time_parts(time_delta_max)

        time_interval = {}
        for time_delta_step in time_delta_list:

            time_period_step, time_frequency_step = split_time_parts(time_delta_step)
            time_period_ratio = int(time_period_max / time_period_step)

            time_step_range_down = pd.date_range(start=time_step, periods=time_period_ratio, freq=time_delta_step)
            time_step_up = pd.date_range(start=time_step, periods=time_period_step, freq=time_frequency_max)[-1]
            time_step_range_up = pd.date_range(start=time_step_up, periods=time_period_ratio, freq=time_delta_step)

            time_interval[time_delta_step] = {}
            for time_id, (time_step_down, time_step_up) in enumerate(zip(time_step_range_down, time_step_range_up)):
                time_interval[time_delta_step]['time_{}'.format(str(time_id))] = {}

                time_interval[time_delta_step]['time_{}'.format(str(time_id))]['time_start'] = {}
                time_interval[time_delta_step]['time_{}'.format(str(time_id))]['time_start'] = time_step_down
                time_interval[time_delta_step]['time_{}'.format(str(time_id))]['time_end'] = {}
                time_interval[time_delta_step]['time_{}'.format(str(time_id))]['time_end'] = time_step_up

        return time_interval
    # -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to collect ancillary file
def collect_file_list(time_range, folder_name_raw, file_name_raw, template_tags, alert_area_name=None):
    if (not isinstance(time_range, pd.DatetimeIndex)) and (isinstance(time_range, pd.Timestamp)):
        time_range = pd.DatetimeIndex([time_range])

    file_name_list = []
    for datetime_step in time_range:
        template_values_step = {
            'alert_area_name': alert_area_name,
            'source_rain_datetime': datetime_step, 'source_rain_sub_path_time': datetime_step,
            'source_sm_datetime': datetime_step, 'source_sm_sub_path_time': datetime_step,
            'ancillary_rain_datetime': datetime_step, 'ancillary_rain_sub_path_time': datetime_step,
            'ancillary_sm_datetime': datetime_step, 'ancillary_sm_sub_path_time': datetime_step,
            'destination_indicators_datetime': datetime_step, 'destination_indicators_sub_path_time': datetime_step
        }

        folder_name_def = fill_tags2string(folder_name_raw, template_tags, template_values_step)
        file_name_def = fill_tags2string(file_name_raw, template_tags, template_values_step)

        file_path_def = os.path.join(folder_name_def, file_name_def)

        file_name_list.append(file_path_def)

    return file_name_list

# -------------------------------------------------------------------------------------
