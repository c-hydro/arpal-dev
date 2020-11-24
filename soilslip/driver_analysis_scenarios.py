"""
Class Features

Name:          driver_analysis_scenarios
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200515'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os
import re
import numpy as np
import pandas as pd
import xarray as xr

from lib_utils_generic import get_dict_nested_value, find_maximum_delta, split_time_parts
from lib_utils_system import fill_tags2string, make_folder
from lib_utils_io import write_obj, read_obj, write_file_csv
from lib_utils_plot import plot_scenarios_sm2event, plot_scenarios_rain2event, plot_scenarios_rain2sm

# Debug
import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverAnalysis for scenarios
class DriverAnalysis:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_run, time_range, ancillary_dict, dst_dict,
                 alg_ancillary=None, alg_template_tags=None,
                 geo_data_region=None, geo_data_alert_area=None,
                 group_data=None,
                 flag_time_data='time',
                 flag_event_data='indicators_event',
                 flag_indicators_data='indicators_data', flag_scenarios_data='scenarios_data',
                 flag_scenarios_graph_sm2event=None,
                 flag_scenarios_graph_rain2event=None,
                 flag_scenarios_graph_rain2sm=None,
                 flag_dest_updating=True,
                 event_n_min=0, event_label=True):

        if flag_scenarios_graph_rain2event is None:
            flag_scenarios_graph_rain2event = ['scenarios_graph', 'rain2event_graph']
        if flag_scenarios_graph_sm2event is None:
            flag_scenarios_graph_sm2event = ['scenarios_graph', 'sm2event_graph']
        if flag_scenarios_graph_rain2sm is None:
            flag_scenarios_graph_rain2sm = ['scenarios_graph', 'rain2sm_graph']

        self.time_run = time_run
        self.time_range = time_range
        self.time_range_from = time_range[-1]
        self.time_range_to = time_range[0]

        self.ancillary_dict = ancillary_dict
        self.dst_dict = dst_dict

        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.flag_time_data = flag_time_data
        self.flag_indicators_data = flag_indicators_data
        self.flag_event_data = flag_event_data
        self.flag_scenarios_data = flag_scenarios_data

        self.flag_scenarios_graph_sm2event = flag_scenarios_graph_sm2event
        self.flag_scenarios_graph_rain2event = flag_scenarios_graph_rain2event
        self.flag_scenarios_graph_rain2sm = flag_scenarios_graph_rain2sm

        self.geo_data_region = geo_data_region
        self.geo_data_alert_area = geo_data_alert_area

        self.alg_ancillary = alg_ancillary
        self.alg_template_tags = alg_template_tags

        self.structure_data_group = group_data

        self.file_name_indicators_raw = dst_dict[self.flag_indicators_data][self.file_name_tag]
        self.folder_name_indicators_raw = dst_dict[self.flag_indicators_data][self.folder_name_tag]
        self.file_name_scenarios_data_raw = dst_dict[self.flag_scenarios_data][self.file_name_tag]
        self.folder_name_scenarios_data_raw = dst_dict[self.flag_scenarios_data][self.folder_name_tag]

        dst_dict_selection = get_dict_nested_value(dst_dict, flag_scenarios_graph_rain2event)
        self.file_name_scenarios_graph_rain2event_raw = dst_dict_selection[self.file_name_tag]
        self.folder_name_scenarios_graph_rain2event_raw = dst_dict_selection[self.folder_name_tag]

        dst_dict_selection = get_dict_nested_value(dst_dict, flag_scenarios_graph_sm2event)
        self.file_name_scenarios_graph_sm2event_raw = dst_dict_selection[self.file_name_tag]
        self.folder_name_scenarios_graph_sm2event_raw = dst_dict_selection[self.folder_name_tag]

        dst_dict_selection = get_dict_nested_value(dst_dict, flag_scenarios_graph_rain2sm)
        self.file_name_scenarios_graph_rain2sm_raw = dst_dict_selection[self.file_name_tag]
        self.folder_name_scenarios_graph_rain2sm_raw = dst_dict_selection[self.folder_name_tag]

        self.flag_dest_updating = flag_dest_updating

        file_path_indicators_collections = {}
        for group_data_key in self.structure_data_group.keys():
            file_path_list = []
            for time_step in time_range:
                file_path_step = collect_file_list(
                    time_step, self.folder_name_indicators_raw, self.file_name_indicators_raw,
                    self.alg_template_tags, alert_area_name=group_data_key)[0]
                if os.path.exists(file_path_step):
                    file_path_list.append(file_path_step)
            if file_path_list:
                file_path_indicators_collections[group_data_key] = file_path_list
            else:
                file_path_indicators_collections[group_data_key] = None
        self.file_path_indicators_collections = file_path_indicators_collections

        file_path_scenarios_data_collections = {}
        file_path_scenarios_graph_rain2event_collections = {}
        file_path_scenarios_graph_sm2event_collections = {}
        file_path_scenarios_graph_rain2sm_collections = {}
        for group_data_key in self.structure_data_group.keys():
            file_path_list = collect_file_list(
                self.time_run, self.folder_name_scenarios_data_raw, self.file_name_scenarios_data_raw,
                self.alg_template_tags, alert_area_name=group_data_key,
                time_run=self.time_run, time_from=self.time_range_from, time_to=self.time_range_to)
            file_path_scenarios_data_collections[group_data_key] = file_path_list

            file_path_list_rain2sm = collect_file_list(
                self.time_run, self.folder_name_scenarios_graph_rain2sm_raw, self.file_name_scenarios_graph_rain2sm_raw,
                self.alg_template_tags, alert_area_name=group_data_key,
                time_run=self.time_run, time_from=self.time_range_from, time_to=self.time_range_to)
            file_path_scenarios_graph_rain2sm_collections[group_data_key] = file_path_list_rain2sm

            file_path_list_sm2event = collect_file_list(
                self.time_run,
                self.folder_name_scenarios_graph_sm2event_raw, self.file_name_scenarios_graph_sm2event_raw,
                self.alg_template_tags, alert_area_name=group_data_key,
                time_run=self.time_run, time_from=self.time_range_from, time_to=self.time_range_to)
            file_path_scenarios_graph_sm2event_collections[group_data_key] = file_path_list_sm2event

            file_path_list_rain2event = collect_file_list(
                self.time_run,
                self.folder_name_scenarios_graph_rain2event_raw, self.file_name_scenarios_graph_rain2event_raw,
                self.alg_template_tags, alert_area_name=group_data_key,
                time_run=self.time_run, time_from=self.time_range_from, time_to=self.time_range_to)
            file_path_scenarios_graph_rain2event_collections[group_data_key] = file_path_list_rain2event

        self.file_path_scenarios_data_collections = file_path_scenarios_data_collections
        self.file_path_scenarios_graph_sm2event_collections = file_path_scenarios_graph_sm2event_collections
        self.file_path_scenarios_graph_rain2event_collections = file_path_scenarios_graph_rain2event_collections
        self.file_path_scenarios_graph_rain2sm_collections = file_path_scenarios_graph_rain2sm_collections

        self.template_rain_accumulated = 'rain_accumulated_{:}'
        self.template_rain_avg = 'rain_average_{:}'

        self.event_n_min = event_n_min
        self.event_label = event_label

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to plot scenarios data
    def plot_scenarios(self, scenarios_collections):

        logging.info(' ----> Plot scenarios [' + str(self.time_run) + '] ... ')

        scenarios_sm2event_file_path = self.file_path_scenarios_graph_sm2event_collections
        scenarios_rain2event_file_path = self.file_path_scenarios_graph_rain2event_collections
        scenarios_rain2sm_file_path = self.file_path_scenarios_graph_rain2sm_collections

        for group_data_key, group_data_alert_value in self.structure_data_group.items():

            logging.info(' -----> Alert Area ' + group_data_key + '  ... ')

            file_path_sm2event = scenarios_sm2event_file_path[group_data_key][0]
            file_path_rain2event = scenarios_rain2event_file_path[group_data_key][0]
            file_path_rain2sm = scenarios_rain2sm_file_path[group_data_key][0]
            file_data = scenarios_collections[group_data_key]

            rain_period_list = group_data_alert_value['rain_datasets']['search_period']

            if file_data is not None:

                logging.info(' ------> Plot rain against sm ... ')

                folder_name_rain2sm, file_name_rain2sm = os.path.split(file_path_rain2sm)
                make_folder(folder_name_rain2sm)

                plot_scenarios_rain2sm(file_data, file_path_rain2sm,
                                       var_x='soil_moisture_max', var_y=self.template_rain_accumulated,
                                       var_z='event_index',
                                       event_n_min=self.event_n_min, event_label=self.event_label,
                                       figure_dpi=60,
                                       extra_args={'rain_type': rain_period_list,
                                                   'soil_moisture_type': 'max'})

                plot_scenarios_rain2sm(file_data, file_path_rain2sm,
                                       var_x='soil_moisture_avg', var_y=self.template_rain_accumulated,
                                       var_z='event_index',
                                       event_n_min=self.event_n_min, event_label=self.event_label,
                                       figure_dpi=60,
                                       extra_args={'rain_type': rain_period_list,
                                                   'soil_moisture_type': 'average'})

                logging.info(' ------> Plot rain against sm ... DONE')

                logging.info(' ------> Plot sm against events ... ')

                folder_name_sm2event, file_name_sm2event = os.path.split(file_path_sm2event)
                make_folder(folder_name_sm2event)

                plot_scenarios_sm2event(file_data, file_path_sm2event,
                                        event_n_min=self.event_n_min, event_label=self.event_label,
                                        figure_dpi=120)
                logging.info(' ------> Plot sm against events ... DONE')

                logging.info(' ------> Plot rain against events ... ')

                folder_name_rain2event, file_name_rain2event = os.path.split(file_path_rain2event)
                make_folder(folder_name_rain2event)

                plot_scenarios_rain2event(file_data, file_path_rain2event)
                logging.info(' ------> Plot rain against events ... DONE')

                logging.info(' -----> Alert Area ' + group_data_key + '  ... DONE')
            else:
                logging.info(' -----> Alert Area ' + group_data_key + '  ... SKIPPED. Datasets are undefined.')

        logging.info(' ----> Plot scenarios [' + str(self.time_run) + '] ... DONE')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to dump scenarios data
    def dump_scenarios(self, scenarios_collections):

        logging.info(' ----> Dump scenarios [' + str(self.time_run) + '] ... ')

        scenarios_file_path = self.file_path_scenarios_data_collections

        for group_data_key in self.structure_data_group.keys():

            logging.info(' -----> Alert Area ' + group_data_key + '  ... ')

            file_path = scenarios_file_path[group_data_key]
            file_data = scenarios_collections[group_data_key]

            if file_data is not None:

                if isinstance(file_path, list):
                    file_path = file_path[0]

                folder_name, file_name = os.path.split(file_path)
                make_folder(folder_name)

                write_file_csv(file_path, file_data)

                logging.info(' -----> Alert Area ' + group_data_key + '  ... DONE')
            else:
                logging.info(' -----> Alert Area ' + group_data_key + '  ... SKIPPED. Datasets are undefined.')

        logging.info(' ----> Dump scenarios [' + str(self.time_run) + '] ... DONE')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect scenarios data
    def collect_scenarios(self):

        logging.info(' ----> Collect scenarios [' + str(self.time_run) + '] ... ')

        geo_data_alert_area = self.geo_data_alert_area
        group_data_alert_area = self.structure_data_group
        file_path_indicators_collections = self.file_path_indicators_collections

        scenarios_collections = {}
        for (group_data_key, group_data_items), geo_data_dframe in zip(group_data_alert_area.items(),
                                                                       geo_data_alert_area.values()):

            logging.info(' -----> Alert Area ' + group_data_key + '  ... ')

            file_path_indicators_selection = file_path_indicators_collections[group_data_key]

            if file_path_indicators_selection is not None:

                file_time_list = []
                file_scenarios_collections = {}
                for file_path_step in file_path_indicators_selection:

                    file_obj_step = read_obj(file_path_step)

                    file_time_step = file_obj_step[self.flag_time_data]
                    file_indicators_step = file_obj_step[self.flag_indicators_data]
                    file_event_step = file_obj_step[self.flag_event_data]

                    if (file_indicators_step is not None) and (file_event_step is not None):
                        file_time_list.append(file_time_step)

                        file_scenarios_dict = {**file_indicators_step, **file_event_step}
                        for field_key, field_value in file_scenarios_dict.items():
                            if field_key not in file_scenarios_collections:
                                file_scenarios_collections[field_key] = [field_value]
                            else:
                                field_tmp = file_scenarios_collections[field_key]
                                field_tmp.append(field_value)
                                file_scenarios_collections[field_key] = field_tmp

                scenarios_df = pd.DataFrame(index=file_time_list, data=file_scenarios_collections)

                logging.info(' -----> Alert Area ' + group_data_key + '  ... DONE')
            else:
                scenarios_df = None
                logging.info(' -----> Alert Area ' + group_data_key + '  ... SKIPPED. All datasets are undefined')

            scenarios_collections[group_data_key] = scenarios_df

        logging.info(' ----> Collect scenarios [' + str(self.time_run) + '] ... DONE')

        return scenarios_collections

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to collect ancillary file
def collect_file_list(time_range, folder_name_raw, file_name_raw, template_tags,
                      alert_area_name=None,
                      time_run=None, time_from=None, time_to=None):

    if (not isinstance(time_range, pd.DatetimeIndex)) and (isinstance(time_range, pd.Timestamp)):
        time_range = pd.DatetimeIndex([time_range])

    if time_run is None:
        datetime_run = time_range[0]
    else:
        datetime_run = time_run
    if time_from is None:
        datetime_from = time_range[-1]
    else:
        datetime_from = time_from
    if time_to is None:
        datetime_to = time_range[0]
    else:
        datetime_to = time_to

    file_name_list = []
    for datetime_step in time_range:
        template_values_step = {
            'alert_area_name': alert_area_name,
            'run_datetime': datetime_run, 'run_sub_path_time': datetime_run,
            'destination_indicators_datetime': datetime_step, 'destination_indicators_sub_path_time': datetime_step,
            'destination_scenarios_datetime': datetime_step, 'destination_scenarios_sub_path_time': datetime_step,
            'destination_scenarios_datetime_from': datetime_from,
            'destination_scenarios_datetime_to': datetime_to,
        }

        template_common_keys = set(template_tags).intersection(template_values_step)
        template_common_tags = {common_key: template_tags[common_key] for common_key in template_common_keys}

        folder_name_def = fill_tags2string(folder_name_raw, template_common_tags, template_values_step)
        file_name_def = fill_tags2string(file_name_raw, template_common_tags, template_values_step)

        file_path_def = os.path.join(folder_name_def, file_name_def)

        file_name_list.append(file_path_def)

    return file_name_list

# -------------------------------------------------------------------------------------
