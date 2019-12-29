from models import Asset, ElectricalConnection, LineType, db

# Root Source
generator = Asset(
    id='voltageSource',
    type_code='g',
    attributes={
        'baseFrequency': 60,
        'baseVoltage': 115,
        'baseVoltageUnit': 'kV',
        'perUnitVoltage': 1.00,
        'phaseCount': 3,
        'phaseAngle': 30,
        'shortCircuit3PhasePower': 10000.0,
        'shortCircuit3PhasePowerUnit': 'MVA',
        'shortCircuit1PhasePower': 10500.0,
        'shortCircuit1PhasePowerUnit': 'MVA',
    })
db.add(generator)

# Substations
substationTransformer = Asset(
    id='substationTransformer',
    type_code='t',
    attributes={
        'phaseCount': 3,
        'windingCount': 2,
        'winding1Winding2PercentReactance': 8 / 1000,
    })
db.add(substationTransformer)

# Regulators
regulator1 = Asset(
    id='voltageRegulator1',
    type_code='qr',
    attributes={
        'phaseCount': 1,
        'windingCount': 2,
        'percentLoadLoss': 0.01,
        'regulatedVoltage': 122,
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
        'regulatedVoltage': 122,
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
        'regulatedVoltage': 122,
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

# Transformer
poleTransformer = Asset(
    id='XFM1',
    type_code='t',
    attributes={
        'phaseCount': 3,
        'windingCount': 2,
        'winding1Winding3PercentReactance': 1.0,
        'winding2Winding3PercentReactance': 1.0
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

ieee_645_bus = Asset(
    id='645',
    type_code='b',
    attributes={})
db.add(ieee_645_bus)

ieee_646_bus = Asset(
    id='646',
    type_code='b',
    attributes={})
db.add(ieee_646_bus)

ieee_652_bus = Asset(
    id='652',
    type_code='b',
    attributes={})
db.add(ieee_652_bus)

ieee_670_bus = Asset(
    id='670',
    type_code='b',
    attributes={})
db.add(ieee_670_bus)

ieee_671_bus = Asset(
    id='671',
    type_code='b',
    attributes={})
db.add(ieee_671_bus)

ieee_675_bus = Asset(
    id='675',
    type_code='b',
    attributes={})
db.add(ieee_675_bus)

ieee_611_bus = Asset(
    id='611',
    type_code='b',
    attributes={})
db.add(ieee_611_bus)

ieee_680_bus = Asset(
    id='680',
    type_code='b',
    attributes={})
db.add(ieee_680_bus)

ieee_684_bus = Asset(
    id='684',
    type_code='b',
    attributes={})
db.add(ieee_684_bus)

ieee_692_bus = Asset(
    id='692',
    type_code='b',
    attributes={})
db.add(ieee_692_bus)

ieee_632_bus = Asset(
    id='632',
    type_code='b',
    attributes={})
db.add(ieee_632_bus)

# Connections
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
    asset_id=regulator1.id,
    bus_id=ieee_rg60_bus.id,
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
    bus_id=ieee_650_bus.id,
    attributes={
        'busNodes': [2],
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
    bus_id=ieee_650_bus.id,
    attributes={
        'busNodes': [3],
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
    bus_id=ieee_633_bus.id,
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
    bus_id=ieee_634_bus.id,
    attributes={
        'connectionType': 'wye',
        'baseVoltage': 0.48,
        'baseVoltageUnit': 'kV',
        'power': 500,
        'powerUnit': 'kVA',
        'powerPercentResistance': 0.55,
        'winding2Winding3PercentReactance': 1,
    })
db.add(electrical_connection)

# Line codes
line_type_mtx601 = LineType(
    id='mtx601',
    attributes={
        'baseFrequency': 60,
        'phaseCount': 3,
        'resistanceMatrix': [
            [0.3465],
            [0.1560, 0.3375],
            [0.1580, 0.1535, 0.3414],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [1.0179],
            [0.5017, 1.04],
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
            [0.7526],
            [0.1580, 0.7475],
            [0.1560, 0.1535, 0.7436],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [1.1814],
            [0.4236, 1.1983],
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
            [1.3294],
            [0.2066, 1.3238],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [1.3471],
            [0.4591, 1.3569],
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
            [1.3238],
            [0.2066, 1.3294],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [1.3569],
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
            [0.7982],
            [0.3192, 0.7891],
            [0.2849, 0.3192, 0.7982],
        ],
        'resistanceMatrixUnit': 'ohms/mi',
        'reactanceMatrix': [
            [0.4463],
            [0.0328, 0.4041],
            [-0.0143, 0.0328, 0.4463],
        ],
        'reactanceMatrixUnit': 'ohms/mi',
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
    })
db.add(line_type_mtx607)

# Loads
load_671 = Asset(
    id='load_671',
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
        'activePower': 1155,
        'activePowerUnit': 'kW',
        'reactivePower': 660,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)

load_634_1 = Asset(
    id='634_1',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_634_1)

electrical_connection = ElectricalConnection(
    asset_id=load_634_1.id,
    bus_id=ieee_634_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [1],
        'baseVoltage': 0.277,
        'baseVoltageUnit': 'kV',
        'activePower': 160,
        'activePowerUnit': 'kW',
        'reactivePower': 110,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)

load_634_2 = Asset(
    id='634_2',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_634_2)

electrical_connection = ElectricalConnection(
    asset_id=load_634_2.id,
    bus_id=ieee_634_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [2],
        'baseVoltage': 0.277,
        'baseVoltageUnit': 'kV',
        'activePower': 120,
        'activePowerUnit': 'kW',
        'reactivePower': 90,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)

load_634_3 = Asset(
    id='634_3',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_634_3)

electrical_connection = ElectricalConnection(
    asset_id=load_634_3.id,
    bus_id=ieee_634_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [3],
        'baseVoltage': 0.277,
        'baseVoltageUnit': 'kV',
        'activePower': 120,
        'activePowerUnit': 'kW',
        'reactivePower': 90,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_645_2 = Asset(
    id='645_2',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_645_2)

electrical_connection = ElectricalConnection(
    asset_id=load_645_2.id,
    bus_id=ieee_645_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [2],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'activePower': 170,
        'activePowerUnit': 'kW',
        'reactivePower': 125,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_646_2 = Asset(
    id='646_2',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_646_2)

electrical_connection = ElectricalConnection(
    asset_id=load_646_2.id,
    bus_id=ieee_646_bus.id,
    attributes={
        'connectionType': 'delta',
        'busNodes': [2, 3],
        'baseVoltage': 4.16,
        'baseVoltageUnit': 'kV',
        'activePower': 230,
        'activePowerUnit': 'kW',
        'reactivePower': 132,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_652_1 = Asset(
    id='652_1',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 2,
    })
db.add(load_652_1)

electrical_connection = ElectricalConnection(
    asset_id=load_652_1.id,
    bus_id=ieee_652_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [1],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'activePower': 128,
        'activePowerUnit': 'kW',
        'reactivePower': 86,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_675_1 = Asset(
    id='675_1',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_675_1)

electrical_connection = ElectricalConnection(
    asset_id=load_675_1.id,
    bus_id=ieee_675_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [1],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'activePower': 485,
        'activePowerUnit': 'kW',
        'reactivePower': 190,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_675_2 = Asset(
    id='675_2',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_675_2)

electrical_connection = ElectricalConnection(
    asset_id=load_675_2.id,
    bus_id=ieee_675_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [2],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'activePower': 68,
        'activePowerUnit': 'kW',
        'reactivePower': 60,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_675_3 = Asset(
    id='675_3',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_675_3)

electrical_connection = ElectricalConnection(
    asset_id=load_675_3.id,
    bus_id=ieee_675_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [3],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'activePower': 290,
        'activePowerUnit': 'kW',
        'reactivePower': 212,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_692_3 = Asset(
    id='692_3',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 5,
    })
db.add(load_692_3)

electrical_connection = ElectricalConnection(
    asset_id=load_692_3.id,
    bus_id=ieee_692_bus.id,
    attributes={
        'connectionType': 'delta',
        'busNodes': [3, 1],
        'baseVoltage': 4.16,
        'baseVoltageUnit': 'kV',
        'activePower': 170,
        'activePowerUnit': 'kW',
        'reactivePower': 151,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_611_3 = Asset(
    id='611_3',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 5,
    })
db.add(load_611_3)

electrical_connection = ElectricalConnection(
    asset_id=load_611_3.id,
    bus_id=ieee_611_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [3],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'activePower': 170,
        'activePowerUnit': 'kW',
        'reactivePower': 80,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_670_1 = Asset(
    id='670_1',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_670_1)

electrical_connection = ElectricalConnection(
    asset_id=load_670_1.id,
    bus_id=ieee_670_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [1],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'activePower': 17,
        'activePowerUnit': 'kW',
        'reactivePower': 10,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_670_2 = Asset(
    id='670_2',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_670_2)

electrical_connection = ElectricalConnection(
    asset_id=load_670_2.id,
    bus_id=ieee_670_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [2],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'activePower': 66,
        'activePowerUnit': 'kW',
        'reactivePower': 38,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


load_670_3 = Asset(
    id='670_3',
    type_code='m',
    attributes={
        'phaseCount': 1,
        'loadModel': 1,
    })
db.add(load_670_3)
electrical_connection = ElectricalConnection(
    asset_id=load_670_3.id,
    bus_id=ieee_670_bus.id,
    attributes={
        'connectionType': 'wye',
        'busNodes': [3],
        'baseVoltage': 2.4,
        'baseVoltageUnit': 'kV',
        'activePower': 117,
        'activePowerUnit': 'kW',
        'reactivePower': 68,
        'reactivePowerUnit': 'kVAR',
    })
db.add(electrical_connection)


# Capacitors
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
        'busNodes': [1, 2, 3],
        'baseVoltage': 4.16,
        'baseVoltageUnit': 'kV',
        'reactivePower': 600,
        'reactivePowerUnit': 'kVAr',
        'connectionType': 'wye',
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
        'reactivePowerUnit': 'kVAr',
    })
db.add(electrical_connection)

# lines
line_632_645 = Asset(
    id='632-645',
    type_code='l',
    attributes={
        'phaseCount': 2,
        'lineType': 'mtx603',
        'lineLength': 0.09,
        'lengthUnit': 'mi',
    })
db.add(line_632_645)


electrical_connection = ElectricalConnection(
    asset_id=line_632_645.id,
    bus_id=ieee_632_bus.id,
    attributes={
        'busNodes': [2, 3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_632_645.id,
    bus_id=ieee_645_bus.id,
    attributes={
        'busNodes': [2, 3],
    })
db.add(electrical_connection)

line_632_633 = Asset(
    id='632-633',
    type_code='l',
    attributes={
        'phaseCount': 3,
        'lineType': 'mtx602',
        'lineLength': 0.09,
        'lengthUnit': 'mi',
    })
db.add(line_632_633)


electrical_connection = ElectricalConnection(
    asset_id=line_632_633.id,
    bus_id=ieee_632_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_632_633.id,
    bus_id=ieee_633_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)

line_645_646 = Asset(
    id='645-646',
    type_code='l',
    attributes={
        'phaseCount': 2,
        'lineType': 'mtx603',
        'lineLength': 0.06,
        'lengthUnit': 'mi',
    })
db.add(line_645_646)


electrical_connection = ElectricalConnection(
    asset_id=line_645_646.id,
    bus_id=ieee_645_bus.id,
    attributes={
        'busNodes': [2, 3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_645_646.id,
    bus_id=ieee_646_bus.id,
    attributes={
        'busNodes': [2, 3],
    })
db.add(electrical_connection)

line_rg60_632 = Asset(
    id='rg60-632',
    type_code='l',
    attributes={
        'phaseCount': 3,
        'lineType': 'mtx601',
        'lineLength': 0.38,
        'lengthUnit': 'mi',
    })
db.add(line_rg60_632)


electrical_connection = ElectricalConnection(
    asset_id=line_rg60_632.id,
    bus_id=ieee_rg60_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_rg60_632.id,
    bus_id=ieee_632_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)

line_684_652 = Asset(
    id='684-652',
    type_code='l',
    attributes={
        'phaseCount': 1,
        'lineType': 'mtx607',
        'lineLength': 0.15,
        'lengthUnit': 'mi',
    })
db.add(line_684_652)


electrical_connection = ElectricalConnection(
    asset_id=line_684_652.id,
    bus_id=ieee_684_bus.id,
    attributes={
        'busNodes': [1],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_684_652.id,
    bus_id=ieee_652_bus.id,
    attributes={
        'busNodes': [1],
    })
db.add(electrical_connection)

line_632_671 = Asset(
    id='632-671',
    type_code='l',
    attributes={
        'phaseCount': 3,
        'lineType': 'mtx601',
        'lineLength': 0.38,
        'lengthUnit': 'mi',
    })
db.add(line_632_671)


electrical_connection = ElectricalConnection(
    asset_id=line_632_671.id,
    bus_id=ieee_632_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_632_671.id,
    bus_id=ieee_671_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)

line_671_684 = Asset(
    id='671-684',
    type_code='l',
    attributes={
        'phaseCount': 2,
        'lineType': 'mtx604',
        'lineLength': 0.06,
        'lengthUnit': 'mi',
    })
db.add(line_671_684)


electrical_connection = ElectricalConnection(
    asset_id=line_671_684.id,
    bus_id=ieee_671_bus.id,
    attributes={
        'busNodes': [1, 3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_671_684.id,
    bus_id=ieee_684_bus.id,
    attributes={
        'busNodes': [1, 3],
    })
db.add(electrical_connection)

line_671_680 = Asset(
    id='671-680',
    type_code='l',
    attributes={
        'phaseCount': 3,
        'lineType': 'mtx601',
        'lineLength': 0.19,
        'lengthUnit': 'mi',
    })
db.add(line_671_680)


electrical_connection = ElectricalConnection(
    asset_id=line_671_680.id,
    bus_id=ieee_671_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_671_680.id,
    bus_id=ieee_680_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)

line_684_611 = Asset(
    id='684-611',
    type_code='l',
    attributes={
        'phaseCount': 1,
        'lineType': 'mtx605',
        'lineLength': 0.06,
        'lengthUnit': 'mi',
    })
db.add(line_684_611)


electrical_connection = ElectricalConnection(
    asset_id=line_684_611.id,
    bus_id=ieee_684_bus.id,
    attributes={
        'busNodes': [3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_684_611.id,
    bus_id=ieee_611_bus.id,
    attributes={
        'busNodes': [3],
    })
db.add(electrical_connection)

line_692_675 = Asset(
    id='692-675',
    type_code='l',
    attributes={
        'phaseCount': 3,
        'lineType': 'mtx606',
        'lineLength': 0.09,
        'lengthUnit': 'mi',
    })
db.add(line_692_675)


electrical_connection = ElectricalConnection(
    asset_id=line_692_675.id,
    bus_id=ieee_692_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=line_692_675.id,
    bus_id=ieee_675_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)

# Switches
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
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)


electrical_connection = ElectricalConnection(
    asset_id=switch.id,
    bus_id=ieee_692_bus.id,
    attributes={
        'busNodes': [1, 2, 3],
    })
db.add(electrical_connection)


db.commit()
