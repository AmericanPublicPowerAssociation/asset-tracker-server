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
POWERQUALITY_CAPACITOR = f'{POWERQUALITY}c'
POWERQUALITY_REGULATOR = f'{POWERQUALITY}r'

to_dss_array = lambda l:  f'[ {" ".join(l)} ]'

build_bus = lambda bus, nodes:  f'{bus}.{".".join(nodes)}'
to_str = lambda l: [str(e) for e in l]
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

    def attributes(self):
        return self.asset.name


class LineCode(AssetMixin):
    type = LINECODE

    def __init__(self, asset):
        self.asset = asset

    def __str__(self):
        return ('New Linecode.{title} nphases={phases} basefreq={frequency} normamps=419.0 ' 
                'rmatrix=({rmatrix}) xmatrix=({xmatrix})')


class Line(AssetMixin):
    type = LINE

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        phases = self.asset.attributes.get('phaseCount')
        lc = self.asset.attributes.get('lineType')
        length = self.asset.attributes.get('lineLength')
        unit = self.asset.attributes.get('lengthUnit')

        line = f'New Line.{self.asset.id} phases={phases} linecode={lc} length={length} units={unit}'
        attr = self.wired.attributes
        bus1 = build_bus(self.bus.id, to_str(attr.get('busNodes')))
        bus2 = None
        if len(self.conn) > 0:
            for conn in self.conn:
                attr = conn.wired.attributes
                bus2 = build_bus(conn.bus.id, to_str(attr.get('busNodes')))

        if bus1:
            line += f' Bus1={bus1} '

        if bus2:
            line += f' Bus2={bus2}'

        return line


class Switch(AssetMixin):
    type = SWITCH

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        phases = self.asset.attributes.get('phaseCount')
        r1 = self.asset.attributes.get('positiveSequenceResistance')
        r0 = self.asset.attributes.get('zeroSequenceResistance')
        x1 = self.asset.attributes.get('positiveSequenceReactance')
        x0 = self.asset.attributes.get('zeroSequenceReactance')
        c1 = self.asset.attributes.get('positiveSequenceCapacitance')
        c0 = self.asset.attributes.get('zeroSequenceCapacitance')

        line = f'New Line.{self.asset.id} Switch=y phases={phases}'
        line += f' r1={r1} r0={r0} x1={x1} x0={x0} c1={c1} c0={c0}'

        attr = self.wired.attributes
        bus1 = build_bus(self.bus.id, to_str(attr.get('busNodes')))
        bus2 = None
        if len(self.conn) > 0:
            for conn in self.conn:
                attr = conn.wired.attributes
                bus2 = build_bus(conn.bus.id, to_str(attr.get('busNodes')))

        if bus1:
            line += f' Bus1={bus1} '

        if bus2:
            line += f' Bus2={bus2}'

        return line


class Meter(AssetMixin):
    type = METER

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        phases = self.asset.attributes.get('phaseCount')
        model = self.asset.attributes.get('loadModel')

        attr = self.wired.attributes
        bus1 = build_bus(self.bus.id, to_str(attr.get('busNodes')))

        kV = attr.get('baseVoltage')
        conn = attr.get('connectionType')
        kW = attr.get('activePower')
        kvar = attr.get('reactivePower')

        command = f'New Load.Load_{self.asset.id} phases={phases} conn={conn} model={model} '
        command += f' Bus1={bus1} kV={kV} kW={kW} kvar={kvar}'

        return command


class Regulator(AssetMixin):
    type = POWERQUALITY_REGULATOR

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        xhl = self.asset.attributes.get('percentLoadLoss')
        vreg = self.asset.attributes.get('regulatedVoltage')
        band = self.asset.attributes.get('bandwidthVoltage')
        ptratio = self.asset.attributes.get('potentialTransformerRatio')
        ctprim = self.asset.attributes.get('currentTransformerRating')
        R = self.asset.attributes.get('rSettingVoltage')
        X = self.asset.attributes.get('xSettingVoltage')
        phases = self.asset.attributes.get('phaseCount')
        winding = self.asset.attributes.get('windingCount')

        attr = self.wired.attributes
        kVs = [attr.get('baseVoltage')]
        kVAs = [attr.get('power')]
        buses = [build_bus(self.bus.id, to_str(attr.get('busNodes')))]

        for conn in self.conn:
            attr = conn.wired.attributes
            kVs.append(attr.get('baseVoltage'))
            kVAs.append(attr.get('power'))
            buses.append(build_bus(conn.bus.id, to_str(attr.get('busNodes'))))

        command = f'New Transformer.{self.asset.id} phases={phases} bank={self.asset.id}'
        command += f' buses={to_dss_array(to_str(buses))} kVs={to_dss_array(to_str(kVs))}'
        command += f' kVAs={to_dss_array(to_str(kVAs))} xhl={xhl} %LoadLoss={xhl}\n'

        command +=  f'New regcontrol.{self.asset.id} transformer={self.asset.id} '
        command += f' winding={winding} vreg={vreg} band={band} ptratio={ptratio} ctprim={ctprim}'
        command += f' R={R} X={X}'

        return command


