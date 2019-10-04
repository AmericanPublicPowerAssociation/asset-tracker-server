from networkx import nx
import json


f = open('asset_tracker/datasets/assetTypes.json')

data_types = json.load(f)
types = {entry['id']: entry for entry in data_types}

TRANSFORMER = 't'
METER = 'm'
LINE = 'l'
GENERATOR = 'g'
STATION = 'S'
SUBSTATION = 's'
LOAD = 'load'
BUS = 'bus'


DEFAULT_SOURCE_BUS = 'SourceBus'


ELEM_2_ELEM = 'ELEMENT to ELEMENT'
BUS_2_BUS = 'BUS to BUS'

DIRECTION_UNI = 'UNIDIRECTIONAL'
DIRECTION_MULTI = 'BIDIRECTIONAL'

DEFAULT = 'DEFAULT'

CONNECTION_MATRIX = {
    (TRANSFORMER + LINE): {
        'type': BUS_2_BUS,
        'direction': DIRECTION_MULTI,
        'bus1': LINE,
        'bus2': TRANSFORMER
    },
    (GENERATOR + LINE): {
        'type': BUS_2_BUS,
        'direction': DIRECTION_MULTI,
        'bus1': GENERATOR,
        'bus2': LINE
    },
    (LINE + GENERATOR): {
        'type': BUS_2_BUS,
        'direction': DIRECTION_MULTI,
        'bus1': GENERATOR,
        'bus2': LINE
    },
    (METER + LINE): {
        'type': ELEM_2_ELEM,
        'direction': DIRECTION_UNI,
        'bus1': METER,
        'bus2': LINE
    },
    (LINE+METER): {
        'type': ELEM_2_ELEM,
        'direction': DIRECTION_UNI,
        'bus1': METER,
        'bus2': LINE
    },
    DEFAULT: {
        'type': BUS_2_BUS,
        'direction': DIRECTION_MULTI,
        'bus1': None,
        'bus2': None
    }
}


def comment(text):
    return f'// {text}'


class AssetMixin:
    @property
    def id(self):
        return self.asset.id


class Line(AssetMixin):
    type = LINE

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None
        self.bus2 = None

    def __str__(self):
        if not self.bus1:
            line = f'New Line.{self.id} Bus1={DEFAULT_SOURCE_BUS}'
        else:
            line = f'New Line.{self.id} Bus1={self.bus1.id}'
        if self.bus2:
            line += f' Bus2={self.bus2.id}'

        return line


class Meter(AssetMixin):
    type = METER

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None
        self.bus2 = None

    def __str__(self):
        element = types[self.bus1.type]['name']
        return f'New EnergyMeter.{self.asset.id} Element={element}.{self.bus1.id} Terminal=1  Action=Save localonly=no'


class Load(AssetMixin):
    def __init__(self, asset):
        self.asset = asset

    def __str__(self):
        bus = self.asset.bus1.bus1.id if self.asset.bus1.bus1 else DEFAULT_SOURCE_BUS
        command = f'New Load.Load_{self.asset.bus1.id} Bus1={bus} '
        attributes = self.asset.asset.attributes
        if attributes:
            KV = attributes.get('KV', False)
            KW = attributes.get('KW', False)
            if KV:
                command += f' kV={KV} '

            if KW:
                command += f' kW={KW} '

        return command


class Transformer(AssetMixin):
    type = TRANSFORMER

    def __init__(self, asset):
        self.asset = asset
        self.bus2 = None
        self.bus1 = None

    def __str__(self):
        if self.bus1:
            if not self.bus2:
                return f'New Transformer.{self.id} Buses=[{DEFAULT_SOURCE_BUS}]'
            return f'New Transformer.{self.id} Buses=[{self.bus1.id}, {self.bus2.id}]'
        if not self.bus2:
            return f'New Transformer.{self.id} Buses=[{DEFAULT_SOURCE_BUS}]'
        return f'New Transformer.{self.id} Buses=[{DEFAULT_SOURCE_BUS}, {self.bus2.id}]'


