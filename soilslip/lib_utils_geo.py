# -------------------------------------------------------------------------------------
# Libraries
import logging
import os
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd

# Debug
import matplotlib.pylab as plt
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get shape file
def get_file_shp(file_name):

    file_dframe = gpd.read_file(file_name)
    file_geoms = ((feature['geometry'], 1) for feature in file_dframe.iterfeatures())
    return file_dframe

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get file point
def get_file_point(file_name, file_header=None, file_subset_columns=None, file_subset_format=None,
                   file_pivot_column='code',
                   # file_points_column='point',
                   file_geo_x_column='longitude', file_geo_y_column='latitude',
                   file_sep=',', file_skiprows=1,
                   scale_factor_longitude=10, scale_factor_latitude=10):

    if file_header is None:
        file_header = ['code', 'name', 'longitude', 'latitude', 'time', 'data']

    if file_subset_columns is None:
        file_subset_columns = ['code', 'name', 'longitude', 'latitude']
    if file_subset_format is None:
        file_subset_format = {'code': str, 'name': str, 'longitude': float, 'latitude': float}

    file_dframe = pd.read_table(file_name, sep=file_sep, names=file_header, skiprows=file_skiprows)

    file_dframe = file_dframe.replace(to_replace=',', value='.', regex=True)
    file_dframe = file_dframe.replace(to_replace=':', value=file_sep, regex=True)

    file_dframe = file_dframe.dropna(axis='columns', how='all')
    file_dframe = file_dframe[file_subset_columns]
    file_dframe = file_dframe.drop_duplicates(subset=[file_pivot_column], keep='first')
    file_dframe = file_dframe.astype(file_subset_format)

    file_dframe[file_geo_x_column] = file_dframe[file_geo_x_column] / scale_factor_longitude
    file_dframe[file_geo_y_column] = file_dframe[file_geo_y_column] / scale_factor_latitude

    # file_dframe[file_points_column] = file_dframe[[file_geo_y_column, file_geo_x_column]].apply(tuple, axis=1)

    return file_dframe

# -------------------------------------------------------------------------------------):


# -------------------------------------------------------------------------------------
# Method to get a raster ascii file
def get_file_raster(file_name):

    dset = rasterio.open(file_name)
    bounds = dset.bounds
    res = dset.res
    transform = dset.transform
    data = dset.read()
    values = data[0, :, :]

    decimal_round = 7

    center_right = bounds.right - (res[0] / 2)
    center_left = bounds.left + (res[0] / 2)
    center_top = bounds.top - (res[1] / 2)
    center_bottom = bounds.bottom + (res[1] / 2)

    lon = np.arange(center_left, center_right + np.abs(res[0] / 2), np.abs(res[0]), float)
    lat = np.arange(center_bottom, center_top + np.abs(res[0] / 2), np.abs(res[1]), float)
    lons, lats = np.meshgrid(lon, lat)

    min_lon_round = round(np.min(lons), decimal_round)
    max_lon_round = round(np.max(lons), decimal_round)
    min_lat_round = round(np.min(lats), decimal_round)
    max_lat_round = round(np.max(lats), decimal_round)

    center_right_round = round(center_right, decimal_round)
    center_left_round = round(center_left, decimal_round)
    center_bottom_round = round(center_bottom, decimal_round)
    center_top_round = round(center_top, decimal_round)

    assert min_lon_round == center_left_round
    assert max_lon_round == center_right_round
    assert min_lat_round == center_bottom_round
    assert max_lat_round == center_top_round

    lats = np.flipud(lats)

    obj = {'values': values, 'longitude': lons, 'latitude': lats,
           'transform': transform,
           'bb_left': bounds.left, 'bb_right': bounds.right,
           'bb_top': bounds.top, 'bb_bottom': bounds.bottom,
           'res_lon': res[0], 'res_lat': res[1]}

    return obj
# -------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------
# Method to convert curve number to s (vmax)
def convert_cn2s(data_cn, data_terrain):

    data_s = (1000.0 / data_cn - 10) * 25.4
    data_s[data_cn <= 0] = np.nan
    data_s[data_cn > 100] = np.nan

    data_s[(data_terrain >= 0) & (data_s < 1.0)] = 1.0

    data_s[data_s < 0] = 0.0

    data_s[data_terrain < 0] = np.nan

    data_s[0, :] = np.nan
    data_s[-1, :] = np.nan
    data_s[:, 0] = np.nan
    data_s[:, -1] = np.nan

    # Debug
    # plt.figure()
    # plt.imshow(data_s)
    # plt.colorbar()
    # plt.show()

    return data_s
# ------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------
# Method to convert decimal degrees to km (2)
def degree_2_km(deg):
    earth_radius = 6378.1370
    km = deg * (np.pi * earth_radius) / 180
    return km
# ------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------
# Method to convert km to decimal degrees
def km_2_degree(km):
    earth_radius = 6378.1370
    deg = 180 * km / (np.pi * earth_radius)
    return deg
# ------------------------------------------------------------------------------------
