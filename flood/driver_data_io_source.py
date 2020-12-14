"""
Class Features

Name:          driver_data_io_source
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
import glob

from copy import deepcopy

from lib_utils_geo import read_file_geo
from lib_utils_hydro import read_file_hydro, parse_file_parts, create_file_tag
from lib_utils_io import read_file_json, read_obj, write_obj
from lib_utils_system import fill_tags2string, make_folder
from lib_utils_generic import get_dict_value

# Debug
# import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverDischarge
class DriverDischarge:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_now, time_run, geo_data_collection, src_dict, ancillary_dict,
                 alg_ancillary=None, alg_template_tags=None,
                 flag_discharge_data='discharge_data',
                 flag_cleaning_dynamic_ancillary=True):

        self.time_now = time_now
        self.time_run = time_run
        self.geo_data_collection = geo_data_collection

        self.flag_discharge_data = flag_discharge_data

        self.alg_ancillary = alg_ancillary

        self.alg_template_tags = alg_template_tags
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.domain_name_list = self.alg_ancillary['domain_name']

        domain_section_dict = {}
        for domain_name_step in self.domain_name_list:
            domain_section_list = get_dict_value(geo_data_collection[domain_name_step], 'name', [])
            domain_section_dict[domain_name_step] = domain_section_list
        self.domain_section_dict = domain_section_dict

        self.folder_name_discharge = src_dict[self.flag_discharge_data][self.folder_name_tag]
        self.file_name_discharge = src_dict[self.flag_discharge_data][self.file_name_tag]

        self.format_group = '{:02d}'
        self.file_path_discharge = self.define_file_discharge(
            self.time_run, self.folder_name_discharge, self.file_name_discharge)

        self.freq_discharge = 'H'
        self.periods_discharge_from = 72
        self.periods_discharge_to = 24
        self.file_time_discharge = self.define_file_time()

        self.folder_name_ancillary = ancillary_dict[self.flag_discharge_data][self.folder_name_tag]
        self.file_name_ancillary = ancillary_dict[self.flag_discharge_data][self.file_name_tag]

        self.file_path_ancillary = self.define_file_ancillary(
            self.time_now, self.folder_name_ancillary, self.file_name_ancillary)

        self.flag_cleaning_dynamic_ancillary = flag_cleaning_dynamic_ancillary

        self.domain_discharge_index_tag = 'discharge_idx'
        self.domain_grid_x_tag = 'grid_x_grid'
        self.domain_grid_y_tag = 'grid_y_grid'
        self.domain_sections_db_tag = 'domain_sections_db'
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define time period
    def define_file_time(self):

        time_run = self.time_run

        time_day_start = time_run.replace(hour=0)
        time_day_end = time_run.replace(hour=23)

        time_period_from = pd.date_range(
            end=time_day_start, periods=self.periods_discharge_from, freq=self.freq_discharge)
        time_period_day = pd.date_range(
            start=time_day_start, end=time_day_end, freq=self.freq_discharge)
        time_period_to = pd.date_range(
            start=time_day_end, periods=self.periods_discharge_to, freq=self.freq_discharge)

        time_period = time_period_from.union(time_period_day).union(time_period_to)

        return time_period

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define ancillary filename
    def define_file_ancillary(self, time, folder_name_raw, file_name_raw):

        alg_template_tags = self.alg_template_tags

        file_path_dict = {}
        for domain_name in self.domain_name_list:

            alg_template_values = {'domain_name': domain_name,
                                   'ancillary_sub_path_time_discharge': time,
                                   'ancillary_datetime_discharge': time}

            folder_name_def = fill_tags2string(folder_name_raw, alg_template_tags, alg_template_values)
            file_name_def = fill_tags2string(file_name_raw, alg_template_tags, alg_template_values)

            file_path_def = os.path.join(folder_name_def, file_name_def)

            file_path_dict[domain_name] = file_path_def

        return file_path_dict

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define discharge filename
    def define_file_discharge(self, time, folder_name_raw, file_name_raw,
                              file_sort_descending=True):

        alg_template_tags = self.alg_template_tags
        geo_data_collection = self.geo_data_collection

        file_path_dict = {}
        for domain_name in self.domain_name_list:

            file_path_dict[domain_name] = {}

            domain_id_list = get_dict_value(geo_data_collection[domain_name], 'id', [])

            for domain_id in domain_id_list:

                domain_group = self.format_group.format(int(domain_id))

                alg_template_values = {'domain_name': domain_name,
                                       'source_sub_path_time_discharge': time,
                                       'ancillary_sub_path_time_discharge': time,
                                       'source_datetime_from_discharge': '*',
                                       'source_datetime_to_discharge': time,
                                       'ancillary_datetime_discharge': time,
                                       'mask_discharge': '*' + domain_group,
                                       'scenario_discharge': '*'}

                folder_name_def = fill_tags2string(folder_name_raw, alg_template_tags, alg_template_values)
                file_name_def = fill_tags2string(file_name_raw, alg_template_tags, alg_template_values)

                file_path_def = os.path.join(folder_name_def, file_name_def)

                file_path_list = glob.glob(file_path_def)
                file_path_list.sort(reverse=file_sort_descending)

                file_path_dict[domain_name][domain_group] = file_path_list

        return file_path_dict

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize discharge
    def organize_discharge(self):

        time = self.time_run
        geo_data_collection = self.geo_data_collection

        logging.info(' --> Organize discharge datasets [' + str(time) + '] ... ')

        file_path_discharge = self.file_path_discharge
        file_time_discharge = self.file_time_discharge

        section_collection = {}
        for domain_name_step in self.domain_name_list:

            logging.info(' ---> Domain ' + domain_name_step + ' ... ')

            file_path_discharge = self.file_path_discharge[domain_name_step]
            file_path_ancillary = self.file_path_ancillary[domain_name_step]

            if self.flag_cleaning_dynamic_ancillary:
                if os.path.exists(file_path_ancillary):
                    os.remove(file_path_ancillary)

            if not os.path.exists(file_path_ancillary):

                domain_discharge_index = geo_data_collection[domain_name_step][self.domain_discharge_index_tag]
                domain_grid_rows = geo_data_collection[domain_name_step][self.domain_grid_x_tag].shape[0]
                domain_grid_cols = geo_data_collection[domain_name_step][self.domain_grid_y_tag].shape[1]
                domain_section_db = geo_data_collection[domain_name_step][self.domain_sections_db_tag]

                section_workspace = {}
                for section_key, section_data in domain_section_db.items():

                    section_description = section_data['description']
                    section_name = section_data['name']
                    section_idx = section_data['idx']
                    section_discharge_default = section_data['discharge_default']
                    section_id = self.format_group.format(section_data['group']['id'])

                    logging.info(' ----> Section ' + section_description + ' ... ')

                    section_file_path_list = file_path_discharge[section_id]

                    if section_file_path_list:
                        section_dframe = pd.DataFrame(index=file_time_discharge)
                        for section_file_path_step in section_file_path_list:

                            section_folder_name_step, section_file_name_step = os.path.split(section_file_path_step)

                            section_file_ts_start, section_file_ts_end, \
                                section_file_mask, section_file_ens = parse_file_parts(section_file_name_step)

                            section_file_tag = create_file_tag(section_file_ts_start, section_file_ts_end, section_file_ens)

                            section_ts = read_file_hydro(section_name, section_file_path_step)
                            section_dframe[section_file_tag] = section_ts

                        section_workspace[section_description] = section_dframe

                        logging.info(' ----> Section ' + section_description + ' ... DONE')

                    else:
                        logging.info(' ----> Section ' + section_description + ' ... SKIPPED. Datasets are empty')
                        section_workspace[section_description] = None

                folder_name_ancillary, file_name_ancillary = os.path.split(file_path_ancillary)
                make_folder(folder_name_ancillary)

                if None not in list(section_workspace.values()):
                    write_obj(file_path_ancillary, section_workspace)
                    logging.info(' ---> Domain ' + domain_name_step + ' ... DONE')
                else:
                    logging.info(' ---> Domain ' + domain_name_step + ' ... SKIPPED. All or some datasets are empty')

            else:

                section_workspace = read_obj(file_path_ancillary)

                logging.info(' ---> Domain ' + domain_name_step + ' ... SKIPPED. Data previously computed')

            section_collection[domain_name_step] = section_workspace

            logging.info(' --> Organize discharge datasets [' + str(time) + '] ... DONE')

        return section_collection

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