class Circuit(AssetMixin):
    type = ''
    bus2 = 'SourceBus'

    def __init__(self, name):
        self.asset = name

    def __str__(self):
        return f'New Circuit.{self.asset} ! (Vsource.Source is active circuit element)'


class Generator(AssetMixin):
    type = GENERATOR

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None
        self.bus2 = None

    def __str__(self):
        command = f'New Generator.{self.id} bus1={self.bus1.id}'
        attributes = self.asset.attributes
        if attributes:
            KV = attributes.get('KV', False)
            KW = attributes.get('KW', False)
            if KV:
                command += f' kV={KV} '

            if KW:
                command += f' kW={KW} '

        return command


class Station(AssetMixin):
    type = STATION

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None

    def __str__(self):
        command = f'New Vsource.{self.asset.id} bus1={self.bus1.id}'
        KV = self.asset.attributes.get('KV', False)

        if KV:
            command += f' basekv={KV} '


class Substation(AssetMixin):
    type = SUBSTATION

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None

    def __str__(self):
        command = f'New Vsource.{self.asset.id} bus1={self.bus1.id}'
        KV = self.asset.attributes.get('KV', False)

        if KV:
            command += f' basekv={KV} '

        return command


class Bus(AssetMixin):
    def __init__(self, node):
        self.node = node

    @property
    def id(self):
        return f'bus_{self.node.asset.id}'

    def __str__(self):
        return  f'AddBusMarker Bus={self.id} code=36 color=Red size=2'


def node_existence(id, graph):
    val = graph.node.get(id, False)
    if val:
        return val['translate']


def create_node(asset, index, graph=None):
    current_node = None

    if asset.type_id[0] == TRANSFORMER:
        current_node = Transformer(asset)
        index[TRANSFORMER]['assets'].append(current_node)


    if asset.type_id[0] == LINE:
        current_node = Line(asset)
        index[LINE]['assets'].append(current_node)

    if asset.type_id[0] == METER:
        current_node = Meter(asset)
        index[METER]['assets'].append(current_node)
        load = Load(current_node)
        index[LOAD]['assets'].append(load)
    if asset.type_id[0] == GENERATOR:
        current_node = Generator(asset)
        index[GENERATOR]['assets'].append(current_node)

    # if asset.type_id[0] == STATION:
    #     current_node = Station(asset)
    #     create_bus(current_node, index=index, graph=graph, invisible=True)
    #     index[STATION]['assets'].append(current_node)
    #
    # if asset.type_id[0] == SUBSTATION:
    #     current_node = Substation(asset)
    #     create_bus(current_node, index=index, graph=graph, invisible=True)
    #     index[SUBSTATION]['assets'].append(current_node)

    graph.add_node(asset.id, instance=asset, translate=current_node, type_id=types[asset.type_id[0]])

    return current_node


def create_bus(node, index, graph, invisible=False):
    bus = Bus(node)
    node.bus1 = bus
    if not invisible:
        graph.add_node(bus.id, instance=None, translate=bus)
        graph.add_edge(bus.id, node.id)
        index[BUS]['assets'].append(bus)

    return bus


def create_connection(asset1, asset2, index, graph, matrix=CONNECTION_MATRIX):
    type1 = asset1.type
    type2 = asset2.type
    connection = matrix.get(f'{type1}{type2}', matrix[DEFAULT])
    bus = None

    if connection['bus1'] == type2:
        source = asset2
        destination = asset1
    else:
        source = asset1
        destination = asset2

    if connection['type'] == ELEM_2_ELEM:
        source.bus1 = destination
        if connection['direction'] == DIRECTION_MULTI:
            destination.bus2 = source
    else:
        bus = source.bus1
        if not bus:
            bus = create_bus(source, index, graph)

        source.bus2 = bus

        if connection['direction'] == DIRECTION_MULTI:
            destination.bus1 = bus

    graph.add_edge(source.id, destination.id)

    return source, destination, bus, connection

