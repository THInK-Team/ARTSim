# Author: Adam Corbier (@Ad2Am2)

# Imports
from src import materials    # Allows for use of default values for given materials
from src.nub_ctm import make_unit_dict  # Prepackaged function to create functional blocks in the system


##### FIRST LAYER #####

# Definition of functional blocks' coordinates

bk1_leftX = 0   # coordinate system uses (0,0) as the bottom left corner. All values in meters.
bk1_bottomY = 0
bk1_width = 0.000288617 # X-axis
bk1_height = 7.21543e-05    # Y-axis

bk2_leftX = 0
bk2_bottomY = 7.21543e-05
bk2_width = 1.194520000E-04
bk2_height = 0.000149315

bk3_leftX = 0.000288617
bk3_bottomY = 0
bk3_width = 2.575840000E-04
bk3_height = 1.830740000E-04

bk4_leftX = 0
bk4_bottomY = 2.214693000E-04
bk4_width = 1.194520000E-04
bk4_height = 1.335257000E-04

bk5_leftX = 1.194520000E-04
bk5_bottomY = 1.830740000E-04
bk5_width = 2.149010000E-04
bk5_height = 0.000171921


bk6_leftX = 0.000334353
bk6_bottomY = 1.830740000E-04
bk6_width = 2.118480000E-04
bk6_height = 1.719210000E-04


bk7_leftX = 0
bk7_bottomY = 0.000354995
bk7_width = 2.257430000E-04
bk7_height = 2.821790000E-04


bk8_leftX = 0.000225743
bk8_bottomY = 0.000354995
bk8_width = 3.204580000E-04
bk8_height = 2.821790000E-04



##### LAYER 2 #####


bk9_leftX = 0
bk9_bottomY = 0
bk9_width = 7.506660000E-05
bk9_height = 3.220780000E-04


bk10_leftX = 7.50666e-05
bk10_bottomY = 0
bk10_width = 2.347874000E-04
bk10_height = 1.890780000E-04


bk11_leftX = 0.000309854
bk11_bottomY = 0
bk11_width = 0.000236347
bk11_height = 0.000189078


bk12_leftX = 7.50666e-05
bk12_bottomY = 0.000189078
bk12_width = 2.990244000E-04
bk12_height = 0.000133


bk13_leftX = 0
bk13_bottomY = 0.000322078
bk13_width = 0.000374091
bk13_height = 9.35227e-05


bk14_leftX = 0.000374091
bk14_bottomY = 0.000189078
bk14_width = 1.721100000E-04
bk14_height = 2.265220000E-04


bk15_leftX = 0
bk15_bottomY = 0.0004156
bk15_width = 0.000223562
bk15_height = 2.215740000E-04


bk16_leftX = 0.000223562
bk16_bottomY = 0.0004156
bk16_width = 0.000122049
bk16_height = 2.215740000E-04

bk17_leftX = 0.000345611
bk17_bottomY = 0.0004156
bk17_width = 0.000136599
bk17_height = 2.215740000E-04






chipThickness =0.000020 # Thickness of active layers (can be different for each layer and even each block)
chipVHC = materials.materials["Si"]["volumetricHeatCapacity"]   # Volumetric Heat Capacity for the material of the active layers (can be different for each layer and even each block). Using default value for Silicon defined in materials.py
chipConductivity = materials.materials["Si"]["conductivity"]    # Conductivity for the material of the active layers (can be different for each layer and even each block). Using default value for Silicon defined in materials.py

chipWidth = 0.0005462   # Total width (X-axis) of active layer
chipHeight = 0.0006372  # Total height (Y-axis) of active layer


# Definition of power dissipation for each block. Power is in W. Below, the power density in Wm^-3 is converted to W using the volume of each block.

l0_b1_p = 1.000002036E+10 * bk1_width * bk1_height * chipThickness
l0_b2_p = 3.050004210E+10 * bk2_width * bk2_height * chipThickness
l0_b3_p = 7.549996340E+10 * bk3_width * bk3_height * chipThickness
l0_b4_p = 2.550001641E+10 * bk4_width * bk4_height * chipThickness
l0_b5_p = 2.050000287E+10 * bk5_width * bk5_height * chipThickness
l0_b6_p = 1.149998611E+10 * bk6_width * bk6_height * chipThickness
l0_b7_p = 3.650003782E+10 * bk7_width * bk7_height * chipThickness
l0_b8_p = 6.200007154E+10 * bk8_width * bk8_height * chipThickness

