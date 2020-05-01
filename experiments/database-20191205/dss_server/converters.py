from typing import Sequence

from dss_server.models import Asset, ElectricalConnection

def get_bus(bus: Asset):
    return {
        'id': bus.name or bus.id,
        'attributes': bus.attributes or {}
    }

def getElectricalConnection(conn: ElectricalConnection):
    return {
        'asset_id': conn.asset_id,
        'bus_id': conn.bus_id,
        'attributes': conn.attributes
    }

def get_line(asset: Asset, buses: Sequence[Asset], connections: Sequence[ElectricalConnection]):
    return {
        'id': asset.id,
        'type': asset.type_code,
        'name': asset.name or asset.id,
        'attributes': asset.attributes,
        'busByIndex': {bus.id: get_bus(bus) for bus in buses},
        'electricalConnections': [getElectricalConnection(con) for con in connections]
    }