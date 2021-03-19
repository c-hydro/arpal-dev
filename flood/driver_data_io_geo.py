"""
Class Features

Name:          driver_data_io_geo
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200515'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os
import numpy as np

from lib_utils_geo import read_file_geo, read_file_drainage_area
from lib_utils_hydro import read_file_info
from lib_utils_io import read_file_json, read_obj, write_obj, read_mat
from lib_utils_system import fill_tags2string, make_folder

# Debug
# import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverGeo
class DriverGeo:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, src_dict, dst_dict,
                 alg_ancillary=None, alg_template_tags=None,
                 flag_geo_data='geo_data',
                 flag_telemac_data='telemac_data', flag_hazard_data='hazard_data', flag_drift_data='drift_data',
                 flag_drainage_area_data='drainage_area_data', flag_info_data='info_data',
                 flag_domain_collections='domain_collection',
                 flag_cleaning_geo=True):

        self.flag_geo_data = flag_geo_data
        self.flag_telemac_data = flag_telemac_data
        self.flag_hazard_data = flag_hazard_data
        self.flag_drift_data = flag_drift_data
        self.flag_info_data = flag_info_data
        self.flag_drainage_area_data = flag_drainage_area_data
        self.flag_domain_collections = flag_domain_collections

        self.alg_ancillary = alg_ancillary

        self.alg_template_tags = alg_template_tags
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.domain_name_list = self.alg_ancillary['domain_name']
        self.hydro_group = self.alg_ancillary['drift_group']
        self.hydro_format = '{:02d}'

        self.folder_name_geo = src_dict[self.flag_geo_data][self.folder_name_tag]
        self.file_name_geo = src_dict[self.flag_geo_data][self.file_name_tag]

        self.folder_name_info = src_dict[self.flag_info_data][self.folder_name_tag]
        self.file_name_info = src_dict[self.flag_info_data][self.file_name_tag]

        self.folder_name_telemac = src_dict[self.flag_telemac_data][self.folder_name_tag]
        self.file_name_telemac = src_dict[self.flag_telemac_data][self.file_name_tag]

        self.folder_name_hazard = src_dict[self.flag_hazard_data][self.folder_name_tag]
        self.file_name_hazard = src_dict[self.flag_hazard_data][self.file_name_tag]

        self.folder_name_drainage_area = src_dict[self.flag_drainage_area_data][self.folder_name_tag]
        self.file_name_drainage_area = src_dict[self.flag_drainage_area_data][self.file_name_tag]

        self.folder_name_hydro = src_dict[self.flag_drift_data][self.folder_name_tag]
        self.file_name_hydro = src_dict[self.flag_drift_data][self.file_name_tag]

        self.folder_name_collections = dst_dict[self.flag_domain_collections][self.folder_name_tag]
        self.file_name_collections = dst_dict[self.flag_domain_collections][self.file_name_tag]

        self.data_geo = self.read_geo_ref()
        self.data_hydro = self.read_hydro_ref()

        self.flag_cleaning_geo = flag_cleaning_geo

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to read hydro reference file(s)
    def read_hydro_ref(self, tag_hydro_group='drift_group'):

        template_tags = self.alg_template_tags

        hydro_list = np.arange(1, self.hydro_group + 1, 1).tolist()

        folder_name_hydro_raw = self.folder_name_hydro
        file_name_hydro_raw = self.file_name_hydro

        file_data_collections = {}
        for hydro_id in hydro_list:

            hydro_value = self.hydro_format.format(hydro_id)
            template_values = {tag_hydro_group: hydro_value}

            folder_name_hydro_def = fill_tags2string(folder_name_hydro_raw, template_tags, template_values)
            file_name_hydro_def = fill_tags2string(file_name_hydro_raw, template_tags, template_values)
            file_path_hydro_def = os.path.join(folder_name_hydro_def, file_name_hydro_def)

            if os.path.exists(file_path_hydro_def):
                file_data_tmp = read_file_info(file_path_hydro_def, hydro_id)
                file_data_collections = {**file_data_collections, **file_data_tmp}
            else:
                logging.error(' ===> Hydro reference file ' + file_path_hydro_def + ' not available')
                raise IOError('Check your configuration file')

        return file_data_collections

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to read geographical reference file
    def read_geo_ref(self):
        if os.path.exists(os.path.join(self.folder_name_geo, self.file_name_geo)):
            if self.file_name_geo.endswith('mat'):
                data_geo = read_file_geo(os.path.join(self.folder_name_geo, self.file_name_geo))
            else:
                logging.error(' ===> Geographical reference file ' + self.file_name_geo + ' not available')
                raise IOError('Check your configuration file')
        else:
            logging.error(' ===> Geographical reference file ' + self.file_name_geo + ' not available')
            raise IOError('Check your configuration file')
        return data_geo

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get domain info
    def get_domain_info(self, domain_name):

        template_tags = self.alg_template_tags
        template_values = {'domain_name': domain_name}

        folder_name = fill_tags2string(self.folder_name_info, template_tags, template_values)
        file_name = fill_tags2string(self.file_name_info, template_tags, template_values)
        file_path = os.path.join(folder_name, file_name)

        if os.path.exists(file_path):

            domain_info_file = read_file_json(file_path)

            domain_section_db = domain_info_file['domain_sections_db']
            for domain_section_id, domain_section_fields in domain_section_db.items():
                domain_name = domain_section_fields['name']

                if domain_name in list(self.data_hydro.keys()):
                    domain_group = self.data_hydro[domain_name]
                else:
                    logging.error(' ===> Section ' + domain_name + ' is not available on hydro dataset')
                    raise IOError('Section not found')

                domain_section_fields['group'] = domain_group
                domain_section_db[domain_section_id] = domain_section_fields
            domain_info_file['domain_sections_db'] = domain_section_db

            domain_bbox_meters = domain_info_file['domain_bounding_box']['meters']
            domain_bbox_degree = domain_info_file['domain_bounding_box']['degree']

            domain_info_reference = find_domain_reference(
                self.data_geo['longitude'], self.data_geo['latitude'], domain_bbox_degree, domain_bbox_meters)

            idx_x_min = domain_info_reference['idx_x_min']
            idx_x_max = domain_info_reference['idx_x_max']
            idx_y_min = domain_info_reference['idx_y_min']
            idx_y_max = domain_info_reference['idx_y_max']
            for geo_key, geo_values in self.data_geo.items():
                geo_values_select = geo_values[idx_x_min:idx_x_max + 1, idx_y_min:idx_y_max + 1]
                domain_info_reference[geo_key] = geo_values_select

            domain_info_extended = {**domain_info_reference, **domain_info_file}

        else:
            logging.error(' ===> Domain info filename is not available. Check your settings.')
            raise IOError('File not found')

        return domain_info_extended

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get domain drainage area
    def get_domain_drainage_area(self, domain_name):

        template_tags = self.alg_template_tags
        template_values = {'domain_name': domain_name}

        folder_name_dr_area = fill_tags2string(self.folder_name_drainage_area, template_tags, template_values)
        file_name_dr_area = fill_tags2string(self.file_name_drainage_area, template_tags, template_values)
        file_path_dr_area = os.path.join(folder_name_dr_area, file_name_dr_area)

        if os.path.exists(file_path_dr_area):
            if file_path_dr_area.endswith('.mat'):
                domain_area = read_file_drainage_area(file_path_dr_area)
            else:
                logging.error(' ===> Drainage area file format not supported')
                raise NotImplementedError('Format not supported yet')
        else:
            logging.error(' ===> Drainage area is not available. Check your settings.')
            raise IOError('File not found')

        return domain_area
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define domain collection
    def define_domain_collection(self, domain_name):

        template_tags = self.alg_template_tags
        template_values = {'domain_name': domain_name}

        folder_name = fill_tags2string(self.folder_name_collections, template_tags, template_values)
        file_name = fill_tags2string(self.file_name_collections, template_tags, template_values)
        file_path = os.path.join(folder_name, file_name)

        if self.flag_cleaning_geo:
            if os.path.exists(file_path):
                os.remove(file_path)

        return file_path
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize geographical data
    def organize_geo(self):

        domain_collection_list = {}
        for domain_name_step in self.domain_name_list:

            file_path_collections = self.define_domain_collection(domain_name_step)

            if not os.path.exists(file_path_collections):

                domain_info = self.get_domain_info(domain_name_step)
                domain_drainage_area = self.get_domain_drainage_area(domain_name_step)

                domain_collection = {**domain_drainage_area, **domain_info}

                folder_name_collections, file_name_collections = os.path.split(file_path_collections)
                make_folder(folder_name_collections)
                write_obj(file_path_collections, domain_collection)

            else:

                domain_collection = read_obj(file_path_collections)

            domain_collection_list[domain_name_step] = domain_collection

        return domain_collection_list
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a domain collection
def find_domain_reference(lon_grid, lat_grid, domain_bbox_degree, domain_bbox_meters):

    center_left_dg = domain_bbox_degree['coord_left']
    center_right_dg = domain_bbox_degree['coord_right']
    center_bottom_dg = domain_bbox_degree['coord_bottom']
    center_top_dg = domain_bbox_degree['coord_top']
    cell_size_dg = domain_bbox_degree['cell_size']

    lon_1d = lon_grid[0, :]
    lat_1d = lat_grid[:, 0]
    array_idx_y_min = np.where((lon_1d - center_right_dg) < 0)[0]
    geo_idx_y_min = array_idx_y_min[-1]
    array_idx_y_max = np.where((lon_1d - center_left_dg) < 0)[0]
    geo_idx_y_max = array_idx_y_max[-1]
    array_idx_x_max = np.where((lat_1d - center_bottom_dg) > 0)[0]
    geo_idx_x_max = array_idx_x_max[-1]
    array_idx_x_min = np.where((lat_1d - center_top_dg) > 0)[0]
    geo_idx_x_min = array_idx_x_min[-1]

    center_left_mt = domain_bbox_meters['coord_left']
    center_right_mt = domain_bbox_meters['coord_right']
    center_bottom_mt = domain_bbox_meters['coord_bottom']
    center_top_mt = domain_bbox_meters['coord_top']
    cell_size_mt = domain_bbox_meters['cell_size']
    geo_array_x = np.arange(center_left_mt, center_right_mt, cell_size_mt, float)
    geo_array_y = np.arange(center_bottom_mt, center_top_mt, cell_size_mt, float)
    geo_grid_x, geo_grid_y = np.meshgrid(geo_array_x, geo_array_y)

    geo_domain_collections = {
        # 'center_left_degree': center_left_dg, 'center_right_degree': center_right_dg,
        # 'center_bottom_degree': center_bottom_dg, 'center_top_degree': center_top_dg,
        # 'cell_size_degree': cell_size_dg,
        # 'center_left_meter': center_left_mt, 'center_right_meter': center_right_mt,
        # 'center_bottom_meter': center_bottom_mt, 'center_top_meter': center_top_mt,
        # 'cell_size_meter': cell_size_mt,
        'grid_x_grid': geo_grid_x, 'grid_y_grid': geo_grid_y,
        'idx_y_min': geo_idx_y_min, 'idx_y_max': geo_idx_y_max,
        'idx_x_min': geo_idx_x_min, 'idx_x_max': geo_idx_x_max,
    }

    return geo_domain_collections
# -------------------------------------------------------------------------------------
