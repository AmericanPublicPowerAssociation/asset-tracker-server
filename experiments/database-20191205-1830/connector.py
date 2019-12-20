from collections import namedtuple

try:
    from .models import Asset, ElectricalConnection, db, LineType
    from .opendss import Line, Switch, Meter, Regulator, Capacitor, Transformer, Generator, Circuit, LineCode
except ModuleNotFoundError:
    from models import Asset, ElectricalConnection, db, LineType
    from opendss import Line, Switch, Meter, Regulator, Capacitor, Transformer, Generator, Circuit, LineCode



ASSET = [Line, Switch, Meter, Regulator, Capacitor, Transformer, Generator]
Conn = namedtuple("Conn", ["bus", "element", 'asset', 'wired'])

buses = {}
for conn in db.query(ElectricalConnection):
    asset = None
    # print(conn.bus_id)
    if conn.asset_id not in buses.keys():
        current = []
    else:
        current = buses[conn.asset_id]
    # print(current)
    element = db.query(Asset).filter(Asset.id==conn.asset_id).one()
    bus = db.query(Asset).filter(Asset.id == conn.bus_id).one()

    if element.id == 'voltageSource':
        asset = Circuit
    else:
        for AssetClass in ASSET:
            # print(element.type_code == AssetClass.type)
            if element.type_code == AssetClass.type:
                asset = AssetClass
                # print(AssetClass.type)

    # print(f'Bus {asset.type}')

    current.append(Conn(bus, element, asset, conn))
    buses[conn.asset_id] = current

print('// == Wiring assets')

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
    # print(f'{bus_id}: {connections}')
    conns = connections[1:]
    conn = connections[0]
    # print(f'Wire: {conn.asset.type} {conn.element} {conn.bus} {conns}')
    asset = conn.asset(conn.element, conn.bus, conns, conn.wired)

    ASSET = [Line, Switch, Meter, Regulator, Capacitor, Transformer, Generator]
    if conn.element.id == 'voltageSource':
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


print(circuit_head)
for group in ELEMENTS:
    print(f'// ==== {group["title"]}')

    for asset in group['assets']:
        print(asset)
print(circuit_tail)