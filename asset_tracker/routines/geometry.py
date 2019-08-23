from shapely.geometry import GeometryCollection


def get_bounding_box(assets):
    geometries = [_.geometry for _ in assets if _.geometry]
    if len(geometries) == 0:
        return ()
    geometry_collection = GeometryCollection(geometries)
    if len(geometries) == 1:
        # Buffer 1 decimal degree if there is only one geometry
        geometry_collection = geometry_collection.buffer(1)
    [
        minimum_longitude, minimum_latitude,
        maximum_longitude, maximum_latitude,
    ] = geometry_collection.bounds
    return (
        (minimum_longitude, minimum_latitude),
        (maximum_longitude, maximum_latitude),
    )
