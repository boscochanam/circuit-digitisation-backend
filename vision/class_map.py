# older model
# class_map = {
#         0: 'text',
#         1: 'socket',
#         2: 'resistor',
#         3: 'transistorfet',
#         4: 'integrated_circuitne555',
#         5: 'resistorphoto',
#         6: 'not',
#         7: 'unknown',
#         8: 'fuse',
#         9: 'nand',
#         10: 'varistor',
#         11: 'or',
#         12: 'optocoupler',
#         13: 'diodethyrector',
#         14: 'crystal',
#         15: 'microphone',
#         16: 'diode',
#         17: 'diodezener',
#         18: 'capacitor', # capacitor unpolarized
#         19: 'transistorphoto',
#         20: 'nor',
#         21: 'diac',
#         22: 'lamp',
#         23: 'powersource',
#         24: 'crossover',
#         25: 'probevoltage',
#         26: 'powersource',
#         27: 'probecurrent',
#         28: 'triac',
#         29: 'gnd',
#         30: 'vss',
#         31: 'voltagebattery',
#         32: 'junction',
#         33: 'switch',
#         34: 'and',
#         35: 'probe',
#         36: 'diodelight_emitting',
#         37: 'integrated_circuit',
#         38: 'mechanical',
#         39: 'motor',
#         40: 'magnetic',
#         41: 'capacitor', # capacitor polarized
#         42: 'integrated_circuitvoltage_regulator',
#         43: 'operational_amplifier',
#         44: 'relay',
#         45: 'operational_amplifierschmitt_trigger',
#         46: 'optical',
#         47: 'inductor', # inductor ferrite
#         48: 'terminal',
#         49: 'speaker',
#         50: 'transformer',
#         51: 'thyristor',
#         52: 'inductor',
#         53: 'xor',
#         54: 'antenna',
#         55: 'transistorbjt',
#         56: 'capacitor', # capacitor variable
#         57: 'resistoradjustable'
#     }

# new mapping for new model
class_map = {
    0: "text",
    1: "diodelight_emitting",
    2: "lamp",
    3: "transformer",
    4: "capacitor", # capacitor unpolarized
    5: "resistor",
    6: "inductor",
    7: "diode",
    8: "switch",
    9: "powersource",
    10: "junction"
}


def get_class_mapping(key):
    return class_map[key]