l1_b1_p = 2.049997928E+10 * bk9_width * bk9_height * chipThickness
l1_b2_p = 1.349998708E+10 * bk10_width * bk10_height * chipThickness
l1_b3_p = 1.749999293E+10 * bk11_width * bk11_height * chipThickness
l1_b4_p = 8.050000000E+10 * bk12_width * bk12_height * chipThickness
l1_b5_p = 3.049999968E+10 * bk13_width * bk13_height * chipThickness
l1_b6_p = 1.200000366E+10 * bk14_width * bk14_height * chipThickness
l1_b7_p = 1.049998327E+10 * bk15_width * bk15_height * chipThickness
l1_b8_p = 1.600007090E+10 * bk16_width * bk16_height * chipThickness
l1_b9_p = 2.849999260E+10 * bk17_width * bk17_height * chipThickness





#Optional: for transient simulations, the user may define variable power levels for each functional block.

l0_b1_p1 = 1.000002036E+10 * bk1_width * bk1_height * chipThickness
l0_b2_p1 = 3.050004210E+10 * bk2_width * bk2_height * chipThickness
l0_b3_p1 = 7.549996340E+10 * bk3_width * bk3_height * chipThickness
l0_b4_p1 = 2.550001641E+10 * bk4_width * bk4_height * chipThickness
l0_b5_p1 = 2.050000287E+10 * bk5_width * bk5_height * chipThickness
l0_b6_p1 = 1.149998611E+10 * bk6_width * bk6_height * chipThickness
l0_b7_p1 = 3.650003782E+10 * bk7_width * bk7_height * chipThickness
l0_b8_p1 = 6.200007154E+10 * bk8_width * bk8_height * chipThickness



l0_b1_p2 = 2.000002036E+10 * bk1_width * bk1_height * chipThickness
l0_b2_p2 = 9.050004210E+10 * bk2_width * bk2_height * chipThickness
l0_b3_p2 = 1.549996340E+10 * bk3_width * bk3_height * chipThickness
l0_b4_p2 = 0.550001641E+10 * bk4_width * bk4_height * chipThickness
l0_b5_p2 = 4.050000287E+10 * bk5_width * bk5_height * chipThickness
l0_b6_p2 = 2.149998611E+10 * bk6_width * bk6_height * chipThickness
l0_b7_p2 = 1.650003782E+10 * bk7_width * bk7_height * chipThickness
l0_b8_p2 = 2.200007154E+10 * bk8_width * bk8_height * chipThickness



l0_b1_p3 = 3.000002036E+10 * bk1_width * bk1_height * chipThickness
l0_b2_p3 = 1.050004210E+10 * bk2_width * bk2_height * chipThickness
l0_b3_p3 = 2.549996340E+10 * bk3_width * bk3_height * chipThickness
l0_b4_p3 = 3.550001641E+10 * bk4_width * bk4_height * chipThickness
l0_b5_p3 = 5.050000287E+10 * bk5_width * bk5_height * chipThickness
l0_b6_p3 = 3.149998611E+10 * bk6_width * bk6_height * chipThickness
l0_b7_p3 = 2.650003782E+10 * bk7_width * bk7_height * chipThickness
l0_b8_p3 = 1.200007154E+10 * bk8_width * bk8_height * chipThickness




# In the case where variable power dissipation is used, the variable power dissipations for each block must be aggregated in an array, like below

# l0_b1_p = [l0_b1_p1, l0_b1_p2, l0_b1_p3]
# l0_b2_p = [l0_b2_p1, l0_b2_p2, l0_b2_p3]
# l0_b3_p = [l0_b3_p1, l0_b3_p2, l0_b3_p3]
# l0_b4_p = [l0_b4_p1, l0_b4_p2, l0_b4_p3]
# l0_b5_p = [l0_b5_p1, l0_b5_p2, l0_b5_p3]
# l0_b6_p = [l0_b6_p1, l0_b6_p2, l0_b6_p3]
# l0_b7_p = [l0_b7_p1, l0_b7_p2, l0_b7_p3]
# l0_b8_p = [l0_b8_p1, l0_b8_p2, l0_b8_p3]




# This function takes the variable definitions above to define the layer in the model.
# In this example layer, the layer is not subdivided into different chiplets.
def makeDeviceLayer1(resolution):
    layer = []
    chiplet = []
    bk1 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk1_leftX, bk1_bottomY, bk1_width, bk1_height, l0_b1_p)
    bk2 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk2_leftX, bk2_bottomY, bk2_width, bk2_height, l0_b2_p)
    bk3 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk3_leftX, bk3_bottomY, bk3_width, bk3_height, l0_b3_p)
    bk4 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk4_leftX, bk4_bottomY, bk4_width, bk4_height, l0_b4_p)
    bk5 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk5_leftX, bk5_bottomY, bk5_width, bk5_height, l0_b5_p)
    bk6 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk6_leftX, bk6_bottomY, bk6_width, bk6_height, l0_b6_p)
    bk7 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk7_leftX, bk7_bottomY, bk7_width, bk7_height, l0_b7_p)
    bk8 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk4_leftX, bk4_bottomY, bk4_width, bk4_height, l0_b8_p)



    chiplet.append(bk1)
    chiplet.append(bk2)
    chiplet.append(bk3)
    chiplet.append(bk4)
    chiplet.append(bk5)
    chiplet.append(bk6)
    chiplet.append(bk7)
    chiplet.append(bk8)



    layer.append(chiplet)

    return layer




