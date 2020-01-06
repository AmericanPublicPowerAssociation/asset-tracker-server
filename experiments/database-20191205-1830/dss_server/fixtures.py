substation = {
    'id': 1,
    'type': 's',
    'name': 'Substation A',
}

substation_1 = {
    'id': 2,
    'type': 't',
    'name': 'Substation Transformer 1',
    'attributes': {
        'phaseCount': 3,
        'windingCount': 2,
        'winding1Winding2PercentReactance': 8 / 1000,
        'vendor': 'Schneider Electric',
        'product': 'HVT36A',
        'version': '2.0.1',
    },
    'busByIndex': {
        '0': {
            'id': 'Ai',
            'attributes': {
                'connectionType': 'delta',
                'baseVoltage': 115,
                'baseVoltageUnit': 'kV',
                'power': 5000,
                'powerUnit': 'kVA',
                'powerPercentResistance': 0.5 / 1000,
            },
        },
        '1': {
            'id': 'Ao',
            'attributes': {
                'connectionType': 'wye',
                'baseVoltage': 4.16,
                'baseVoltageUnit': 'kV',
                'power': 5000,
                'powerUnit': 'kVA',
                'powerPercentResistance': 0.5 / 1000,
            },
        },
    },
}

meter_1 = {
    'id': 3,
    'type': 'm',
    'name': 'Industrial Meter 1',
    'vendor': 'Schneider Electric',
    'product': 'SCH-MV10',
    'version': '10.5.7',
    'attributes': {
        'phaseCount': 3,
        'loadModel': 1,
    },
    'busByIndex': {
        '0': {
            'id': 'L2o',
            'attributes': {
            },
        },
    },
}

meter_2 = {
    'id': 4,
    'type': 'm',
    'name': 'Industrial Meter 2',
    'vendor': 'Schneider Electric',
    'product': 'SCH-MV10',
    'version': '10.5.7',
    'attributes': {
        'phaseCount': 3,
        'loadModel': 5,
    },
    'busByIndex': {
        '0': {
            'id': 'L3o',
            'attributes': {
            },
        },
    },
}

line_1 = {
    'id': 5,
    'type': 'l',
    'name': 'Line 1',
    'attributes': {
        'phaseCount': 3,
        'lineType': 'mtx601',
        'lineLength': 2000,
        'lengthUnit': 'ft',
    },
    'busByIndex': {
        '0': {
            'id': 'Ao',
            'attributes': {
            },
        },
        '3': {
            'id': 'L1o',
            'attributes': {
            },
        },
    },
}

line_2 = {
    'id': 6,
    'type': 'l',
    'name': 'Line 2',
    'attributes': {
        'phaseCount': 3,
        'lineType': 'mtx602',
        'lineLength': 500,
        'lengthUnit': 'ft',
    },
    'busByIndex': {
        '0': {
            'id': 'L1o',
            'attributes': {
            },
        },
        '1': {
            'id': 'L2o',
            'attributes': {
            },
        },
    },
}

line_3 = {
    'id': 7,
    'type': 'l',
    'name': 'Line 3',
    'attributes': {
        'phaseCount': 3,
        'lineType': 'mtx602',
        'lineLength': 500,
        'lengthUnit': 'ft',
    },
    'busByIndex': {
        '0': {
            'id': 'L1o',
            'attributes': {
            },
        },
        '1': {
            'id': 'L3o',
            'attributes': {
            },
        },
    },
}