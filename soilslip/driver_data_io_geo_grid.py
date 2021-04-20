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

from lib_analysis_interpolation_grid import interp_grid2index

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
                 flag_geo_region_data='geo_region',
                 flag_geo_alert_area_data='geo_alert_area', flag_index_alert_area_data='index_alert_area',
                 flag_geo_basin_data='geo_basin',
                 flag_geo_updating=True):

        self.flag_geo_data = flag_geo_data
        self.flag_basin_data = flag_basin_data

        self.flag_geo_region_data = flag_geo_region_data
        self.flag_geo_alert_area_data = flag_geo_alert_area_data
        self.flag_index_alert_area_data = flag_index_alert_area_data
        self.flag_geo_basin_data = flag_geo_basin_data

        self.alg_template_tags = alg_template_tags
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.region_tag = 'region'
        self.alert_area_vector_tag = 'alert_area_vector'
        self.alert_area_raster_tag = 'alert_area_raster'
        self.alert_area_index_tag = 'alert_area_index'

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
        self.dst_dict_geo_alert_area_index = dst_dict[self.flag_geo_data][self.alert_area_index_tag]
        self.dst_dict_basin = dst_dict[self.flag_basin_data]

        self.file_path_region = os.path.join(self.dst_dict_geo_region[self.folder_name_tag],
                                             self.dst_dict_geo_region[self.file_name_tag])

        self.file_path_alert_area_vector_obj = self.collect_file_obj(
            self.dst_dict_geo_alert_area_vector[self.folder_name_tag], self.dst_dict_geo_alert_area_vector[self.file_name_tag])
        self.file_path_alert_area_raster_obj = self.collect_file_obj(
            self.dst_dict_geo_alert_area_raster[self.folder_name_tag], self.dst_dict_geo_alert_area_raster[self.file_name_tag])
        self.file_path_alert_area_index_obj = self.collect_file_obj(
            self.dst_dict_geo_alert_area_raster[self.folder_name_tag], self.dst_dict_geo_alert_area_index[self.file_name_tag])

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
    # Method to compute index data of alert area
    def compute_index_data_alert_area(self):

        logging.info(' -----> Compute alert area index ... ')

        file_path_alert_area_index = self.file_path_alert_area_index_obj

        geoy_region_1d = self.dset_geo_region[self.region_tag]['south_north'].values
        geox_region_1d = self.dset_geo_region[self.region_tag]['west_east'].values
        geox_region_2d, geoy_region_2d = np.meshgrid(geox_region_1d, geoy_region_1d)

        dset_geo_alert_area = self.dset_geo_alert_area

        dset_index_alert_area = {}
        for group_key, group_data in self.structure_data_group.items():

            logging.info(' ------> Alert area ' + group_key + ' ... ')

            file_path = file_path_alert_area_index[group_key]
            geo_alert_area = dset_geo_alert_area[group_key]

            if self.flag_geo_updating:
                if os.path.exists(file_path):
                    os.remove(file_path)

            if not os.path.exists(file_path):

                geox_alert_area_1d = geo_alert_area['west_east'].values
                geoy_alert_area_1d = geo_alert_area['south_north'].values
                geox_alert_area_2d, geoy_alert_area_2d = np.meshgrid(geox_alert_area_1d, geoy_alert_area_1d)

                index_alert_area_2d = interp_grid2index(geox_region_2d, geoy_region_2d,
                                                        geox_alert_area_2d, geoy_alert_area_2d,
                                                        nodata=-9999, interp_method='nearest')

                folder_name, file_name = os.path.split(file_path)
                make_folder(folder_name)

                write_obj(file_path, index_alert_area_2d)

                logging.info(' ------> Alert area ' + group_key + ' ... DONE')

            else:
                index_alert_area_2d = read_obj(file_path)
                logging.info(' ------> Alert area ' + group_key + ' ... LOADED. Datasets was previously computed.')

            dset_index_alert_area[group_key] = index_alert_area_2d

        logging.info(' -----> Compute alert area index ... DONE')

        return dset_index_alert_area

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize geographical data
    def organize_data(self):

        # Starting info
        logging.info(' ----> Organize grid information ... ')

        # Compute alert area index
        dset_index_alert_area = self.compute_index_data_alert_area()

        # Create geo data collections
        geo_data_collections = {self.flag_geo_region_data: self.dset_geo_region,
                                self.flag_geo_alert_area_data: self.dset_geo_alert_area,
                                self.flag_index_alert_area_data: dset_index_alert_area,
                                self.flag_geo_basin_data: self.dset_basins}

        # Ending info
        logging.info(' ----> Organize grid information ... DONE')

        return geo_data_collections
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
