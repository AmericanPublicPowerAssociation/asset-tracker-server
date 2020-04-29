import json
from collections import namedtuple

from dss_server.converters import get_line
from dss_server.fixtures import substation, substation_1, meter_1, meter_2
from dss_server.opendss import LINE
from pyramid.config import Configurator
from pyramid.view import view_config

from dss_server.models import Asset, ElectricalConnection, LineType, engine
from sqlalchemy.orm import sessionmaker

asset_conn =  namedtuple('Asset', ['element', 'buses', 'conns'])

@view_config(
  route_name='list_assets',
  renderer='json'
)
def list_assets(request):
    Session = sessionmaker(bind=engine)
    db = Session()

    assets = []
    for line in db.query(Asset).filter(Asset.type_code == LINE):
        buses = []
        conns = []
        connections = db.query(ElectricalConnection).filter(ElectricalConnection.asset_id == line.id)

        for conn in connections:
            buses.append(db.query(Asset).filter(Asset.id == conn.bus_id).one())
            conns.append(conn)

        assets.append(asset_conn(line, buses, conns))
    (line1, line2, line3, *_) = assets
    with open('./assetTypes.json') as f:
        spec = json.load(f)

    db.close()

    return {
      'spec': spec,
        'assets': [
          substation,
          substation_1,
          meter_1,
          meter_2,
          get_line(line1.element, line1.buses, line1.conns),
          get_line(line2.element, line2.buses, line2.conns),
          get_line(line3.element, line3.buses, line3.conns),
        ]
    }


def main(global_config, **settings):
    with Configurator() as config:
        config.add_route('list_assets', '/assets.json')
        config.scan()
        return config.make_wsgi_app()