"""
Class Features

Name:          driver_data_io_geo_point_weather_stations
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210411'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os
import numpy as np
import pandas as pd

import shapefile
from shapely.geometry import shape, Point

from scipy.spatial import cKDTree

from lib_utils_io import write_obj, read_obj
from lib_utils_geo import get_file_point, km_2_degree
from lib_utils_system import fill_tags2string, make_folder

# Debug
# import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverGeo
class DriverGeoPoint:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, src_dict, dst_dict=None, group_data=None,
                 flag_point_data_src='weather_stations_data',  flag_grid_data='geo_data',
                 flag_point_data_dst='weather_stations_data',
                 alg_template_tags=None, flag_geo_updating=True,
                 search_radius_km=10):

        self.flag_point_data_src = flag_point_data_src
        self.flag_point_data_dst = flag_point_data_dst
        self.flag_grid_data = flag_grid_data

        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.point_registry_tag = 'registry'
        self.point_alert_area_tree_tag = 'alert_area_tree'
        self.grid_vector_tag = 'alert_area_vector'

        self.point_code_tag = 'code'
        self.point_name_tag = 'name'
        self.point_longitude_tag = 'longitude'
        self.point_latitude_tag = 'latitude'
        self.point_alert_area_tag = 'alert_area'

        self.group_data = group_data
        self.alg_template_tags = alg_template_tags

        self.flag_geo_updating = flag_geo_updating
        self.search_radius_km = search_radius_km

        self.file_name_point_registry_src = src_dict[
            self.flag_point_data_src][self.point_registry_tag][self.file_name_tag]
        self.folder_name_point_registry_src = src_dict[
            self.flag_point_data_src][self.point_registry_tag][self.folder_name_tag]
        self.file_path_point_registry_src = os.path.join(
            self.folder_name_point_registry_src, self.file_name_point_registry_src)

        self.file_name_point_registry_dst = dst_dict[
            self.flag_point_data_dst][self.point_registry_tag][self.file_name_tag]
        self.folder_name_point_registry_dst = dst_dict[
            self.flag_point_data_dst][self.point_registry_tag][self.folder_name_tag]
        self.file_path_point_registry_dst = os.path.join(
            self.folder_name_point_registry_dst, self.file_name_point_registry_dst)

        self.file_name_point_alert_area_tree_dst = dst_dict[
            self.flag_point_data_dst][self.point_alert_area_tree_tag][self.file_name_tag]
        self.folder_name_point_alert_area_tree_dst = dst_dict[
            self.flag_point_data_dst][self.point_alert_area_tree_tag][self.folder_name_tag]
        self.file_path_point_alert_area_tree_dst = os.path.join(
            self.folder_name_point_alert_area_tree_dst, self.file_name_point_alert_area_tree_dst)

        self.file_name_grid = dst_dict[self.flag_grid_data][self.grid_vector_tag][self.file_name_tag]
        self.folder_name_grid = dst_dict[self.flag_grid_data][self.grid_vector_tag][self.folder_name_tag]
        self.file_path_grid = self.collect_file_obj(self.folder_name_grid, self.file_name_grid)

        self.search_radius_degree = km_2_degree(self.search_radius_km)

        if self.flag_geo_updating:
            if os.path.exists(self.file_path_point_registry_dst):
                os.remove(self.file_path_point_registry_dst)

        logging.info(' -----> Define geo points registry ... ')
        if not os.path.exists(self.file_path_point_registry_dst):
            df_geo_point = self.dset_geo_point = self.read_geo_point()
            self.df_geo_point = self.join_geo_point2grid(df_geo_point)
            make_folder(self.folder_name_point_registry_dst)
            self.df_geo_point.to_csv(self.file_path_point_registry_dst)
            logging.info(' -----> Define geo points registry ... DONE')
        else:
            self.df_geo_point = pd.read_csv(self.file_path_point_registry_dst)
            logging.info(' -----> Define geo points registry ... LOADED. Datasets was previously computed.')

        self.tag_sep = ':'

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect file
    def collect_file_obj(self, folder_name_raw, file_name_raw):

        data_group = self.group_data

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
    # Method to define the domain for each point
    def join_geo_point2grid(self, point_dframe):

        point_x = point_dframe[self.point_longitude_tag].values
        point_y = point_dframe[self.point_latitude_tag].values

        point_domain_array = np.array([None] * point_dframe.shape[0], dtype=object)
        point_polygon = {}
        for var_name, file_name in self.file_path_grid.items():

            if os.path.exists(file_name):
                # read the shapefile
                file_handle = shapefile.Reader(file_name)
                # get the shapes
                file_shapes = file_handle.shapes()
                # build a shapely polygon from your shape
                file_polygon = shape(file_shapes[0])

                for i, (x, y) in enumerate(zip(point_x, point_y)):
                    var_point = Point(x, y)
                    if file_polygon.contains(var_point):
                        point_domain_array[i] = var_name

                if var_name not in list(point_polygon.keys()):
                    point_polygon[var_name] = file_polygon

            else:
                logging.error(' ===> Alert area shapefile "' + file_name + '" is not available')
                raise IOError('File not found!')

        point_domain_list = point_domain_array.tolist()

        for point_id, point_aa in enumerate(point_domain_list):
            if point_aa is None:

                code = point_dframe[self.point_code_tag].values[point_id]
                x = point_dframe[self.point_longitude_tag].values[point_id]
                y = point_dframe[self.point_latitude_tag].values[point_id]

                logging.warning(' ===> Reference area for point "' +
                                code + '" is not defined. Try using a polygon build around the point')
                var_polygon = Point(x, y).buffer(self.search_radius_degree)

                for var_name, file_polygon in point_polygon.items():
                    if file_polygon.intersects(var_polygon):
                        point_domain_array[point_id] = var_name

                if point_domain_array[point_id] is None:
                    logging.warning(' ===> Reference area for point "' + code + '" is undefined. Use default assignment')
                else:
                    logging.warning(' ===> Reference area for point "' + code + '" is correctly defined')

        point_domain_list = point_domain_array.tolist()
        point_dframe[self.point_alert_area_tag] = point_domain_list

        # DEFAULT STATIC CONDITION TO FIX POINTS OUTSIDE THE DOMAINS (IF NEEDED AFTER POINT AND POLYGONS APPROACHES)
        if point_dframe.loc[point_dframe[self.point_code_tag] == 'ALTOM', self.point_alert_area_tag].values[0] is None:
            point_dframe.loc[point_dframe[self.point_code_tag] == 'ALTOM', self.point_alert_area_tag] = "alert_area_a"
        if point_dframe.loc[point_dframe[self.point_code_tag] == 'CASON', self.point_alert_area_tag].values[0] is None:
            point_dframe.loc[point_dframe[self.point_code_tag] == 'CASON', self.point_alert_area_tag] = "alert_area_c"

        return point_dframe
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to read weather stations data file
    def read_geo_point(self):

        # Read geo points db
        if os.path.exists(self.file_path_point_registry_src):
            point_dframe = get_file_point(self.file_path_point_registry_src, file_sep=';')
        else:
            logging.error(' ===> Weather stations database file "' +
                          self.file_path_point_registry_src + '" is not available')
            raise IOError('File not found!')

        # Adjust geo points dataframe
        point_dframe = point_dframe.reset_index()
        point_dframe = point_dframe.drop(columns=['index'])
        point_dframe.index.name = 'index'

        return point_dframe
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize data
    def organize_data(self):

        # Starting info
        logging.info(' ----> Organize weather stations point information ... ')

        df_point = self.df_geo_point
        max_distance = self.search_radius_degree
        inf_distance = float("inf")

        file_path_point = self.file_path_point_alert_area_tree_dst
        flag_geo_updating = self.flag_geo_updating

        if flag_geo_updating:
            if os.path.exists(file_path_point):
                os.remove(file_path_point)

        if not os.path.exists(file_path_point):

            code_points = df_point[self.point_code_tag].values
            name_points = df_point[self.point_name_tag].values
            lats_points = df_point[self.point_latitude_tag].values
            lons_points = df_point[self.point_longitude_tag].values
            aa_points = df_point[self.point_alert_area_tag].values

            coord_points = np.dstack([lats_points.ravel(), lons_points.ravel()])[0]
            coord_tree = cKDTree(coord_points)

            weather_stations_collections = {}
            for code_point, aa_point, coord_point in zip(code_points, aa_points, coord_points):

                distances, indices = coord_tree.query(
                    coord_point, len(coord_points), p=2, distance_upper_bound=max_distance)

                code_points_neighbors = []
                name_points_neighbors = []
                coord_points_neighbors = []
                lats_points_neighbors = []
                lons_points_neighbors = []
                aa_points_neighbors = []
                for index, distance in zip(indices, distances):
                    if distance == inf_distance:
                        break
                    coord_points_neighbors.append(coord_points[index])
                    code_points_neighbors.append(code_points[index])
                    name_points_neighbors.append(name_points[index])
                    lons_points_neighbors.append(lons_points[index])
                    lats_points_neighbors.append(lats_points[index])
                    aa_points_neighbors.append(aa_points[index])

                coord_dict = {
                    self.point_code_tag: code_points_neighbors, self.point_name_tag: name_points_neighbors,
                    self.point_latitude_tag: lats_points_neighbors, self.point_longitude_tag: lons_points_neighbors,
                    self.point_alert_area_tag: aa_points_neighbors
                }
                coord_dframe = pd.DataFrame(data=coord_dict)

                if aa_point not in list(weather_stations_collections.keys()):
                    weather_stations_collections[aa_point] = {}
                weather_stations_collections[aa_point][code_point] = coord_dframe

            folder_name, file_name = os.path.split(file_path_point)
            make_folder(folder_name)
            write_obj(file_path_point, weather_stations_collections)

            # Ending info
            logging.info(' ----> Organize weather stations point information ... DONE')

        else:
            # Ending info
            weather_stations_collections = read_obj(file_path_point)
            logging.info(' ----> Organize weather stations point information ... LOADED. '
                         'Datasets was previously computed.')

        return weather_stations_collections

# -------------------------------------------------------------------------------------