class Capacitor(AssetMixin):
    type = POWERQUALITY_CAPACITOR

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        phases = self.asset.attributes.get('phaseCount')

        attr = self.wired.attributes
        bus1 = build_bus(self.bus.id, to_str(attr.get('busNodes')))
        kV = attr.get('baseVoltage')
        conn = attr.get('connectionType', None)
        kvar = attr.get('reactivePower')

        command = f'new capacitor.{self.asset.id} phases={phases} bus1={bus1} kVAr={kvar} kV={kV} '

        if conn:
            command += f' conn={conn}'

        return command


class Transformer(AssetMixin):
    type = TRANSFORMER

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        phases = self.asset.attributes.get('phaseCount')
        winding = self.asset.attributes.get('windingCount')
        xhl = self.asset.attributes.get('winding1Winding2PercentReactance', None)
        xht = self.asset.attributes.get('winding1Winding3PercentReactance', None)
        xlt = self.asset.attributes.get('winding2Winding3PercentReactance', None)
        command = f'New Transformer.{self.asset.id} Phases={phases} Windings={winding}'

        if xhl:
            command += f' xhl={xhl}'
        if xht:
            command += f' xht={xht}'
        if xlt:
            command += f' xlt={xlt}'

        attr = self.wired.attributes
        conns = [attr.get('connectionType')]
        kVs = [attr.get('baseVoltage')]
        kVAs = [attr.get('power')]
        Rs = [attr.get('powerPercentResistance')]
        buses = [self.bus.id]
        for conn in self.conn:
            attr = conn.wired.attributes
            conns.append(attr.get('connectionType'))
            kVs.append(attr.get('baseVoltage'))
            kVAs.append(attr.get('power'))
            Rs.append(attr.get('powerPercentResistance'))
            buses.append(conn.bus.id)

        command += f' buses={to_dss_array(to_str(buses))} conns={to_dss_array(to_str(conns))}'
        command += f' kVs={to_dss_array(to_str(kVs))} kvas={to_dss_array(to_str(kVAs))}'
        command += f' %Rs={to_dss_array(to_str(Rs))}'

        return command


class Generator(AssetMixin):
    type = GENERATOR

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        command = f'New Generator.{self.asset,id}'
        return command


class Circuit(AssetMixin):
    type = ''

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        frequency = self.asset.attributes.get('baseFrequency')
        kV = self.asset.attributes.get('baseVoltage')
        pu = self.asset.attributes.get('perUnitVoltage')
        phases = self.asset.attributes.get('phaseCount')
        angle = self.asset.attributes.get('phaseAngle')
        Isc3 = self.asset.attributes.get('shortCircuit3PhasePower')
        Isc1 = self.asset.attributes.get('shortCircuit1PhasePower')

        command = f'set defaultbasefrequency={frequency}\n'
        command += f'Edit Vsource.Source bus1={self.bus.id} BasekV={kV} pu={pu} angle={angle}'
        command += f' frequency={frequency} phases={phases} Isc3={Isc3} Isc1={Isc1}'

        return command


class LineCode(AssetMixin):
    type = LINECODE

    def __init__(self, linetype):
        self.linetype = linetype

    def __str__(self):
        rmatrix = to_matrix(self.linetype.attributes.get('resistanceMatrix'))
        xmatrix = to_matrix(self.linetype.attributes.get('reactanceMatrix'))
        frequency = self.linetype.attributes.get('baseFrequency')
        phases = self.linetype.attributes.get('phaseCount')
        unit = self.linetype.attributes.get('resistanceMatrixUnit').split('/')[1]
        return (f'New Linecode.{self.linetype.id} nphases={phases} BaseFreq={frequency} units={unit}\n' 
                f'~ rmatrix={rmatrix} \n'
                f'~ xmatrix={xmatrix}')

