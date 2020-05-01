from networkx import nx
from os.path import dirname, join, abspath
import json
import asset_tracker

from asset_tracker.routines.geometry import get_length

script_dir = dirname(abspath(__file__))
rel_path = 'datasets/assetTypes.json'
abs_path = join(dirname(script_dir), rel_path)
f = open(abs_path)

data_types = json.load(f)
types = {entry['id']: entry for entry in data_types}

TRANSFORMER = 't'
METER = 'm'
LINE = 'l'
LINECODE = 'linecode'
GENERATOR = 'g'
STATION = 'S'
SUBSTATION = 's'
LOAD = 'load'
BUS = 'bus'
STORAGE = 'o'
SWITCH = 'x'
POWERQUALITY = 'q'
POWERQUALITY_CAPACITOR = f'${POWERQUALITY}c'
POWERQUALITY_REGULATOR = f'${POWERQUALITY}r'

DEFAULT_SOURCE_BUS = 'SourceBus'

DIRECTION_UNI = 'UNIDIRECTIONAL'
DIRECTION_MULTI = 'BIDIRECTIONAL'

DEFAULT = 'DEFAULT'


def comment(text):
    return f'// {text}'


def to_matrix(lists):
    rows = [' '.join(map(str, entry)) for entry in lists]
    matrix = ' | '.join(rows)
    return f'[{matrix}]'


class AssetMixin:
    @property
    def id(self):
        return self.asset.name

    @property
    def name(self):
        return self.asset.name


class LineCode(AssetMixin):
    type = LINECODE

    def __init__(self, name, phases, rmatrix, xmatrix, frequency=60, units='mi'):
        self.title = name
        self.phases = phases
        self.rmatrix = rmatrix
        self.xmatrix = xmatrix
        self.frequency = frequency
        self.units = units

    def __str__(self):
        rmatrix = to_matrix(self.rmatrix)
        xmatrix = to_matrix(self.xmatrix)

        return (f'New Linecode.{self.title} nphases={self.phases} basefreq={self.frequency} normamps=419.0 ' 
                f'rmatrix=({rmatrix}) xmatrix=({xmatrix})')


BASIC_LC = LineCode('lc', phases=2, rmatrix=[[0.25], [0.06, 0.25]], xmatrix=[[0.80], [0.60, 0.8011]])


class Line(AssetMixin):
    type = LINE
    direction = DIRECTION_MULTI

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None
        self.bus2 = None

    def __str__(self):
        line = f'New Line.{self.id} phases=2 x1=0.1 r1=0.01 linecode=lc'
        if self.bus1:
            line += f' Bus1={self.bus1.id} '

        if self.bus2:
            line += f' Bus2={self.bus2.id}'

        meters = (get_length(self.asset) if self.asset.geometry else 300)
        line += f' length={meters/1000}'

        return line


class Switch(AssetMixin):
    type = SWITCH
    direction = DIRECTION_MULTI

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None
        self.bus2 = None

    def __str__(self):
        command = f'New Line.{self.id} phases=3 Switch=y'
        if self.bus1:
            command += f' Bus1={self.bus1.id} '

        if self.bus2:
            command += f' Bus2={self.bus2.id}'

        return command


class Meter(AssetMixin):
    type = METER
    direction = DIRECTION_UNI

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None

    def __str__(self):
        command = f'New Load.Load_{self.asset.name} phases=2 conn=wye model=5 '

        if self.bus1:
            command += f' Bus1={self.bus1.id}'

        attributes = self.asset.attributes
        if attributes:
            KV = attributes.get('KV', False)
            KW = attributes.get('KW', False)
            if KV:
                command += f' kV={KV} '

            if KW:
                command += f' kW={KW} '

        command += ' kvar=100'

        return command


class PowerQuality(AssetMixin):
    type = POWERQUALITY
    direction = DIRECTION_MULTI

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None
        self.bus2 = None

    def __str__(self):
        command = ''
        attributes = self.asset.attributes

        if self.asset.type_id == POWERQUALITY_REGULATOR:
            command = (f'New regcontrol.{self.id} transformer={self.bus1.id}\n'
                       '~ winding=2  vreg=122  band=2  ptratio=20 ctprim=700  R=3 X=9')

        if self.asset.type_id == POWERQUALITY_CAPACITOR:
            command = f'New Capacitor.{self.id} Bus1={self.bus1.id}'

            if self.bus2:
                command += f' bus2={self.bus2.id}'

            if attributes:
                kv = attributes.get('KV', False)
                kvar = attributes.get('KVAR', False)
                phases = attributes.get('phases', 2)
                local_kv = kv if kv else ''
                local_kvar = kvar if kvar else ''

                command += f' phases={phases} kV={local_kv} kvar={local_kvar}'

        return command


class Storage(AssetMixin):
    type = STORAGE
    direction = DIRECTION_UNI

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None

    def __str__(self):
        command = (f'New Loadshape.{self.id}Shape  npts=24  interval=1 '
                   'mult=[0 0 -1 -1 -1 -1 -1 0 0 0 0 0 0 0 0 0 0.8 0.9 0.94 1 0.94 0 0 0]\n'
                   f'New Storage.{self.id} phases=3 kWrated=350 kWhrated=2000 dispmode=follow daily={self.id}Shape')
        if self.bus1:
            command += f' bus1={self.bus1.id}'
        attributes = self.asset.attributes
        if attributes:
            KV = attributes.get('KV', False)
            if KV:
                command += f' kV={KV} '

        return command


