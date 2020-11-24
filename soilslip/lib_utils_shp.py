# -------------------------------------------------------------------------------------
# Libraries
import logging
import rasterio
import ogr

import geopandas as gpd
logging.getLogger("fiona").setLevel(logging.WARNING)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read shape file
def read_file_shp(file_name):

    shape_dframe = gpd.read_file(file_name)
    shape_geoms = ((feature['geometry'], 1) for feature in shape_dframe.iterfeatures())

    shape_collections = list(shape_dframe.values)

    return shape_dframe, shape_collections, shape_geoms
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Convert polygons to shape file
def convert_polygons_2_shp(shape_polygon, shape_file, template_file=None):

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
# -------------------------------------------------------------------------------------
