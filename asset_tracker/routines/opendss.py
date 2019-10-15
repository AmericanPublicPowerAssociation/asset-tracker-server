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
        return self.asset.name


class Line(AssetMixin):
    type = LINE

    def __init__(self, asset):
        self.asset = asset
        self.connected = set()
        self.buses = set()
        self.bus = None

    def __str__(self):
        buses = list(self.buses)
        bus1 = len(buses) >= 1
        bus2 = len(buses) >= 2

        line = f'New Line.{self.id} phases=1 x0=0.1 r0=0.1'
        if bus2:
            line += f' Bus1={buses[0].id} Bus2={buses[1].id}'

        elif bus1:
            line += f' Bus1=SourceBus Bus2={buses[0].id}'

        return line


class Meter(AssetMixin):
    type = METER

    def __init__(self, asset):
        self.asset = asset
        self.connected = set()
        self.buses = set()

    def __str__(self):
        command = ''
        if self.connected:
            bus = list(self.connected)[0].bus
            command = f'New Load.Load_{self.asset.name} Bus1={bus.id} phases=1 '
            attributes = self.asset.attributes
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
        self.connected = set()
        self.buses = set()

    def __str__(self):
        if not self.connected:
            return ''

        buses = list(self.buses)
        bus2 = len(buses) >= 2

        if bus2:
            return f'New Transformer.{self.id} Buses=[{self.buses[0].id}, {self.buses[1].id}]'

        return f'New Transformer.{self.id} Buses=[{self.buses[0].id}]'


class Circuit(AssetMixin):
    type = ''
    bus2 = 'SourceBus'

    def __init__(self, name):
        self.asset = name

    def __str__(self):
        return f'New Circuit.{self.asset} basekv=10 bus1=SourceBus phases=1 ! (Vsource.Source is active circuit element)'


class Generator(AssetMixin):
    type = GENERATOR

    def __init__(self, asset):
        self.asset = asset
        self.connected = set()
        self.buses = set()

    def __str__(self):
        command = ''
        connected = list(self.connected)
        if self.connected:
            command = f'New Generator.{self.id} phases=1 bus1={connected[0].bus.id}'
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
        self.connected = set()

    def __str__(self):
        command = f'New Vsource.{self.asset.id} bus1={self.bus1.id}'
        KV = self.asset.attributes.get('KV', False)

        if KV:
            command += f' basekv={KV} '

        return command


class Bus(AssetMixin):
    def __init__(self, node):
        self.node = node
        self.connected = set()

    @property
    def id(self):
        return f'bus_{self.node.asset.name}'

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

    source = asset1
    destination = asset2
    if not hasattr(source, 'bus'):
        source = asset2
        destination = asset1

    if source.bus:
        bus = source.bus
    else:
        bus = create_bus(source, index, graph)
        source.bus = bus

    if connection['direction'] == DIRECTION_MULTI:
        graph.add_edge(source.id, bus.id)
        graph.add_edge(bus.id, destination.id)
    else:
        graph.add_edge(source.id, destination.id)

    bus.connected.update([asset2,asset1])
    asset1.connected.add(asset2)
    asset1.buses.add(bus)
    asset2.connected.add(asset1)
    asset2.buses.add(bus)

    return source, destination, bus, connection

