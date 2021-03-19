"""
Class Features

Name:          driver_data_io_destination
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200515'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os
import numpy as np

from copy import deepcopy

from lib_utils_geo import read_file_geo
from lib_utils_hazard import read_file_hazard
from lib_utils_io import read_file_json, read_obj, write_obj, write_file_tif
from lib_utils_system import fill_tags2string, make_folder
from lib_utils_generic import get_dict_value
from lib_utils_plot import save_file_tiff, save_file_png, save_file_json

# Debug
import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverScenario
class DriverScenario:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_now, time_run, discharge_data_collection, geo_data_collection, src_dict, dst_dict,
                 alg_ancillary=None, alg_template_tags=None,
                 flag_telemac_data='telemac_data', flag_hazard_data='hazard_data',
                 flag_scenario_data='scenario_data',
                 flag_scenario_plot_tiff='scenario_plot_tiff', flag_scenario_plot_png='scenario_plot_png',
                 flag_cleaning_scenario=True):

        self.time_now = time_now
        self.time_run = time_run

        self.discharge_data_collection = discharge_data_collection
        self.geo_data_collection = geo_data_collection

        self.flag_telemac_data = flag_telemac_data
        self.flag_hazard_data = flag_hazard_data
        self.flag_scenario_data = flag_scenario_data
        self.flag_scenario_plot_tiff = flag_scenario_plot_tiff
        self.flag_scenario_plot_png = flag_scenario_plot_png

        self.alg_ancillary = alg_ancillary
        self.tr_min = alg_ancillary['tr_min']
        self.tr_max = alg_ancillary['tr_max']

        self.alg_template_tags = alg_template_tags
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.domain_name_list = self.alg_ancillary['domain_name']

        self.folder_name_telemac = src_dict[self.flag_telemac_data][self.folder_name_tag]
        self.file_name_telemac = src_dict[self.flag_telemac_data][self.file_name_tag]

        self.folder_name_hazard = src_dict[self.flag_hazard_data][self.folder_name_tag]
        self.file_name_hazard = src_dict[self.flag_hazard_data][self.file_name_tag]

        self.format_tr = '{:03d}'
        self.scenario_tr = self.define_tr_scenario(self.alg_ancillary['tr_min'], self.alg_ancillary['tr_max'],
                                                   self.alg_ancillary['tr_freq'])

        self.folder_name_scenario_data = dst_dict[self.flag_scenario_data][self.folder_name_tag]
        self.file_name_scenario_data = dst_dict[self.flag_scenario_data][self.file_name_tag]
        self.folder_name_scenario_plot_tiff = dst_dict[self.flag_scenario_plot_tiff][self.folder_name_tag]
        self.file_name_scenario_plot_tiff = dst_dict[self.flag_scenario_plot_tiff][self.file_name_tag]
        self.folder_name_scenario_plot_png = dst_dict[self.flag_scenario_plot_png][self.folder_name_tag]
        self.file_name_scenario_plot_png = dst_dict[self.flag_scenario_plot_png][self.file_name_tag]

        self.flag_cleaning_scenario = flag_cleaning_scenario

        self.domain_discharge_index_tag = 'discharge_idx'
        self.domain_grid_x_tag = 'grid_x_grid'
        self.domain_grid_y_tag = 'grid_y_grid'
        self.domain_sections_db_tag = 'domain_sections_db'

        self.domain_scenario_index_tag = 'scenario_idx'
        self.domain_scenario_discharge_tag = 'discharge_value'
        self.domain_scenario_time_tag = 'time'
        self.domain_scenario_n_tag = 'scenario_n'

        self.domain_scenario_area_tag = "mappa_aree_new"
        self.domain_scenario_grid_x_tag = "new_x"
        self.domain_scenario_grid_y_tag = "new_y"

        self.domain_scenario_hazard_tag = 'mappa_h'

        self.domain_name_tag = 'domain_name'

        self.scale_factor_hazard = 1000
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define hazard file
    def define_file_hazard(self, folder_name_raw, file_name_raw, domain_name, section_tr):

        template_tags = self.alg_template_tags

        template_values_step = {'domain_name': domain_name, 'tr': self.format_tr.format(section_tr)}

        folder_name_def = fill_tags2string(folder_name_raw, template_tags, template_values_step)
        file_name_def = fill_tags2string(file_name_raw, template_tags, template_values_step)
        path_name_def = os.path.join(folder_name_def, file_name_def)

        return path_name_def

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define scenarios tr
    def define_tr_scenario(self, tr_min, tr_max, tr_freq=1):
        scenario_tr_raw = np.arange(tr_min, tr_max + 1, tr_freq).tolist()
        scenario_tr_def = []
        for scenario_step in scenario_tr_raw:
            scenario_tmp = self.format_tr.format(scenario_step)
            scenario_tr_def.append(scenario_tmp)
        return scenario_tr_def
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute tr for evaluating scenario
    @staticmethod
    def compute_scenario_tr(section_discharge_idx, section_discharge_value):

        if section_discharge_idx > 0.0:
            if section_discharge_value >= 0.0:
                section_scenario_tr = np.round(np.exp(
                    (section_discharge_idx * 0.5239 + section_discharge_value) / (section_discharge_idx * 1.0433)))
                section_scenario_tr = int(section_scenario_tr)
            else:
                section_scenario_tr = np.nan
        else:
            section_scenario_tr = np.nan

        return section_scenario_tr
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute discharge for evaluating scenario
    @staticmethod
    def compute_scenario_discharge(dframe_discharge, method='max'):

        if method == 'max':
            reference_value = list(dframe_discharge.idxmax().index)[0]
            time_value = list(dframe_discharge.idxmax().values)[0]
            occurrence_value = list(dframe_discharge.idxmax().index).__len__()
            discharge_value = list(dframe_discharge.max())[0]
        else:
            logging.error(' ===> Method to compute discharge for evaluating scenario not defined')
            raise NotImplemented('Method not implemented yet')

        return reference_value, time_value, discharge_value, occurrence_value
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define hazard file
    def define_file_scenario(self, time, folder_name_raw, file_name_raw, domain_name):

        template_tags = self.alg_template_tags

        template_values_step = {'domain_name': domain_name,
                                'destination_sub_path_time_scenario': time,
                                'destination_datetime_scenario': time}

        folder_name_def = fill_tags2string(folder_name_raw, template_tags, template_values_step)
        file_name_def = fill_tags2string(file_name_raw, template_tags, template_values_step)
        path_name_def = os.path.join(folder_name_def, file_name_def)

        return path_name_def

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to dump scenario map
    def dump_scenario_map(self, scenario_map_collection, scenario_info_collection):

        time_run = self.time_run
        time_stamp = self.time_now
        time_string = self.time_now.strftime(format='%Y-%m-%d %H:%M')
        geo_data_collection = self.geo_data_collection

        logging.info(' --> Dump scenario maps [' + str(time_run) + '] ... ')

        for domain_name_step in self.domain_name_list:

            logging.info(' ---> Domain ' + domain_name_step + ' ... ')

            domain_geo_collection = geo_data_collection[domain_name_step]
            domain_info_collection = scenario_info_collection[domain_name_step]
            domain_map_collection = scenario_map_collection[domain_name_step]

            if domain_map_collection is not None:

                file_path_scenario_data = self.define_file_scenario(
                    time_stamp, self.folder_name_scenario_data, self.file_name_scenario_data, domain_name_step)
                file_path_scenario_plot_tiff = self.define_file_scenario(
                    time_stamp, self.folder_name_scenario_plot_tiff, self.file_name_scenario_plot_tiff, domain_name_step)
                file_path_scenario_plot_png = self.define_file_scenario(
                    time_stamp, self.folder_name_scenario_plot_png, self.file_name_scenario_plot_png, domain_name_step)

                domain_geo_data = domain_geo_collection[self.domain_scenario_area_tag]
                domain_geo_x = domain_geo_collection[self.domain_scenario_grid_x_tag]
                domain_geo_y = domain_geo_collection[self.domain_scenario_grid_y_tag]

                domain_info_collection['scenario_name'] = domain_name_step
                domain_info_collection['scenario_time'] = time_string

                # Save information in json file
                folder_name_scenario_data, file_name_scenario_data = os.path.split(file_path_scenario_data)
                make_folder(folder_name_scenario_data)

                logging.info(' ----> Save file json ' + file_name_scenario_data + ' ... ')
                save_file_json(file_path_scenario_data, domain_info_collection)
                logging.info(' ----> Save file json ' + file_name_scenario_data + ' ... DONE')

                # Save information in png file
                folder_name_scenario_plot_png, file_name_scenario_plot_png = os.path.split(file_path_scenario_plot_png)
                make_folder(folder_name_scenario_plot_png)

                logging.info(' ----> Save file png ' + file_name_scenario_plot_png + ' ... ')
                save_file_png(file_path_scenario_plot_png,
                              domain_map_collection, domain_geo_x, domain_geo_y,
                              scenario_name=domain_name_step, scenario_timestamp=time_string,
                              fig_color_map_type=None, fig_dpi=150)
                logging.info(' ----> Save file png ' + file_name_scenario_plot_png + ' ... DONE')

                # Save information in tiff file
                folder_name_scenario_plot_tiff, file_name_scenario_plot_tiff = os.path.split(file_path_scenario_plot_tiff)
                make_folder(folder_name_scenario_plot_tiff)

                logging.info(' ----> Save file tiff ' + file_name_scenario_plot_tiff + ' ... ')
                save_file_tiff(file_path_scenario_plot_tiff,
                               domain_map_collection, domain_geo_x, domain_geo_y,
                               file_epsg_code='EPSG:32632')
                logging.info(' ----> Save file tiff ' + file_name_scenario_plot_tiff + ' ... DONE')

                logging.info(' ---> Domain ' + domain_name_step + ' ... DONE')

            else:
                logging.info(' ---> Domain ' + domain_name_step + ' ... SKIPPED. Datasets are empty')

        logging.info(' --> Dump scenario maps [' + str(time_run) + '] ... DONE')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute scenario map
    def compute_scenario_map(self, scenario_data_collection):

        time = self.time_run
        geo_data_collection = self.geo_data_collection

        logging.info(' --> Compute scenario maps [' + str(time) + '] ... ')

        scenario_map_collection = {}
        for domain_name_step in self.domain_name_list:

            logging.info(' ---> Domain ' + domain_name_step + ' ... ')

            domain_geo_data = geo_data_collection[domain_name_step]
            domain_scenario_data = scenario_data_collection[domain_name_step]
            domain_section_db = geo_data_collection[domain_name_step][self.domain_sections_db_tag]

            if domain_scenario_data is not None:

                domain_scenario_merged = np.zeros(
                    [domain_geo_data[self.domain_scenario_area_tag].shape[0],
                     domain_geo_data[self.domain_scenario_area_tag].shape[1]])
                domain_scenario_merged[:, :] = np.nan
                for (section_db_key, section_db_data), (section_scenario_key, section_scenario_data) in zip(
                        domain_section_db.items(), domain_scenario_data.items()):

                    logging.info(' ----> Section ' + section_scenario_key + ' ... ')

                    section_db_n = section_db_data['n']
                    section_db_description = section_db_data['description']
                    section_db_name = section_db_data['name']
                    section_db_idx = section_db_data['idx']
                    section_db_discharge_default = section_db_data['discharge_default']

                    assert section_db_description == section_scenario_key

                    section_scenario_tr_cmp = section_scenario_data[self.domain_scenario_index_tag]

                    # Check tr value
                    if np.isnan(section_scenario_tr_cmp):
                        section_scenario_tr_other = get_dict_value(domain_scenario_data, self.domain_scenario_index_tag, [])
                        section_scenario_tr_check = int(np.nanmax(section_scenario_tr_other))
                    else:
                        section_scenario_tr_check = section_scenario_tr_cmp

                    if section_scenario_tr_check >= self.tr_min:

                        section_area_idx = np.argwhere(domain_geo_data[self.domain_scenario_area_tag] == section_db_n)

                        section_scenario_tr_select = max(1, min(self.tr_max, section_scenario_tr_check))

                        file_path_hazard = self.define_file_hazard(self.folder_name_hazard, self.file_name_hazard,
                                                                   domain_name_step, section_scenario_tr_select)

                        file_data_hazard = read_file_hazard(
                            file_path_hazard, file_vars=[self.domain_scenario_hazard_tag])
                        file_data_h = file_data_hazard[self.domain_scenario_hazard_tag]

                        idx_x = section_area_idx[:, 0]
                        idx_y = section_area_idx[:, 1]
                        domain_scenario_merged[idx_x, idx_y] = file_data_h[idx_x, idx_y]

                    logging.info(' ----> Section ' + section_scenario_key + ' ... DONE')

                # Adjust map values
                domain_scenario_merged = domain_scenario_merged / self.scale_factor_hazard
                domain_scenario_merged[domain_scenario_merged <= 0] = np.nan

                logging.info(' ---> Domain ' + domain_name_step + ' ... DONE')

            else:
                logging.info(' ---> Domain ' + domain_name_step + ' ... SKIPPED. Datasets are empty')
                domain_scenario_merged = None

            # Store map values
            scenario_map_collection[domain_name_step] = domain_scenario_merged

        logging.info(' --> Compute scenario maps [' + str(time) + '] ... DONE')

        return scenario_map_collection
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize scenario datasets
    def organize_scenario_datasets(self):

        time = self.time_run
        discharge_data_collection = self.discharge_data_collection
        geo_data_collection = self.geo_data_collection

        logging.info(' --> Organize scenario datasets [' + str(time) + '] ... ')

        scenario_info_collection = {}
        for domain_name_step in self.domain_name_list:

            logging.info(' ---> Domain ' + domain_name_step + ' ... ')

            domain_discharge_data = discharge_data_collection[domain_name_step]
            domain_geo_data = geo_data_collection[domain_name_step]

            domain_discharge_index = geo_data_collection[domain_name_step][self.domain_discharge_index_tag]
            domain_grid_rows = geo_data_collection[domain_name_step][self.domain_grid_x_tag].shape[0]
            domain_grid_cols = geo_data_collection[domain_name_step][self.domain_grid_y_tag].shape[1]
            domain_section_db = geo_data_collection[domain_name_step][self.domain_sections_db_tag]

            domain_scenario_workspace = {}
            for (section_db_key, section_db_data), (section_discharge_key, section_discharge_data) in zip(
                    domain_section_db.items(), domain_discharge_data.items()):

                logging.info(' ----> Section ' + section_discharge_key + ' ... ')

                if section_discharge_data is not None:
                    section_db_n = section_db_data['n']
                    section_db_description = section_db_data['description']
                    section_db_name = section_db_data['name']
                    section_db_idx = section_db_data['idx']
                    section_db_discharge_default = section_db_data['discharge_default']

                    assert section_db_description == section_discharge_key

                    # Compute scenario idx
                    section_discharge_idx = domain_discharge_index[section_db_idx[0] - 1, section_db_idx[1] - 1]

                    # Compute discharge for evaluating scenario
                    section_discharge_run, section_discharge_time, \
                        section_discharge_value, section_n_value = self.compute_scenario_discharge(section_discharge_data)
                    # Compute tr for evaluating scenario
                    section_scenario_tr = self.compute_scenario_tr(section_discharge_idx, section_discharge_value)

                    domain_scenario_workspace[section_discharge_key] = {}
                    domain_scenario_workspace[section_discharge_key][self.domain_scenario_index_tag] = section_scenario_tr
                    domain_scenario_workspace[section_discharge_key][self.domain_scenario_discharge_tag] = section_discharge_value
                    domain_scenario_workspace[section_discharge_key][self.domain_scenario_time_tag] = section_discharge_time
                    domain_scenario_workspace[section_discharge_key][self.domain_scenario_n_tag] = section_n_value

                    logging.info(' ----> Section ' + section_discharge_key + ' ... DONE')

                else:

                    logging.info(' ----> Section ' + section_discharge_key + ' ... SKIPPED. Datasets are empty')
                    domain_scenario_workspace = None

            scenario_info_collection[domain_name_step] = domain_scenario_workspace

            logging.info(' ---> Domain ' + domain_name_step + ' ... DONE')

        logging.info(' --> Organize scenario datasets [' + str(time) + '] ... DONE')

        return scenario_info_collection

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
