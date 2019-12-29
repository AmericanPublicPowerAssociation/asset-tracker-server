import sys
from collections import namedtuple
from getopt import getopt

try:
    from .models import Asset, ElectricalConnection, db, LineType
    from .opendss import Line, Switch, Meter, Regulator, Capacitor, Transformer, Generator, Circuit, LineCode
except ModuleNotFoundError:
    from models import Asset, ElectricalConnection, db, LineType
    from opendss import Line, Switch, Meter, Regulator, Capacitor, Transformer, Generator, Circuit, LineCode


ASSET = (Line, Switch, Meter, Regulator, Capacitor, Transformer, Generator)
Conn = namedtuple("Conn", ["bus", "element", 'asset', 'wired'])


def comment(text):
    return f'// {text}'


def generate_dss_script(db, root='voltageSource', allowed_assets=ASSET):
    buses = {}
    for conn in db.query(ElectricalConnection):
        asset = None
        if conn.asset_id not in buses.keys():
            current = []
        else:
            current = buses[conn.asset_id]

        element = db.query(Asset).filter(Asset.id == conn.asset_id).one()
        bus = db.query(Asset).filter(Asset.id == conn.bus_id).one()

        if element.id == root:
            asset = Circuit
        else:
            for AssetClass in allowed_assets:
                if element.type_code == AssetClass.type:
                    asset = AssetClass

        current.append(Conn(bus, element, asset, conn))
        buses[conn.asset_id] = current

    stations = []
    substation = []
    linecodes = []
    lines = []
    regulators = []
    transformers = []
    capacitors = []
    loads = []
    generators = []
    lcs = []

    ELEMENTS = (
            {'title': 'Station', 'assets': stations},
            {'title': 'Generators', 'assets': generators},
            {'title': 'Transformers', 'assets': transformers},
            {'title': 'Line Codes', 'assets': lcs},
            {'title': 'Lines', 'assets': lines},
            {'title': 'Loads', 'assets': loads},
            # {'title': 'Storage', 'assets': storage},
            {'title': 'Capacitor', 'assets': capacitors},
            {'title': 'Regulator', 'assets': regulators},
    )

    circuit = []
    circuit_head = 'clear\n'
    circuit_head += 'New Circuit.IEEE13buses\n'

    circuit_tail = 'Set Voltagebases=[115, 4.16, .48]\n'
    circuit_tail += 'calcv\n'
    circuit_tail += 'solve\n'
    circuit_tail += 'Show Voltages LN Nodes\n'
    circuit_tail += 'Show Currents Elem\n'
    circuit_tail += 'Show Powers kVA Elem\n'
    circuit_tail += 'Show Losses\n'
    circuit_tail += 'Show Taps\n'

    for conn in db.query(LineType):
        lcs.append(LineCode(conn))

    for bus_id, connections in buses.items():
        conns = connections[1:]
        conn = connections[0]
        asset = conn.asset(conn.element, conn.bus, conns, conn.wired)

        if conn.element.id == root:
            stations.append(asset)
        if conn.asset == Line:
            lines.append(asset)
        if conn.asset == Switch:
            lines.append(asset)
        if conn.asset == Meter:
            loads.append(asset)
        if conn.asset == Regulator:
            regulators.append(asset)
        if conn.asset == Capacitor:
            capacitors.append(asset)
        if conn.asset == Transformer:
            transformers.append(asset)
        if conn.asset == Generator:
            generators.append(asset)

    if len(stations) == 0:
        circuit.append(comment('WARNING: No voltage source provided'))

    circuit.append(circuit_head)
    for group in ELEMENTS:
        circuit.append(f'// ==== {group["title"]}\n')

        for asset in group['assets']:
            circuit.append(str(asset) + '\n')
    circuit.append(circuit_tail)

    return circuit


if __name__ == '__main__':
    opts, args = getopt(sys.argv[1:], '', ['vsource-id='])

    if len(opts) == 0 or opts[0][1].strip() == '':
        print('Provide a voltage source id')
        sys.exit(-1)

    vsource = opts[0][1]
    for line in generate_dss_script(db, root=vsource):
        print(line)