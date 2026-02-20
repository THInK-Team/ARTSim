# Author: Adam Corbier (@Ad2Am2)

"""UNITS:
VHC in J⋅K−1⋅m−3
Conductivity in W/mK
"""

materials = {
    "Si": {
        "volumetricHeatCapacity": 703*2330,
        "conductivity": 125.52
    },
    "Cu": {
        "volumetricHeatCapacity": 385*8940,
        "conductivity": 397.48
    },
    "Resin epoxy": {
        "volumetricHeatCapacity": 900*1500,
        "conductivity": 1
    },
    "Solder": {
        "volumetricHeatCapacity": 197*8500,
        "conductivity": 50.208
    },
    "Aluminium": {
        "volumetricHeatCapacity": 921*2698,
        "conductivity": 225.94
    },
    "Aluminium Silicate": {
        "volumetricHeatCapacity": 766*3200,
        "conductivity": 6.276
    },
    "FR-4 epoxy": {
        "volumetricHeatCapacity": 1100*1900,
        "conductivity": 0.3
    },
    "SiO2": {
        "volumetricHeatCapacity": 680*2270,
        "conductivity": 1.3
    }
}