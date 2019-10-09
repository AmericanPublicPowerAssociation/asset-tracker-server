from sqlalchemy.orm import selectinload
from asset_tracker.routines.geometry import get_bounding_box
from asset_tracker.models import Asset


class TestRoutinesGeometry(object):
    def test_get_bounding_box_empty_asset_list(self):
        bounding_box = get_bounding_box([])
        assert bounding_box == ()

    def test_get_bounding_box_asset(self, db):
        assets = db.query(Asset).options(
            selectinload(Asset.parents),
            selectinload(Asset.children),
            selectinload(Asset.connections),
        ).all()
        bounding_box = get_bounding_box(assets)
        min_coord = bounding_box[0]
        max_coord = bounding_box[1]
        assert min_coord != max_coord
        assert min_coord > max_coord
        assert min_coord[0] > -180 and min_coord[0] < 180
        assert min_coord[1] > -90 and min_coord[1] < 90
        assert max_coord[0] > -180 and max_coord[0] < 180
        assert max_coord[1] > -90 and max_coord[1] < 90
        
