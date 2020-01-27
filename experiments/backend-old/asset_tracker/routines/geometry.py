import utm
from geotable import get_utm_proj4, LONGITUDE_LATITUDE_PROJ4, get_transform_shapely_geometry
from shapely import wkt
from shapely.geometry import GeometryCollection


def get_bounding_box(assets):
    geometries = [_.geometry for _ in assets if _.geometry]
    if len(geometries) == 0:
        return ()
    geometry_collection = GeometryCollection(geometries)
    if len(geometries) == 1:
        # Buffer one decimal degree if there is only one geometry
        geometry_collection = geometry_collection.buffer(1)
    [
        minimum_longitude, minimum_latitude,
        maximum_longitude, maximum_latitude,
    ] = geometry_collection.bounds
    return (
        (minimum_longitude, minimum_latitude),
        (maximum_longitude, maximum_latitude),
    )

def get_length(asset):
    # CrossCompute: https://crosscompute.com/r/dP6dXhdcMOG8pxm5UuBYBenxeikZdhwG
    line_geometry = asset.geometry
    point_geometry = line_geometry.centroid
    point_longitude = point_geometry.x
    point_latitude = point_geometry.y
    utm_zone_number, utm_zone_letter = utm.from_latlon(point_latitude, point_longitude)[-2:]
    utm_proj4 = get_utm_proj4(utm_zone_number, utm_zone_letter)
    f = get_transform_shapely_geometry(LONGITUDE_LATITUDE_PROJ4, utm_proj4)
    utm_line_geometry = f(line_geometry)
    return utm_line_geometry.length
