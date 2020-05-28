import utm
from geotable.projections import (
    LONGITUDE_LATITUDE_PROJ4,
    get_transform_shapely_geometry,
    get_utm_proj4)


def get_line_length_in_meters(line_geometry):
    point_geometry = line_geometry.centroid
    point_longitude = point_geometry.x
    point_latitude = point_geometry.y
    utm_zone_number, utm_zone_letter = utm.from_latlon(
        point_latitude, point_longitude)[-2:]
    utm_proj4 = get_utm_proj4(utm_zone_number, utm_zone_letter)
    f = get_transform_shapely_geometry(LONGITUDE_LATITUDE_PROJ4, utm_proj4)
    utm_line_geometry = f(line_geometry)
    return utm_line_geometry.length