# In this example layer, the layer is subdivided into two different chiplets. Different chiplets means there is no lateral heat transfer between the chiplets, i.e. they are considered thermally isolated on their sides. Vertical heat transfer (to other layers) is unchanged.
def makeDeviceLayer2(resolution):
    layer = []

    chiplet1 = []
    chiplet2 = []


    bk9 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk9_leftX, bk9_bottomY, bk9_width, bk9_height, l1_b1_p)
    bk10 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk10_leftX, bk10_bottomY, bk10_width, bk10_height, l1_b2_p)
    bk11 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk11_leftX, bk11_bottomY, bk11_width, bk11_height, l1_b3_p)
    bk12 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk12_leftX, bk12_bottomY, bk12_width, bk12_height, l1_b4_p)
    bk13 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk13_leftX, bk13_bottomY, bk13_width, bk13_height, l1_b5_p)
    bk14 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk14_leftX, bk14_bottomY, bk14_width, bk14_height, l1_b6_p)
    bk15 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk15_leftX, bk15_bottomY, bk15_width, bk15_height, l1_b7_p)
    bk16 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk16_leftX, bk16_bottomY, bk16_width, bk16_height, l1_b8_p)
    bk17 = make_unit_dict(chipVHC, chipConductivity, chipThickness, resolution, bk17_leftX, bk17_bottomY, bk17_width, bk17_height, l1_b9_p)



    chiplet1.append(bk9)
    chiplet1.append(bk10)
    chiplet1.append(bk11)
    chiplet1.append(bk12)

    chiplet2.append(bk13)
    chiplet2.append(bk14)
    chiplet2.append(bk15)
    chiplet2.append(bk16)
    chiplet2.append(bk17)



    layer.append(chiplet1)
    layer.append(chiplet2)

    return layer



# A unified layer of epoxy is defined, with custom dimensions. The leftX and bottomY are set to have the active layer sit in the middle.
def make_package_layer(resolution):

    layer = []
    chiplet = []

    package = make_unit_dict(materials.materials["FR-4 epoxy"]["volumetricHeatCapacity"], materials.materials["FR-4 epoxy"]["conductivity"], 0.001, resolution, (chipWidth-0.001)/2, (chipHeight-0.001)/2, 0.001, 0.001, 0)

    chiplet.append(package)
    layer.append(chiplet)

    return layer




# A thermal interface layer is defined, similarly to above.
def make_TIM_layer(resolution):
    layer = []
    chiplet = []

    tim = make_unit_dict(materials.materials["Aluminium Silicate"]["volumetricHeatCapacity"], materials.materials["Aluminium Silicate"]["conductivity"], 0.000020, resolution, 0, 0, chipWidth, chipHeight, 0)

    chiplet.append(tim)
    layer.append(chiplet)

    return layer

# A heat spreader layer is defined, similarly to above.
def make_HSp_layer(resolution):
    layer = []
    chiplet = []

    hsp = make_unit_dict(materials.materials["Cu"]["volumetricHeatCapacity"], materials.materials["Cu"]["conductivity"], 0.000100, resolution, (chipWidth-0.003)/2, (chipHeight-0.003)/2, 0.003, 0.003, 0)

    chiplet.append(hsp)
    layer.append(chiplet)

    return layer


# A heat sink layer is defined, similarly to above.
def make_HSi_layer(resolution):
    layer = []
    chiplet = []

    hsi = make_unit_dict(materials.materials["Aluminium"]["volumetricHeatCapacity"], materials.materials["Aluminium"]["conductivity"], 0.000690, resolution, (chipWidth-0.006)/2, (chipHeight-0.006)/2, 0.006, 0.006, 0)

    chiplet.append(hsi)
    layer.append(chiplet)

    return layer

resolution = [2,2] # Resolution for all blocks (defined here as uniform, can be defined on a block-by-block basis)



# Adding all layers to the model. Order of the layers is defined here, from bottom to top.
model = [make_package_layer(resolution), makeDeviceLayer1(resolution), makeDeviceLayer2(resolution), make_TIM_layer(resolution), make_HSp_layer(resolution), make_HSi_layer(resolution)]