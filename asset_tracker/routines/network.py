import networkx as nx
import numpy as np


def get_downstream_meters(asset):
    downstream_meter_asset_ids = []
    asset_id = asset.id
    g = get_graph(asset)
    # Get all connected sources
    source_asset_ids = [node_id for node_id, node_d in g.nodes(
        data=True) if node_d['is_power_source']]
    # Get all connected meters
    meter_asset_ids = [node_id for node_id, node_d in g.nodes(
        data=True) if node_d['primary_type_id'] == 'm']
    # Compute path from the nearest power source to the asset
    source_asset_path = get_path(g, source_asset_ids, asset_id)
    if not source_asset_path:
        return []
    # Get downstream meter ids
    for meter_asset_id in meter_asset_ids:
        asset_meter_path = get_path(g, [asset_id], meter_asset_id)
        if not asset_meter_path:
            continue
        overlapping_node_ids = set(source_asset_path).intersection(
            asset_meter_path)
        if overlapping_node_ids:
            continue
        downstream_meter_asset_ids.append(meter_asset_id)
    # Get downstream meters
    return [g.nodes[_]['asset'] for _ in downstream_meter_asset_ids]


def get_graph(asset):
    g = nx.Graph()
    old_asset_ids = []
    new_assets = [asset]

    def add_node(a):
        g.add_node(
            a.id,
            primary_type_id=a.primary_type_id,
            is_power_source=a.is_power_source,
            asset=a)

    while new_assets:
        new_asset = new_assets.pop()
        new_asset_id = new_asset.id
        old_asset_ids.append(new_asset_id)
        for connected_asset in new_asset.connections:
            connected_asset_id = connected_asset.id
            if connected_asset_id in old_asset_ids:
                continue
            add_node(new_asset)
            add_node(connected_asset)
            g.add_edge(new_asset_id, connected_asset_id)
            new_assets.append(connected_asset)
    return g


def get_path(g, source_asset_ids, target_asset_id):
    paths = []
    for source_asset_id in source_asset_ids:
        path = nx.shortest_path(g, source_asset_id, target_asset_id)
        paths.append(path)
    if not paths:
        return ()
    path_lengths = [len(_) for _ in paths]
    shortest_path_index = np.argmin(path_lengths)
    return paths[shortest_path_index][:-1]
