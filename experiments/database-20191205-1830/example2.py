from models import Asset, ElectricalConnection, LineType, db


generator = Asset(
    id='voltageSource',
    type_code='g',
    attributes={
        'baseFrequency': 60,
        'baseVoltage': 115,
        'baseVoltageUnit': 'kV',
        'perUnitVoltage': 1.0001,
        'phaseCount': 3,
        'phaseAngle': 30,
        'shortCircuit3PhasePower': 20000,
        'shortCircuit3PhasePowerUnit': 'MVA',
        'shortCircuit1PhasePower': 21000,
        'shortCircuit1PhasePowerUnit': 'MVA',
    })
db.add(generator)


substationTransformer = Asset(
    id='substationTransformer',
    type_code='t',
    attributes={
        'phaseCount': 3,
        'windingCount': 2,
        'winding1Winding2PercentReactance': 8 / 1000,
    })
db.add(substationTransformer)


regulator1 = Asset(
    id='voltageRegulator1',
    type_code='qr',
    attributes={
        'phaseCount': 1,
        'windingCount': 2,
        'winding1Winding2PercentReactance': 0.01,
        'percentLoadLoss': 0.01,
        'regulatedVoltage': 120,
        'regulatedVoltageUnit': 'V',
        'bandwidthVoltage': 2,
        'bandwidthVoltageUnit': 'V',
        'potentialTransformerRatio': 20,
        'currentTransformerRating': 700,
        'currentTransformerRatingUnit': 'A',
        'rSettingVoltage': 3,
        'rSettingVoltageUnit': 'V',
        'xSettingVoltage': 9,
        'xSettingVoltageUnit': 'V',
    })
db.add(regulator1)


regulator2 = Asset(
    id='voltageRegulator2',
    type_code='qr',
    attributes={
        'phaseCount': 1,
        'windingCount': 2,
        'winding1Winding2PercentReactance': 0.01,
        'percentLoadLoss': 0.01,
        'regulatedVoltage': 120,
        'regulatedVoltageUnit': 'V',
        'bandwidthVoltage': 2,
        'bandwidthVoltageUnit': 'V',
        'potentialTransformerRatio': 20,
        'currentTransformerRating': 700,
        'currentTransformerRatingUnit': 'A',
        'rSettingVoltage': 3,
        'rSettingVoltageUnit': 'V',
        'xSettingVoltage': 9,
        'xSettingVoltageUnit': 'V',
    })
db.add(regulator2)


regulator3 = Asset(
    id='voltageRegulator3',
    type_code='qr',
    attributes={
        'phaseCount': 1,
        'windingCount': 2,
        'winding1Winding2PercentReactance': 0.01,
        'percentLoadLoss': 0.01,
        'regulatedVoltage': 120,
        'regulatedVoltageUnit': 'V',
        'bandwidthVoltage': 2,
        'bandwidthVoltageUnit': 'V',
        'potentialTransformerRatio': 20,
        'currentTransformerRating': 700,
        'currentTransformerRatingUnit': 'A',
        'rSettingVoltage': 3,
        'rSettingVoltageUnit': 'V',
        'xSettingVoltage': 9,
        'xSettingVoltageUnit': 'V',
    })
db.add(regulator3)


poleTransformer = Asset(
    id='XFM1',
    type_code='t',
    attributes={
        'phaseCount': 3,
        'windingCount': 2,
        'winding1Winding2PercentReactance': 2,
    })
db.add(poleTransformer)


source_bus = Asset(
    id='sourceBus',
    type_code='b',
    attributes={})
db.add(source_bus)


ieee_650_bus = Asset(
    id='650',
    type_code='b',
    attributes={})
db.add(ieee_650_bus)


ieee_rg60_bus = Asset(
    id='RG60',
    type_code='b',
    attributes={})
db.add(ieee_rg60_bus)


ieee_633_bus = Asset(
    id='633',
    type_code='b',
    attributes={})
db.add(ieee_633_bus)


ieee_634_bus = Asset(
    id='634',
    type_code='b',
    attributes={})
db.add(ieee_634_bus)


ieee_671_bus = Asset(
    id='671',
    type_code='b',
    attributes={})
