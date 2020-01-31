from sqlalchemy.orm import selectinload
from pytest import mark
from asset_tracker.routines.geometry import get_bounding_box
from asset_tracker.models import Asset


class TestGeometryBoundingBox(object):
    coords = {
        'one': [[74.0060, 40.7128]],
        'many': [
            [-73.92540591006002, 40.879898414161204],
            [-73.90254961197161, 40.70979268356925],
            [-73.90269247777564, 40.71087563023107],
            [-73.84743045332118, 40.78651101016763],
        ]
    }

    def test_empty_asset_list(self):
        bounding_box = get_bounding_box([])
        assert bounding_box == ()

    @mark.parametrize("coord_amt", ['one', 'many'])
    def test_populated_asset_list(self, coord_amt):
        assets = []
        coords = self.__class__.coords[coord_amt]
        for coord in coords:
            asset = Asset()
            asset.location = coord
            assets.append(asset)
        bounding_box = get_bounding_box(assets)
        min_lon, min_lat = bounding_box[0]
        max_lon, max_lat = bounding_box[1]
        assert max_lon - min_lon > 0
        assert max_lat - min_lat > 0
        assert min_lon > -180 and min_lon < 180
        assert min_lat > -90 and min_lat < 90
        assert max_lon > -180 and max_lon < 180
        assert max_lat > -90 and max_lat < 90
