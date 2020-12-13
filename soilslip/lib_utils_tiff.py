# -------------------------------------------------------------------------------------
# Libraries
import logging
import warnings
import os
import ogr
import gdal

import osr

import numpy as np
import geopandas as gpd
import rasterio
from rasterio import features
from osgeo import ogr

from shapely.geometry import shape

from lib_utils_io import create_filename_tmp, create_darray_2d, write_file_tif

# Default settings
proj_default_wkt='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to save data values in geotiff format
def save_file_tiff(file_name, file_data, file_geo_x, file_geo_y, file_metadata=None, file_epsg_code='EPSG:32632'):

    if file_metadata is None:
        file_metadata = {'description': 'data'}

    file_data_height, file_data_width = file_data.shape

    file_geo_x_west = np.min(file_geo_x)
    file_geo_x_east = np.max(file_geo_x)
    file_geo_y_south = np.min(file_geo_y)
    file_geo_y_north = np.max(file_geo_y)

    file_data_transform = rasterio.transform.from_bounds(
        file_geo_x_west, file_geo_y_south, file_geo_x_east, file_geo_y_north,
        file_data_width, file_data_height)

    if not isinstance(file_data, list):
        file_data = [file_data]

    write_file_tif(file_name, file_data,
                   file_data_width, file_data_height, file_data_transform, file_epsg_code,
                   file_metadata=file_metadata)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read tiff file
def read_file_tiff(file_name):

    if os.path.exists(file_name):
        if file_name.endswith('tif') or file_name.endswith('.tiff'):

            dset = rasterio.open(file_name)
            bounds = dset.bounds
            res = dset.res
            transform = dset.transform
            data = dset.read()
            values = data[0, :, :]
            if dset.crs is None:
                proj = proj_default_wkt
            else:
                proj = dset.crs.wkt
            geotrans = dset.transform

            decimal_round = 7

            dims = values.shape
            high = dims[0]
            wide = dims[1]

            center_right = bounds.right - (res[0] / 2)
            center_left = bounds.left + (res[0] / 2)
            center_top = bounds.top - (res[1] / 2)
            center_bottom = bounds.bottom + (res[1] / 2)

            if center_bottom > center_top:
                center_bottom_tmp = center_top
                center_top_tmp = center_bottom
                center_bottom = center_bottom_tmp
                center_top = center_top_tmp

                values = np.flipud(values)

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

            da_frame = create_darray_2d(values, lons, lats, coord_name_x='west_east', coord_name_y='south_north',
                                        dim_name_x='west_east', dim_name_y='south_north')

        else:
            logging.error(' ===> Geographical file ' + file_name + ' format unknown')
            raise NotImplementedError('File type reader not implemented yet')
    else:
        logging.error(' ===> Geographical file ' + file_name + ' not found')
        raise IOError('Geographical file location or name is wrong')

    return da_frame, proj, geotrans
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Convert data to tiff
def convert_polygons_2_tiff(shape_polygon, shape_file, raster_file, template_file=None,
                            pixel_size=0.001, burn_value=1, epsg=4326):

    template_handle = rasterio.open(template_file)
    metadata = template_handle.meta.copy()
    metadata.update(compress='lzw')

    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(shape_file)

    if shape_polygon.type == 'MultiPolygon':
        layer = ds.CreateLayer('', None, ogr.wkbMultiPolygon)
    elif shape_polygon.type == 'Polygon':
        layer = ds.CreateLayer('', None, ogr.wkbPolygon)
    else:
        raise IOError('Shape type not implemented yet')
    defn = layer.GetLayerDefn()
    feat = ogr.Feature(defn)

    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkb(shape_polygon.wkb)
    feat.SetGeometry(geom)

    layer.CreateFeature(feat)
    feat = geom = None  # destroy these

    # Save and close everything
    ds = layer = feat = geom = None

    convert_shp_2_tiff(shape_file, raster_file,
                       pixel_size=pixel_size, burn_value=burn_value, epsg=epsg)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to transform shape file to tiff
def convert_shp_2_tiff(shape_file, raster_file, pixel_size=0.1, burn_value=1, epsg=4326):

    input_shp = ogr.Open(shape_file)
    shp_layer = input_shp.GetLayer()

    # get extent values to set size of output raster.
    x_min, x_max, y_min, y_max = shp_layer.GetExtent()

    # calculate size/resolution of the raster.
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)

    # get GeoTiff driver by
    image_type = 'GTiff'
    driver = gdal.GetDriverByName(image_type)

    # passing the filename, x and y direction resolution, no. of bands, new raster.
    raster_handle = driver.Create(raster_file, x_res, y_res, 1, gdal.GDT_Byte)

    # transforms between pixel raster space to projection coordinate space.
    raster_handle.SetGeoTransform((x_min, pixel_size, 0, y_min, 0, pixel_size))

    # get required raster band.
    band = raster_handle.GetRasterBand(1)

    # assign no data value to empty cells.
    no_data_value = -9999
    band.SetNoDataValue(no_data_value)
    band.FlushCache()

    # adding a spatial reference
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromEPSG(epsg)
    raster_handle.SetProjection(raster_srs.ExportToWkt())

    # main conversion method
    ds = gdal.Rasterize(raster_handle, shape_file, burnValues=[burn_value])
    ds = None
# -------------------------------------------------------------------------------------