db.add(ieee_671_bus)


electrical_connection = ElectricalConnection(
    asset_id=generator.id,
    bus_id=source_bus.id,
    attributes={})
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=substationTransformer.id,
    bus_id=source_bus.id,
    attributes={
        'connectionType': 'delta',
        'baseVoltage': 115,
        'baseVoltageUnit': 'kV',
        'power': 5000,
        'powerUnit': 'kVA',
        'powerPercentResistance': 0.5 / 1000,
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=substationTransformer.id,
    bus_id=ieee_650_bus.id,
    attributes={
        'connectionType': 'wye',
        'baseVoltage': 4.16,
        'baseVoltageUnit': 'kV',
        'power': 5000,
        'powerUnit': 'kVA',
        'powerPercentResistance': 0.5 / 1000,
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=regulator1.id,
    bus_id=ieee_650_bus.id,
    attributes={
        'busNodes': [1],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'power': 1666,
        'powerUnit': 'kVA',
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=regulator2.id,
    bus_id=ieee_rg60_bus.id,
    attributes={
        'busNodes': [2],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'power': 1666,
        'powerUnit': 'kVA',
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=regulator3.id,
    bus_id=ieee_rg60_bus.id,
    attributes={
        'busNodes': [3],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'power': 1666,
        'powerUnit': 'kVA',
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=poleTransformer.id,
    bus_id=ieee_633_bus,
    attributes={
        'connectionType': 'wye',
        'baseVoltage': 4.16,
        'baseVoltageUnit': 'kV',
        'power': 500,
        'powerUnit': 'kVA',
        'powerPercentResistance': 0.55,
        'winding1Winding3PercentReactance': 1,
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=poleTransformer.id,
    bus_id=ieee_634_bus,
    attributes={
        'connectionType': 'wye',
        'baseVoltage': 0.48,
        'baseVoltageUnit': 'kV',
        'power': 500,
        'powerUnit': 'kVA',
        'powerPercentResistance': 0.55,
        'winding1Winding3PercentReactance': 1,
    })
db.add(electrical_connection)


line_type_mtx601 = LineType(
    id='mtx601',
    attributes={
        'baseFrequency': 60,
        'phaseCount': 3,
        'resistanceMatrix': [
            [0.3465, 0, 0],
            [0.1560, 0.3375, 0],
            [0.1580, 0.1535, 0.3414],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [1.0179, 0, 0],
            [0.5017, 1.0478, 0],
            [0.4236, 0.3849, 1.0348],
        ],
        'reactanceMatrixUnit': 'ohms/mi',
    })
db.add(line_type_mtx601)


line_type_mtx602 = LineType(
    id='mtx602',
    attributes={
        'baseFrequency': 60,
        'phaseCount': 3,
        'resistanceMatrix': [
            [0.7526, 0, 0],
            [0.1580, 0.7475, 0],
            [0.1560, 0.1535, 0.7436],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [1.1814, 0, 0],
            [0.4236, 1.1983, 0],
            [0.5017, 0.3849, 1.2112],
        ],
        'reactanceMatrixUnit': 'ohms/mi',
    })
db.add(line_type_mtx602)


line_type_mtx603 = LineType(
    id='mtx603',
    attributes={
        'baseFrequency': 60,
        'phaseCount': 2,
        'resistanceMatrix': [
            [1.3238, 0],
            [0.2066, 1.3294],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [1.3569, 0],
            [0.4591, 1.3471],
        ],
        'reactanceMatrixUnit': 'ohms/mi',
    })
db.add(line_type_mtx603)


line_type_mtx604 = LineType(
    id='mtx604',
    attributes={
        'baseFrequency': 60,
        'phaseCount': 2,
        'resistanceMatrix': [
            [1.3238, 0],
            [0.2066, 1.3294],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [1.3569, 0],
            [0.4591, 1.3471],
        ],
        'reactanceMatrixUnit': 'ohms/mi',
    })
db.add(line_type_mtx604)


line_type_mtx605 = LineType(
    id='mtx605',
    attributes={
        'baseFrequency': 60,
        'phaseCount': 1,
        'resistanceMatrix': [
            [1.3292],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [1.3475],
        ],
        'reactanceMatrixUnit': 'ohms/mi',
    })
db.add(line_type_mtx605)


line_type_mtx606 = LineType(
    id='mtx606',
    attributes={
        'baseFrequency': 60,
        'phaseCount': 3,
        'resistanceMatrix': [
            [0.791721, 0, 0],
            [0.318476, 0.781649, 0],
            [0.28345, 0.318476, 0.791721],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [0.438352, 0, 0],
            [0.0276838, 0.396697, 0],
            [-0.0184204, 0.0276838, 0.4383],
        ],
        'reactanceMatrixUnit': 'ohms/mi',
        'capacitanceMatrix': [
            [383.948, 0, 0],
            [0, 383.948, 0],
            [0, 0, 383.948],
        ],
        'capacitanceMatrixUnit': 'nF/mi',
    })
db.add(line_type_mtx606)


line_type_mtx607 = LineType(
    id='mtx607',
    attributes={
        'baseFrequency': 60,
        'phaseCount': 1,
        'resistanceMatrix': [
            [1.3425],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [0.5124],
        ],
        'reactanceMatrixUnit': 'ohms/mi',
        'capacitanceMatrix': [
            [236],
        ],
        'capacitanceMatrixUnit': 'nF/mi',
    })
db.add(line_type_mtx607)


load_671 = Asset(
    id='671',
    type_code='m',
    attributes={
        'phaseCount': 3,
        'loadModel': 1,
    })
db.add(load_671)


electrical_connection = ElectricalConnection(
    asset_id=load_671.id,
    bus_id=ieee_671_bus.id,
    attributes={
        'connectionType': 'delta',
        'busNodes': [1, 2, 3],
        'baseVoltage': 4.16,
        'baseVoltageUnit': 'kV',
        'activePower': 115,
        'activePowerUnit': 'kW',
        'reactivePower': 660,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


capacitor1 = Asset(
    id='cap1',
    type_code='qc',
    attributes={
        'phaseCount': 3,
    })
db.add(capacitor1)


electrical_connection = ElectricalConnection(
    asset_id=capacitor1.id,
    bus_id=ieee_675_bus.id,
    attributes={
        'baseVoltage': 4.16,
        'baseVoltageUnit': 'kV',
        'reactivePower': 600,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


capacitor2 = Asset(
    id='cap2',
    type_code='qc',
    attributes={
        'phaseCount': 1,
    })
db.add(capacitor2)


electrical_connection = ElectricalConnection(
    asset_id=capacitor2.id,
    bus_id=ieee_611_bus.id,
    attributes={
        'busNodes': [3],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'reactivePower': 100,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


line_650_632 = Asset(
    id='650-632',
    type_code='l',
    attributes={
        'phaseCount': 3,
        'lineType': 'mtx601',
        'lineLength': 2000,
        'lengthUnit': 'ft',
    })
db.add(line_650_632)


electrical_connection = ElectricalConnection(
    asset_id=line_650_632.id,
    bus_id=ieee_rg60_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_650_632.id,
    bus_id=ieee_632_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)


switch = Asset(
    id='671-692',
    type_code='x',
    attributes={
        'phaseCount': 3,
        'positiveSequenceResistance': 1e-4,
        'positiveSequenceResistanceUnit': 'ohms/mi',
        'zeroSequenceResistance': 1e-4,
        'zeroSequenceResistanceUnit': 'ohms/mi',
        'positiveSequenceReactance': 0,
        'positiveSequenceReactanceUnit': 'ohms/mi',
        'zeroSequenceReactance': 0,
        'zeroSequenceReactanceUnit': 'ohms/mi',
        'positiveSequenceCapacitance': 0,
        'positiveSequenceCapacitanceUnit': 'nF/mi',
        'zeroSequenceCapacitance': 0,
        'zeroSequenceCapacitanceUnit': 'nF/mi',
    })
db.add(switch)


electrical_connection = ElectricalConnection(
    asset_id=switch.id,
    bus_id=ieee_671_bus.id,
    attributes={
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=switch.id,
    bus_id=ieee_692_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)
