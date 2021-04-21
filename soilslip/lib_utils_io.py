# -------------------------------------------------------------------------------------
# Libraries
import logging
import tempfile
import os
import json
import pickle
import rasterio
import gzip
import struct

import numpy as np
import geopandas as gpd
import pandas as pd
import xarray as xr
import scipy.io

from copy import deepcopy
from rasterio.transform import Affine
from osgeo import gdal, gdalconst

logging.getLogger('rasterio').setLevel(logging.WARNING)

# Debug
import matplotlib.pylab as plt

# Default settings
proj_default_wkt='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
# -------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Method to unzip file
def unzip_filename(file_name_zip, file_name_unzip):

    file_handle_zip = gzip.GzipFile(file_name_zip, "rb")
    file_handle_unzip = open(file_name_unzip, "wb")

    file_data_unzip = file_handle_zip.read()
    file_handle_unzip.write(file_data_unzip)

    file_handle_zip.close()
    file_handle_unzip.close()

# --------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a tmp name
def create_filename_tmp(prefix='tmp_', suffix='.tiff', folder=None):

    if folder is None:
        folder = '/tmp'

    with tempfile.NamedTemporaryFile(dir=folder, prefix=prefix, suffix=suffix, delete=False) as tmp:
        temp_file_name = tmp.name
    return temp_file_name
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read shape file
def read_file_shp(file_name):

    file_dframe = gpd.read_file(file_name)
    file_geoms = ((feature['geometry'], 1) for feature in file_dframe.iterfeatures())
    return file_dframe

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file binary
def read_file_binary(file_name, data_geo, scale_factor=10000):

    file_handle = open(file_name, 'rb')

    data_n = data_geo.shape[0] * data_geo.shape[1]
    data_format = 'i' * data_n

    file_obj = file_handle.read(-1)
    data_array = struct.unpack(data_format, file_obj)

    data_grid = np.reshape(data_array, (data_geo.shape[0], data_geo.shape[1]), order='F')

    data_grid = np.float32(data_grid / scale_factor)

    data_grid[data_geo < 0] = np.nan
    data_grid[0, :] = np.nan
    data_grid[-1, :] = np.nan
    data_grid[:, 0] = np.nan
    data_grid[:, -1] = np.nan

    # Debug
    # plt.figure()
    # plt.imshow(data_grid)
    # plt.colorbar()
    # plt.show()

    return data_grid

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write file csv
def write_file_csv(file_name, file_data, file_sep=',', file_header=True, file_index=True, file_format='%.3f'):
    if isinstance(file_data, pd.DataFrame):
        file_data.to_csv(file_name, sep=file_sep, header=file_header, index=file_index, float_format=file_format)
    else:
        logging.error(' ===> Variable type for writing csv file not supported')
        raise NotImplementedError('Case not implemented yet')
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read csv and transform to a dataframe
def convert_file_csv2df(file_name):
    file_df = pd.read_csv(file_name)

    if 'Unnamed' in list(file_df.columns)[0]:
        file_df.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
        file_df['time'] = pd.to_datetime(file_df['time'], format="%Y-%m-%d")
        file_df.set_index('time', inplace=True)

    return file_df
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file csv
def read_file_csv(file_name, file_time=None, file_header=None, file_format=None,
                  file_sep=',', file_skiprows=1, file_time_format='%Y%m%d%H%M',
                  scale_factor_longitude=10, scale_factor_latitude=10, scale_factor_data=1):

    if file_header is None:
        file_header = ['code', 'name', 'longitude', 'latitude', 'time', 'data']
    if file_format is None:
        file_format = {'code': str, 'name': str, 'longitude': float, 'latitude': float, 'data': float}

    file_dframe = pd.read_table(file_name, sep=file_sep, names=file_header, skiprows=file_skiprows)

    file_dframe = file_dframe.replace(to_replace=',', value='.', regex=True)
    file_dframe = file_dframe.replace(to_replace=':', value=file_sep, regex=True)

    file_dframe = file_dframe.dropna(axis='columns', how='all')

    if (file_dframe.columns.__len__() == 1) and (file_dframe.columns.__len__() != file_header.__len__()):

        logging.warning(' ===> The format of csv file ' + file_name +
                        ' is not in the expected format. Try to correct due to wrong file delimiter')

        file_cols_name = list(file_dframe.columns)[0]
        file_n_expected = file_header.__len__()

        file_dframe_tmp = file_dframe[file_cols_name].str.split(file_sep, file_n_expected, expand=True)
        file_dframe_tmp.columns = file_header

        file_dframe = deepcopy(file_dframe_tmp)

    elif file_dframe.columns.__len__() == file_header.__len__():
        pass
    else:
        logging.error(' ===> Parser of csv file ' + file_name + ' failed')
        raise IOError('Check the format of csv file')

    #values = [float(i) for i in file_dframe['data'].values]

    file_dframe = file_dframe.reset_index()
    file_dframe = file_dframe.set_index('time')

    file_dframe = file_dframe.astype(file_format)

    file_dframe.index = pd.to_datetime(file_dframe.index, format=file_time_format)
    file_dframe['longitude'] = file_dframe['longitude'] / scale_factor_longitude
    file_dframe['latitude'] = file_dframe['latitude'] / scale_factor_latitude
    file_dframe['data'] = file_dframe['data'] / scale_factor_data

    if file_time is not None:
        if file_time in file_dframe.index:
            file_dframe_select = file_dframe.loc[file_time]
        else:
            file_dframe_select = None
            logging.warning(' ===> Time ' + str(file_time) + ' is not available in file: ' + file_name)
    else:
        file_dframe_select = file_dframe

    return file_dframe_select

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write file tiff
def write_file_tif(file_name, file_data, file_wide, file_high, file_geotrans, file_proj,
                   file_metadata=None,
                   file_format=gdalconst.GDT_Float32):

    if not isinstance(file_data, list):
        file_data = [file_data]

    if file_metadata is None:
        file_metadata = {'description_field': 'data'}
    if not isinstance(file_metadata, list):
        file_metadata = [file_metadata] * file_data.__len__()

    if isinstance(file_geotrans, Affine):
        file_geotrans = file_geotrans.to_gdal()

    file_n = file_data.__len__()
    dset_handle = gdal.GetDriverByName('GTiff').Create(file_name, file_wide, file_high, file_n, file_format,
                                                       options=['COMPRESS=DEFLATE'])
    dset_handle.SetGeoTransform(file_geotrans)
    dset_handle.SetProjection(file_proj)

    for file_id, (file_data_step, file_metadata_step) in enumerate(zip(file_data, file_metadata)):
        dset_handle.GetRasterBand(file_id + 1).WriteArray(file_data_step)
        dset_handle.GetRasterBand(file_id + 1).SetMetadata(file_metadata_step)
    del dset_handle
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file tif
def read_file_tif(file_name):

    file_handle = rasterio.open(file_name)
    file_proj = file_handle.crs.wkt
    file_geotrans = file_handle.transform

    file_tags = file_handle.tags()
    file_bands = file_handle.count
    file_metadata = file_handle.profile

    if file_bands == 1:
        file_data = file_handle.read(1)
    elif file_bands > 1:
        file_data = []
        for band_id in range(0, file_bands):
            file_data_tmp = file_handle.read(band_id + 1)
            file_data.append(file_data_tmp)
    else:
        logging.error(' ===> File multi-band are not supported')
        raise NotImplementedError('File multi-band not implemented yet')

    return file_data, file_proj, file_geotrans
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file json
def read_file_json(file_name):
    env_ws = {}
    for env_item, env_value in os.environ.items():
        env_ws[env_item] = env_value

    with open(file_name, "r") as file_handle:
        json_block = []
        for file_row in file_handle:

            for env_key, env_value in env_ws.items():
                env_tag = '$' + env_key
                if env_tag in file_row:
                    env_value = env_value.strip("'\\'")
                    file_row = file_row.replace(env_tag, env_value)
                    file_row = file_row.replace('//', '/')

            # Add the line to our JSON block
            json_block.append(file_row)

            # Check whether we closed our JSON block
            if file_row.startswith('}'):
                # Do something with the JSON dictionary
                json_dict = json.loads(''.join(json_block))
                # Start a new block
                json_block = []

    return json_dict

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a data array
def create_darray_2d(data, geo_x, geo_y, geo_1d=True, time=None,
                     coord_name_x='west_east', coord_name_y='south_north', coord_name_time='time',
                     dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                     dims_order=None):

    if dims_order is None:
        dims_order = [dim_name_y, dim_name_x]
    if time is not None:
        dims_order = [dim_name_y, dim_name_x, dim_name_time]

    if geo_1d:
        if geo_x.shape.__len__() == 2:
            geo_x = geo_x[0, :]
        if geo_y.shape.__len__() == 2:
            geo_y = geo_y[:, 0]

        if time is None:
            data_da = xr.DataArray(data,
                                   dims=dims_order,
                                   coords={coord_name_x: (dim_name_x, geo_x),
                                           coord_name_y: (dim_name_y, geo_y)})
        elif isinstance(time, pd.DatetimeIndex):

            if data.shape.__len__() == 2:
                data = np.expand_dims(data, axis=-1)

            data_da = xr.DataArray(data,
                                   dims=dims_order,
                                   coords={coord_name_x: (dim_name_x, geo_x),
                                           coord_name_y: (dim_name_y, geo_y),
                                           coord_name_time: (dim_name_time, time)})
        else:
            logging.error(' ===> Time obj is in wrong format')
            raise IOError('Variable time format not valid')

    else:
        logging.error(' ===> Longitude and Latitude must be 1d')
        raise IOError('Variable shape is not valid')

    return data_da
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a data array
def create_darray_3d(data, time, geo_x, geo_y, geo_1d=True,
                     coord_name_x='west_east', coord_name_y='south_north', coord_name_time='time',
                     dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                     dims_order=None):

    if dims_order is None:
        dims_order = [dim_name_y, dim_name_x, dim_name_time]

    if geo_1d:
        if geo_x.shape.__len__() == 2:
            geo_x = geo_x[0, :]
        if geo_y.shape.__len__() == 2:
            geo_y = geo_y[:, 0]

        data_da = xr.DataArray(data,
                               dims=dims_order,
                               coords={coord_name_time: (dim_name_time, time),
                                       coord_name_x: (dim_name_x, geo_x),
                                       coord_name_y: (dim_name_y, geo_y)})
    else:
        logging.error(' ===> Longitude and Latitude must be 1d')
        raise IOError('Variable shape is not valid')

    return data_da
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to select attributes
def select_attrs(var_attrs_raw):

    var_attrs_select = {}
    if var_attrs_raw:
        for var_key, var_value in var_attrs_raw.items():
            if var_value is not None:
                if var_key not in attrs_decoded:
                    if isinstance(var_value, list):
                        var_string = [str(value) for value in var_value]
                        var_value = ','.join(var_string)
                    if isinstance(var_value, dict):
                        var_string = json.dumps(var_value)
                        var_value = var_string
                    if var_key in attrs_reserved:
                        var_value = None
                    if var_value is not None:
                        var_attrs_select[var_key] = var_value

    return var_attrs_select
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create dataset
def create_dset(var_data_values,
                var_geo_values, var_geo_x, var_geo_y,
                var_data_time=None,
                var_data_name='variable', var_geo_name='terrain', var_data_attrs=None, var_geo_attrs=None,
                var_geo_1d=False,
                coord_name_x='longitude', coord_name_y='latitude', coord_name_time='time',
                dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                dims_order_2d=None, dims_order_3d=None):

    var_geo_x_tmp = var_geo_x
    var_geo_y_tmp = var_geo_y
    if var_geo_1d:
        if (var_geo_x.shape.__len__() == 2) and (var_geo_y.shape.__len__() == 2):
            var_geo_x_tmp = var_geo_x[0, :]
            var_geo_y_tmp = var_geo_y[:, 0]
    else:
        if (var_geo_x.shape.__len__() == 1) and (var_geo_y.shape.__len__() == 1):
            var_geo_x_tmp, var_geo_y_tmp = np.meshgrid(var_geo_x, var_geo_y)

    if dims_order_2d is None:
        dims_order_2d = [dim_name_y, dim_name_x]
    if dims_order_3d is None:
        dims_order_3d = [dim_name_y, dim_name_x, dim_name_time]

    if not isinstance(var_data_time, list):
        var_data_time = [var_data_time]

    if var_data_values.shape.__len__() == 2:
        var_dset = xr.Dataset(coords={coord_name_time: ([dim_name_time], var_data_time)})
        var_dset.coords[coord_name_time] = var_dset.coords[coord_name_time].astype('datetime64[ns]')
    elif var_data_values.shape.__len__() == 3:
        var_dset = xr.Dataset(coords={coord_name_x: ([dim_name_y, dim_name_x], var_geo_x_tmp),
                                      coord_name_y: ([dim_name_y, dim_name_x], np.flipud(var_geo_y_tmp)),
                                      coord_name_time: ([dim_name_time], var_data_time)})
        var_dset.coords[coord_name_time] = var_dset.coords[coord_name_time].astype('datetime64[ns]')
    else:
        raise NotImplemented

    var_da_terrain = xr.DataArray(np.flipud(var_geo_values),  name=var_geo_name,
                                  dims=dims_order_2d,
                                  coords={coord_name_x: ([dim_name_y, dim_name_x], var_geo_x_tmp),
                                          coord_name_y: ([dim_name_y, dim_name_x], np.flipud(var_geo_y_tmp))})
    var_dset[var_geo_name] = var_da_terrain
    var_geo_attrs_select = select_attrs(var_geo_attrs)

    if var_geo_attrs_select is not None:
        var_dset[var_geo_name].attrs = var_geo_attrs_select

    if var_data_values.shape.__len__() == 2:
        var_da_data = xr.DataArray(np.flipud(var_data_values), name=var_data_name,
                                   dims=dims_order_2d,
                                   coords={coord_name_x: ([dim_name_y, dim_name_x], var_geo_x_tmp),
                                           coord_name_y: ([dim_name_y, dim_name_x], np.flipud(var_geo_y_tmp))})
    elif var_data_values.shape.__len__() == 3:
        var_da_data = xr.DataArray(np.flipud(var_data_values), name=var_data_name,
                                   dims=dims_order_3d,
                                   coords={coord_name_time: ([dim_name_time], var_data_time),
                                           coord_name_x: ([dim_name_y, dim_name_x], var_geo_x_tmp),
                                           coord_name_y: ([dim_name_y, dim_name_x], np.flipud(var_geo_y_tmp))})
    else:
        raise NotImplemented

    if var_data_attrs is not None:
        if attr_valid_range in list(var_data_attrs.keys()):
            valid_range = var_data_attrs[attr_valid_range]
            var_da_data = clip_map(var_da_data, valid_range)

        if attr_missing_value in list(var_data_attrs.keys()):
            missing_value = var_data_attrs[attr_missing_value]
            var_da_data = var_da_data.where(var_da_terrain > 0, other=missing_value)

    var_dset[var_data_name] = var_da_data
    if var_data_attrs is not None:
        var_data_attrs_select = select_attrs(var_data_attrs)
    else:
        var_data_attrs_select = None

    if var_data_attrs_select is not None:
        var_dset[var_data_name].attrs = var_data_attrs_select

    return var_dset

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write dataset
def write_dset(file_name,
               dset_data, dset_mode='w', dset_engine='h5netcdf', dset_compression=0, dset_format='NETCDF4',
               dim_key_time='time', no_data=-9999.0):

    dset_encoded = dict(zlib=True, complevel=dset_compression)

    dset_encoding = {}
    for var_name in dset_data.data_vars:

        if isinstance(var_name, bytes):
            var_name_upd = var_name.decode("utf-8")
            dset_data = var_name.rename({var_name: var_name_upd})
            var_name = var_name_upd

        var_data = dset_data[var_name]
        var_attrs = dset_data[var_name].attrs
        if len(var_data.dims) > 0:
            dset_encoding[var_name] = deepcopy(dset_encoded)

        if var_attrs:
            for attr_key, attr_value in var_attrs.items():
                if attr_key in attrs_decoded:

                    dset_encoding[var_name][attr_key] = {}

                    if isinstance(attr_value, list):
                        attr_string = [str(value) for value in attr_value]
                        attr_value = ','.join(attr_string)

                    dset_encoding[var_name][attr_key] = attr_value

            if '_FillValue' not in list(dset_encoding[var_name].keys()):
                dset_encoding[var_name]['_FillValue'] = no_data

    if dim_key_time in list(dset_data.coords):
        dset_encoding[dim_key_time] = {'calendar': 'gregorian'}

    dset_data.to_netcdf(path=file_name, format=dset_format, mode=dset_mode, engine=dset_engine,
                        encoding=dset_encoding)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read data obj
def read_obj(file_name):
    if os.path.exists(file_name):
        data = pickle.load(open(file_name, "rb"))
    else:
        data = None
    return data
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write data obj
def write_obj(file_name, data):
    if os.path.exists(file_name):
        os.remove(file_name)
    with open(file_name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read mat obj
def read_mat(file_name):
    if os.path.exists(file_name):
        data = scipy.io.loadmat(file_name)
    else:
        data = None
    return data
# -------------------------------------------------------------------------------------