class Transformer(AssetMixin):
    type = TRANSFORMER
    direction = DIRECTION_MULTI

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None
        self.bus2 = None

    def __str__(self):
        command = f'New Transformer.{self.asset.id} Phases=3 Windings=2 xhl=(8 1000 /)'
        if self.asset.attributes:
            kv = self.asset.attributes.get('KV', False)
            kv_high = self.asset.attributes.get('HIGHVOLT', kv)
            kv_med = self.asset.attributes.get('MEDVOLT', kv)

            kva = self.asset.attributes.get('KVA', False)
            kva_high = self.asset.attributes.get('KVAHIGH', kva)
            kva_med = self.asset.attributes.get('KVAMED', kva)

            if self.bus1:
                local_kv = kv_high if kv_high else ''
                local_kva = kva_high if kva_high else ''
                command += f'~ wdg=1 bus={self.bus1.id} conn=delta kV={local_kv} kva={local_kva} %r=(.5 1000 /)\n'
            if self.bus2:
                local_kv = kv_med if kv_med else ''
                local_kva = kva_med if kva_med else ''
                command += f'~ wdg=2 bus={self.bus2.id} conn=wye kV={local_kv} kva={local_kva} %r=(.5 1000 /)'

        return command


class Circuit(AssetMixin):
    type = ''
    bus2 = 'SourceBus'
    direction = DIRECTION_UNI

    def __init__(self, name):
        self.asset = name
        self.bus1 = Bus(node=self, name=DEFAULT_SOURCE_BUS)

    @property
    def id(self):
        return self.asset

    @property
    def name(self):
        return self.id

    def __str__(self):
        return f'New Circuit.{self.asset} basekv=13.8 pu=1.000 bus1=SourceBus'


class Generator(AssetMixin):
    type = GENERATOR
    direction = DIRECTION_UNI

    def __init__(self, asset):
        self.asset = asset
        self.bus1 = None

    def __str__(self):
        command = f'New Generator.{self.id} model=3'
        if self.bus1:
            command += f' bus1={self.bus1.id}'
        attributes = self.asset.attributes
        if attributes:
            KV = attributes.get('KV', False)
            KW = attributes.get('KW', False)
            if KV:
                command += f' kV={KV} '

            if KW:
                command += f' kW={KW} maxkvar={KW * 2} minkvar={KW / 10}'

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


class Substation(Transformer):
    type = SUBSTATION


class Bus(AssetMixin):
    def __init__(self, node, name):
        self.node = node
        self._name = name

    @property
    def id(self):
        if self._name:
            return self._name
        return f'bus_{self.node.name}'

    def __str__(self):
        return f'AddBusMarker Bus={self.id} code=36 color=Red size=2'


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

    if asset.type_id[0] == SWITCH:
        current_node = Switch(asset)
        index[SWITCH]['assets'].append(current_node)

    if asset.type_id[0] == STORAGE:
        current_node = Storage(asset)
        index[STORAGE]['assets'].append(current_node)

    if asset.type_id[0] == POWERQUALITY:
        current_node = PowerQuality(asset)
        index[POWERQUALITY]['assets'].append(current_node)

    # if asset.type_id[0] == STATION:
    #     current_node = Station(asset)
    #     create_bus(current_node, index=index, graph=graph, invisible=True)
    #     index[STATION]['assets'].append(current_node)
    #
    # if asset.type_id[0] == SUBSTATION:
    #     current_node = Substation(asset)
    #     create_bus(current_node, index=index, graph=graph, invisible=True)
    #     index[SUBSTATION]['assets'].append(current_node)

    graph.add_node(asset.name, instance=asset, translate=current_node, type_id=types[asset.type_id[0]])

    return current_node


def create_bus(node, name=None):
    return Bus(node, name)


def create_connection(asset1, asset2, graph):
    graph.add_edge(asset1.id, asset2.id)


def get_node(asset, graph, index):
    current_node = node_existence(asset.name, graph=graph)

    if not current_node:
        current_node = create_node(asset, index=index, graph=graph)

    return current_node


def have_free_bus1(element):
    return element.bus1 is None


def have_free_bus2(element):
    return element.bus2 is None


def connect(E1, E2, index):
    if E1.direction is DIRECTION_UNI and E2.direction is DIRECTION_UNI and have_free_bus1(E2):
        E2.bus1 = E1.bus1
        return True

    if (E1.direction is DIRECTION_UNI) and (E2.direction is DIRECTION_MULTI) and have_free_bus1(E2):
        E2.bus1 = E1.bus1
        return True

    if E1.direction is DIRECTION_MULTI and E2.direction is DIRECTION_UNI and have_free_bus1(E2):
        E2.bus1 = E1.bus1
        return True

    if E1.direction is DIRECTION_MULTI and E2.direction is DIRECTION_MULTI:
        if have_free_bus2(E1) and have_free_bus1(E2):
            bus = create_bus(E1)
            E2.bus1 = bus
            E1.bus2 = bus
            return True

        if have_free_bus2(E1) and not have_free_bus1(E2):
            E1.bus2 = E2.bus1
            return True

    return False