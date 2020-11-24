"""
Class Features

Name:          driver_data_io_geo_grid
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200515'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os
import numpy as np

from lib_utils_tiff import convert_polygons_2_tiff, convert_shp_2_tiff, read_file_tiff
from lib_utils_shp import read_file_shp, convert_polygons_2_shp
from lib_utils_geo import get_file_raster
from lib_utils_io import read_file_json, read_obj, write_obj, create_darray_2d
from lib_utils_system import fill_tags2string, make_folder

# Debug
import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverGeo
class DriverGeoGrid:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, src_dict, dst_dict,
                 group_data=None, alg_template_tags=None,
                 flag_geo_data='geo_data', flag_basin_data='basin_data',
                 flag_geo_updating=True):

        self.flag_geo_data = flag_geo_data
        self.flag_basin_data = flag_basin_data

        self.alg_template_tags = alg_template_tags
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.region_tag = 'region'
        self.alert_area_vector_tag = 'alert_area_vector'
        self.alert_area_raster_tag = 'alert_area_raster'

        self.structure_region_group = {'region': {'name': 'Liguria'}}
        self.structure_data_group = group_data

        self.src_dict_geo = src_dict[self.flag_geo_data]
        self.src_dict_basin = src_dict[self.flag_basin_data]

        self.src_collection_geo = {}
        for src_key, src_fields in self.src_dict_geo.items():
            folder_name_def = src_fields[self.folder_name_tag]
            file_name_def = src_fields[self.file_name_tag]

            path_name_def = os.path.join(folder_name_def, file_name_def)
            self.src_collection_geo[src_key] = path_name_def

        self.src_collection_basin = {}
        for src_key, src_fields in self.src_dict_basin.items():
            folder_name_def = src_fields[self.folder_name_tag]
            file_name_def = src_fields[self.file_name_tag]

            path_name_def = os.path.join(folder_name_def, file_name_def)
            self.src_collection_basin[src_key] = path_name_def

        self.dst_dict_geo_region = dst_dict[self.flag_geo_data][self.region_tag]
        self.dst_dict_geo_alert_area_vector = dst_dict[self.flag_geo_data][self.alert_area_vector_tag]
        self.dst_dict_geo_alert_area_raster = dst_dict[self.flag_geo_data][self.alert_area_raster_tag]
        self.dst_dict_basin = dst_dict[self.flag_basin_data]

        self.file_path_region = os.path.join(self.dst_dict_geo_region[self.folder_name_tag],
                                             self.dst_dict_geo_region[self.file_name_tag])

        self.file_path_alert_area_vector_obj = self.collect_file_obj(
            self.dst_dict_geo_alert_area_vector[self.folder_name_tag], self.dst_dict_geo_alert_area_vector[self.file_name_tag])
        self.file_path_alert_area_raster_obj = self.collect_file_obj(
            self.dst_dict_geo_alert_area_raster[self.folder_name_tag], self.dst_dict_geo_alert_area_raster[self.file_name_tag])

        self.dset_geo_region = self.read_geo_data_region()
        self.dset_geo_alert_area = self.read_geo_data_alert_area()

        self.dset_basins = self.read_geo_basin()

        self.flag_geo_updating = flag_geo_updating

        self.tag_mask = 'mask_value'

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect file
    def collect_file_obj(self, folder_name_raw, file_name_raw):

        data_group = self.structure_data_group

        file_name_obj = {}
        for group_key, group_data in data_group.items():

            file_name_obj[group_key] = {}

            group_name = group_data['name']
            alg_template_values_step = {'alert_area_name': group_name}

            folder_name_def = fill_tags2string(
                folder_name_raw, self.alg_template_tags, alg_template_values_step)
            file_name_def = fill_tags2string(
                file_name_raw, self.alg_template_tags, alg_template_values_step)
            file_path_def = os.path.join(folder_name_def, file_name_def)

            file_name_obj[group_key] = {}
            file_name_obj[group_key] = file_path_def

        return file_name_obj

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to read geographical data file
    def read_geo_basin(self, tag_data='basin'):

        group_obj = {}
        for src_key, src_file in self.src_collection_basin.items():

            for group_key, group_data in self.structure_data_group.items():
                group_basin = group_data[tag_data]

                if group_key not in list(group_obj.keys()):
                    group_obj[group_key] = {}

                for basin_name in group_basin:

                    alg_template_values = {"basin_name": basin_name}

                    file_basin = fill_tags2string(
                        src_file, self.alg_template_tags, alg_template_values)

                    if os.path.exists(os.path.join(file_basin)):
                        if file_basin.endswith('txt'):
                            data_basin = get_file_raster(file_basin)

                            da_basin = create_darray_2d(data_basin['values'],
                                                        data_basin['longitude'], data_basin['latitude'],
                                                        coord_name_x='west_east', coord_name_y='south_north',
                                                        dim_name_x='west_east', dim_name_y='south_north')

                            if basin_name not in list(group_obj[group_key].keys()):
                                dset_basin = da_basin.to_dataset(name=src_key)
                                group_obj[group_key][basin_name] = {}
                                group_obj[group_key][basin_name] = dset_basin
                            else:
                                dset_tmp = group_obj[group_key][basin_name]
                                dset_tmp[src_key] = da_basin
                                group_obj[group_key][basin_name] = dset_tmp
                        else:
                            logging.error(' ===> Geographical data file ' + file_basin + ' not available')
                            raise IOError('Check your configuration file')
                    else:
                        logging.warning(' ===> Geographical data file ' + file_basin + ' not available')

        return group_obj
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to read geographical data file of region
    def read_geo_data_region(self):

        group_obj = {}
        for src_key, src_file in self.src_collection_geo.items():
            if os.path.exists(os.path.join(src_file)):

                if src_file.endswith('.shp'):

                    dst_file_region = self.file_path_region
                    convert_shp_2_tiff(src_file, dst_file_region,
                                       pixel_size=0.001, burn_value=1, epsg=4326)

                    da_frame, _, _ = read_file_tiff(dst_file_region)

                    group_obj[self.region_tag] = da_frame

                else:
                    logging.error(' ===> Geographical data file ' + src_file + ' not available')
                    raise IOError('Check your configuration file')
            else:
                logging.error(' ===> Geographical data file ' + src_file + ' not available')
                raise IOError('Check your configuration file')

        return group_obj
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to read geographical data file of alert area
    def read_geo_data_alert_area(self):

        data_group = self.structure_data_group

        group_obj = {}
        for src_key, src_file in self.src_collection_geo.items():
            if os.path.exists(os.path.join(src_file)):

                if src_file.endswith('.shp'):

                    shape_dframe, shape_collections, shape_geoms = read_file_shp(src_file)

                    dst_file_region = self.file_path_region
                    convert_shp_2_tiff(src_file, dst_file_region,
                                       pixel_size=0.001, burn_value=1, epsg=4326)

                    for shape_data, (group_key, group_data) in zip(shape_collections, data_group.items()):

                        shape_name = shape_data[0]
                        shape_polygons = shape_data[1]

                        assert shape_name == group_data['name']

                        file_path_vector = self.file_path_alert_area_vector_obj[group_key]
                        file_path_raster = self.file_path_alert_area_raster_obj[group_key]

                        convert_polygons_2_shp(shape_polygons, file_path_vector, template_file=dst_file_region)

                        convert_shp_2_tiff(file_path_vector, file_path_raster,
                                           pixel_size=0.001, burn_value=1, epsg=4326)

                        da_frame, _, _ = read_file_tiff(file_path_raster)

                        group_obj[group_key] = da_frame
                else:
                    logging.error(' ===> Geographical data file ' + src_file + ' not available')
                    raise IOError('Check your configuration file')
            else:
                logging.error(' ===> Geographical data file ' + src_file + ' not available')
                raise IOError('Check your configuration file')

        return group_obj

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize geographical data
    def organize_data(self):
        pass
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
