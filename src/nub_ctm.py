# Author: Adam Corbier (@Ad2Am2)

from copy import deepcopy

import numpy as np
import scipy
import scipy.linalg
import scipy.sparse.linalg
import time

from src import globalVar
from cmath import isclose

r_conv = 1

"""Creates the dictionary of the unit that contains all the modeling and material properties of that unit"""
def make_unit_dict(volumetricHeatCapacity, conductivity, thickness, resolution, leftX, bottomY, width, height, powerDissipation):
    unitDict = {
        "volumetricHeatCapacity": volumetricHeatCapacity,
        "conductivity": conductivity,
        "thickness": thickness,
        "resolution": resolution,
        "leftX": leftX,
        "bottomY": bottomY,
        "width": width,
        "height": height,
        "powerDissipation": powerDissipation
    }
    return(unitDict)

"""Function that turns one function unit of the structure and turn it into several smaller units, using the given resolution."""
def flatten_unit(bigUnit, layerIndex, chipletIndex, unitIndex):
    unitArray = []
    unitWidth = bigUnit["width"]/bigUnit["resolution"][0]   # The width of each smaller unit will be the width of the big unit / the number of nodes in the x direction
    unitHeight = bigUnit["height"]/bigUnit["resolution"][1]   # The height of each smaller unit will be the height of the big unit / the number of nodes in the y direction
    for rows in range (bigUnit["resolution"][1]): # For each row in the big unit (from bottom to top)
        for cols in range (bigUnit["resolution"][0]): # For each column in the big unit (from left to right)
            if type(bigUnit["powerDissipation"]) == list:

                unitDict = {
                    "volumetricHeatCapacity": bigUnit["volumetricHeatCapacity"],
                    "conductivity": bigUnit["conductivity"],
                    "thickness": bigUnit["thickness"],
                    "leftX": bigUnit["leftX"] + unitWidth*cols, # The left X of the new unit is farther to the right than that of the big unit by the number of columns preceding it times their width
                    "bottomY": bigUnit["bottomY"] + unitHeight*rows, # The bottom Y of the new unit is higher than that of the big unit by the number of rows preceding it times their height
                    "width": unitWidth,
                    "height": unitHeight,
                    "powerDissipation": [powerDissipation/(bigUnit["resolution"][0]*bigUnit["resolution"][1]) for powerDissipation in bigUnit["powerDissipation"]],
                    "layerIndex": layerIndex,
                    "chipletIndex": chipletIndex,
                    "unitIndex": unitIndex
                }
            else:
                unitDict = {
                    "volumetricHeatCapacity": bigUnit["volumetricHeatCapacity"],
                    "conductivity": bigUnit["conductivity"],
                    "thickness": bigUnit["thickness"],
                    "leftX": bigUnit["leftX"] + unitWidth*cols, # The left X of the new unit is farther to the right than that of the big unit by the number of columns preceding it times their width
                    "bottomY": bigUnit["bottomY"] + unitHeight*rows, # The bottom Y of the new unit is higher than that of the big unit by the number of rows preceding it times their height
                    "width": unitWidth,
                    "height": unitHeight,
                    "powerDissipation": bigUnit["powerDissipation"]/(bigUnit["resolution"][0]*bigUnit["resolution"][1]),
                    "layerIndex": layerIndex,
                    "chipletIndex": chipletIndex,
                    "unitIndex": unitIndex
                }
            unitArray.append(unitDict)
    return unitArray

"""Function that turns the inputted structured, separated by function blocks, and divides the units into smaller ones instead, according to each of their resolutions"""
def flatten_model(blockModel):
    model = []  # The model is still represented as an array
    for iLayer in range (len(blockModel)):
        layer = []  # Each layer is an array
        for iChiplet in range (len(blockModel[iLayer])):
            chiplet = []    # In each layer there can be several chiplets, each represented as an array
            for iUnit in range (len(blockModel[iLayer][iChiplet])):
                chiplet.extend(flatten_unit(blockModel[iLayer][iChiplet][iUnit], iLayer, iChiplet, iUnit))   # Add the new units to the chiplet
            layer.append(chiplet)
        model.append(layer)
    return(model)

"""This function calculates thermal resistance based on the thermal resistance formula R=t/CA.
To avoid a ZeroDivisionError, if the adjacency area is 0, ther function returns a very large (quasi infinite) number, 1e100.
Thermal resistance is in K/W"""
def calculate_resistance(adjacencyArea, conductivity, thickness):
    if adjacencyArea != 0:
        return thickness / (conductivity*adjacencyArea)
    else:   # In case the adjacency area returned is 0, the resistance is infinite, so we put a very large number. This is to catch any potential ZeroDivisionError
        return 1e100

"""Function that determines if 2 blocks are adjacent.
Returns 0 if not adjacent, even number if one on top of the other, odd number if one next to the other
1: the blocks are adjacent with unit1 on the right, unit2 on the left
2: the blocks are adjacent with unit1 on top, unit2 on the bottom
3: the blocks are adjacent with unit1 on the left, unit2 on the right
4: the blocks are adjacent with unit1 on the bottom, unit2 on top"""
def are_adjacent(unit1, unit2):
    if (isclose(unit1["leftX"], (unit2["leftX"]+unit2["width"])) and ((unit1["bottomY"]<=unit2["bottomY"]<unit1["bottomY"]+unit1["height"] or (isclose(unit1["bottomY"], unit2["bottomY"]) and unit2["bottomY"]<unit1["bottomY"]+unit1["height"])) or (unit2["bottomY"]<=unit1["bottomY"]<unit2["bottomY"]+unit2["height"] or (isclose(unit2["bottomY"], unit1["bottomY"]) and unit1["bottomY"]<unit2["bottomY"]+unit2["height"])))):
        return 1 # Return 1 if the blocks are adjacent with unit1 on the right, unit2 on the left
    elif (isclose(unit1["leftX"]+unit1["width"], unit2["leftX"]) and ((unit1["bottomY"]<=unit2["bottomY"]<unit1["bottomY"]+unit1["height"] or (isclose(unit1["bottomY"], unit2["bottomY"]) and unit2["bottomY"]<unit1["bottomY"]+unit1["height"])) or (unit2["bottomY"]<=unit1["bottomY"]<unit2["bottomY"]+unit2["height"] or (isclose(unit2["bottomY"], unit1["bottomY"]) and unit1["bottomY"]<unit2["bottomY"]+unit2["height"])))):
        return 3 # Return 3 if the blocks are adjacent with unit1 on the left, unit2 on the right
    elif (isclose(unit1["bottomY"], unit2["bottomY"]+unit2["height"]) and ((unit1["leftX"]<=unit2["leftX"]<unit1["leftX"]+unit1["width"] or (isclose(unit1["leftX"], unit2["leftX"]) and unit2["leftX"]<unit1["leftX"]+unit1["width"])) or (unit2["leftX"]<=unit1["leftX"]<unit2["leftX"]+unit2["width"] or (isclose(unit2["leftX"], unit1["leftX"]) and unit1["leftX"]<unit2["leftX"]+unit2["width"])))):
        return 2 # Return 2 if the blocks are adjacent with unit1 on top, unit2 on the bottom
    elif (isclose(unit1["bottomY"]+unit1["height"], unit2["bottomY"]) and ((unit1["leftX"]<=unit2["leftX"]<unit1["leftX"]+unit1["width"] or (isclose(unit1["leftX"], unit2["leftX"]) and unit2["leftX"]<unit1["leftX"]+unit1["width"])) or (unit2["leftX"]<=unit1["leftX"]<unit2["leftX"]+unit2["width"] or (isclose(unit2["leftX"], unit1["leftX"]) and unit1["leftX"]<unit2["leftX"]+unit2["width"])))):
        return 4 # Return 4 if the blocks are adjacent with unit1 on the bottom, unit2 on top
    else:
        return 0 # Return 0 if the blocks are not adjacent

"""Function that returns the area that connects unit1 and unit2. Useful in the 2D resistance calculation.
NOTE: This is the 2D function, to be used only if the units are on the same layer (and the same chiplet, or they woulld not connected).
Both thicknesses should be the same as the units are on the same layer of the same chiplet, but thickness of unit1 is used."""
def get_shared_area_2D(unit1, unit2):
    if (are_adjacent(unit1, unit2)%2 == 1):  # If the two blocks are next to each other in the X direction
        if(unit1["bottomY"] < unit2["bottomY"] and not isclose(unit1["bottomY"], unit2["bottomY"])):
            if ((unit1["bottomY"]+unit1["height"]) < (unit2["bottomY"]+unit2["height"])) and not isclose(unit1["bottomY"]+unit1["height"], unit2["bottomY"]+unit2["height"]):   # Case where shared area is between top of unit1 and bottom of unit2
                return(((unit1["bottomY"]+unit1["height"])-unit2["bottomY"])*unit1["thickness"]) # Return shared length times thickness of layer (area of adjacency)
            else:   # Case where shared area is between top of unit2 and bottom of unit2
                return(unit2["height"]*unit1["thickness"]) # Return shared length times thickness of layer (area of adjacency)
        else:
            if ((unit1["bottomY"]+unit1["height"]) < (unit2["bottomY"]+unit2["height"]) and not isclose(unit1["bottomY"]+unit1["height"], unit2["bottomY"]+unit2["height"])):   # Case where shared area is between top of unit1 and bottom of unit1
                return(unit1["height"]*unit1["thickness"]) # Return shared length times thickness of layer (area of adjacency)
            else:   # Case where shared area is between top of unit2 and bottom of unit1
                return(((unit2["bottomY"]+unit2["height"])-unit1["bottomY"])*unit1["thickness"]) # Return shared length times thickness of layer (area of adjacency)
    elif (are_adjacent(unit1, unit2)%2 == 0 and are_adjacent(unit1, unit2) != 0): # If the two blocks are one on top of the other (in the Y direction)
        if(unit1["leftX"] < unit2["leftX"] and not isclose(unit1["leftX"], unit2["leftX"])):
            if ((unit1["leftX"]+unit1["width"]) < (unit2["leftX"]+unit2["width"]) and not isclose(unit1["leftX"]+unit1["width"], unit2["leftX"]+unit2["width"])):   # Case where shared area is between left of unit2 and right of unit1
                return(((unit1["leftX"]+unit1["width"])-unit2["leftX"])*unit1["thickness"]) # Return shared length times thickness of layer (area of adjacency)
            else:   # Case where shared area is between left and right of unit2
                return(unit2["width"]*unit1["thickness"]) # Return shared length times thickness of layer (area of adjacency)
        else:
            if unit1["leftX"]+unit1["width"] < unit2["leftX"]+unit2["width"] and not isclose(unit1["leftX"]+unit1["width"], unit2["leftX"]+unit2["width"]):   # Case where shared area is between left and right of unit1
                return(unit1["width"]*unit1["thickness"]) # Return shared length times thickness of layer (area of adjacency)
            else:   # Case where shared area is between left of unit1 and right of unit2
                return(((unit2["leftX"]+unit2["width"])-unit1["leftX"])*unit1["thickness"]) # Return shared length times thickness of layer (area of adjacency)
    else:
        print("ERROR: Unexpected return value for call of are_adjacent function.")
        print("Return value of are_adjacent: ", end="")
        print(are_adjacent(unit1, unit2))
        return 0

"""Assuming that 2 units are adjacent, this function will calculate the resistance between the center node of unit1 and the middle of the shared edge of unit1 and unit2.
If units are not adjacent, returns -1 and prints error message"""
def calculate_2D_res(unit1, unit2):
    adjacencyArea = get_shared_area_2D(unit1,unit2)
    if (are_adjacent(unit1, unit2)%2 == 1):  # If unit1 and unit2 are next to one another
        return(calculate_resistance(adjacencyArea, unit1["conductivity"], unit1["width"]/2)) # Adjacency area is the area that connects the 2 units. "Thickness" is the X length between the center of unit1 and the shared edge (width/2)
    elif ((are_adjacent(unit1, unit2)%2 == 0) and (are_adjacent(unit1, unit2) != 0)): # If unit1 and unit2 are one on top of the other
        return(calculate_resistance(adjacencyArea, unit1["conductivity"], unit1["height"]/2)) # Adjacency area is the area that connects the 2 units. "Thickness" is the Y length between the center of unit1 and the shared edge (height/2)
    else: # units are not adjacent or unexpected return code from are_adjacent
        print("ERROR: Unexpected return value for call of are_adjacent function.")
        print("Return value of are_adjacent: ", end="")
        print(are_adjacent(unit1, unit2))
        return -1

"""Function that determines if 2 units are superposed.
Returns True if superposed, False if not superposed
NOTE: This assumes that the units are in adjacent layers, and does not check for the layer of each unit."""
def are_superposed(unit1, unit2):
    if (unit1["bottomY"] >= unit2["bottomY"]+unit2["height"] or isclose(unit1["bottomY"], unit2["bottomY"]+unit2["height"])) or (unit2["bottomY"] >= unit1["bottomY"]+unit1["height"] or isclose(unit2["bottomY"], unit1["bottomY"]+unit1["height"])):  # The Y coordinates of the blocks are NOT matching => not superposed
        return False # Not superposed
    else: # The Y coordinates of the blocks are matching => check for X
        if (unit1["leftX"] >= unit2["leftX"]+unit2["width"] or isclose(unit1["leftX"], unit2["leftX"]+unit2["width"])) or (unit2["leftX"] >= unit1["leftX"]+unit1["width"] or isclose(unit2["leftX"], unit1["leftX"]+unit1["width"])):    # The X coordinates of the blocks are NOT matching => not superposed
            return False # Not superposed
        else: # X are matching AND Y are matching => superposed
            return True

"""Function that gets the shared area between 2 units in adjacent layers.
NOTE: This fuction assumes that the units are superposed. If the are not superposed, this function will print an error message and reurn -1"""
def get_shared_area_3D(unit1,unit2):
    if (are_superposed(unit1, unit2) != True):
        print("ERROR: units are not superposed")
        return -1 # Filter out cases where units may not be superposed

    # Calculation of the length of the shared area in the y direction 
    if (unit1["bottomY"] < unit2["bottomY"]):
        if ((unit1["bottomY"]+unit1["height"]) < (unit2["bottomY"]+unit2["height"])):   # Case where the bottom of the shared area is the bottom of unit2, and the top is the top of unit1.
            yLength = unit1["bottomY"]+unit1["height"] - unit2["bottomY"]
        else:   # Case where the bottom of the shared area is the bottom of unit2, and the top is the top of unit2.
            yLength = unit2["height"]
    else:
        if ((unit1["bottomY"]+unit1["height"]) < (unit2["bottomY"]+unit2["height"])):   # Case where the bottom of the shared area is the bottom of unit1, and the top is the top of unit1.
            yLength = unit1["height"]
        else:   # Case where the bottom of the shared area is the bottom of unit1, and the top is the top of unit2.
            yLength = unit2["bottomY"]+unit2["height"] - unit1["bottomY"]
    
    # Calculation of the length of the shared area in the x direction
    if (unit1["leftX"] < unit2["leftX"]):
        if ((unit1["leftX"]+unit1["width"]) < (unit2["leftX"]+unit2["width"])):   # Case where the left of the shared area is the left of unit2, and the right is the right of unit1.
            xLength = unit1["leftX"]+unit1["width"] - unit2["leftX"]
        else:   # Case where the left of the shared area is the left of unit2, and the right is the right of unit2.
            xLength = unit2["width"]
    else:
        if ((unit1["leftX"]+unit1["width"]) < (unit2["leftX"]+unit2["width"])):   # Case where the left of the shared area is the left of unit1, and the right is the right of unit1.
            xLength = unit1["width"]
        else:   # Case where the left of the shared area is the left of unit1, and the right is the right of unit2.
            xLength = unit2["leftX"]+unit2["width"] - unit1["leftX"]

    return (xLength*yLength)

"""Assuming that 2 units are superposed, this function will calculate the resistance between the center node of unit1 and the middle of the shared area of unit1 and unit2.
If units are not superposed, returns -1 and prints error message"""
def calculate_3D_res (unit1, unit2):
    if (are_superposed(unit1, unit2) != True):
        print("ERROR: units are not superposed")
        return -1 # Filter out cases where units may not be superposed
    adjacencyArea = get_shared_area_3D(unit1, unit2)
    return (calculate_resistance(adjacencyArea, unit1["conductivity"], unit1["thickness"]/2))
    
"""Function that determines the border at which a unit is grounded on a chiplet (in 2D, does NOT determine if it is grounded at the top or at the bottom)
Output is a list of integers. Its length is the number of ground nodes this unit has. Each element is a 0-3 int representing the side on which the ground node is.
0 -- North border
1 -- East border
2 -- South border
3 -- West border
Output examples:
[] -- this unit has no ground nodes. Length of the list is 0
[2] -- this unit has 1 ground node, on the south border
[0,3] -- this unit has 2 ground nodes, one on the north border and one on the south border
[0,1,2,3] -- this unit has 4 ground nodes, on all 4 sides. This can only happen if it is the only unit on the chiplet."""
def get_ground_nodes(chiplet, unit):
    northGround = 1 # All side are initialized to be grounded, we will then check for each if it is in fact false
    eastGround = 1
    southGround = 1
    westGround = 1
    for i in range (len(chiplet)):
        if ((unit["leftX"] > chiplet[i]["leftX"]) and not(isclose(unit["leftX"], chiplet[i]["leftX"]))): # West border: Go through the leftX of all the units in the chiplet to check if it is smaller than all of them
            westGround = 0    # If it is not smaller than all of them, then it is not grounded on the west border (assumes chiplet is rectangular). Otherwise, it is. (Every unit has a higher or equal leftX)
        if (((unit["bottomY"]+unit["height"]) < (chiplet[i]["bottomY"]+chiplet[i]["height"])) and not(isclose(unit["bottomY"]+unit["height"], chiplet[i]["bottomY"]+chiplet[i]["height"]))):   # North border: Go through the topY of all the units in the chiplet to check if it is larger than all of them
            northGround = 0 # If not, then it is not grounded on the north border (assumes chiplet is rectangular). (Every unit has a lower or equal top Y)
        if ((unit["bottomY"] > chiplet[i]["bottomY"]) and not(isclose(unit["bottomY"], chiplet[i]["bottomY"]))):   # South border: Go through the bottomY of all the units in the chiplet to check if it is lower than all of them
            southGround = 0 # If not, then it is not grounded on the south border (assumes chiplet is rectangular). (Every unit has a lower or equal top Y)
        if (((unit["leftX"]+unit["width"]) < (chiplet[i]["leftX"]+chiplet[i]["width"])) and not(isclose(unit["leftX"]+unit["width"], chiplet[i]["leftX"]+chiplet[i]["width"]))): # East border: Go through the right X of all the units in the chiplet to check if it is higher than all of them
            eastGround = 0  # If at least one unit's rightX is higher, then it is not grounded to the east border (assumes chiplet is rectangular)
    # Create the ouput list
    groundConnections = []
    if northGround:
        groundConnections.append(0)
    if eastGround:
        groundConnections.append(1)
    if southGround:
        groundConnections.append(2)
    if westGround:
        groundConnections.append(3)
    return(groundConnections)

"""Function that creates and returns a center node. groundNodes is an array containing information about the ground nodes of the center unit (see get_ground_nodes for more info)"""
def make_center_node(unitIndex, groundNodes, layerIndex, chipletIndex):
    centerNode = {
        "type": 0,  # 0 means this is a center node
        "unitIndex": unitIndex,  # The unit it is at the center of is the unit we are currently building
        "groundNodes": groundNodes,
        "layerIndex": layerIndex,
        "chipletIndex": chipletIndex
    }
    return centerNode

"""Function that creates and returns a boundary node between unit1 and unit2"""
def make_boundary_node_2D(unit1Index, unit2Index, chipletIndex, layerIndex):
    boundaryNode = {
        "type": 1,  # 1 means this is a boundary node
        "unit1Index": unit1Index, # The index of the first unit
        "unit2Index": unit2Index,  # The index of the second unit
        "chipletIndex": chipletIndex, # The index of the chiplet
        "layerIndex": layerIndex  # The index of the layer
    }
    return boundaryNode

"""Function that creates and returns a boundary node between unit1 and unit2, where these are in adjacent layer"""
def make_boundary_node_3D(topUnitIndex, bottomUnitIndex, topChipletIndex, bottomChipletIndex, topLayerIndex, bottomLayerIndex):
    boundaryNode = {
        "type": 2,   # 2 means this is a boundary node between 2 layers
        "topUnitIndex": topUnitIndex,  # The index of the unit on layer1
        "bottomUnitIndex": bottomUnitIndex,  # The index of the unit on layer2
        "topChipletIndex": topChipletIndex,   # The index of the chiplet of topUnit
        "bottomChipletIndex": bottomChipletIndex,   # The index of the chiplet of bottomUnit
        "topLayerIndex": topLayerIndex,   # The index of the layer of topUnit
        "bottomLayerIndex": bottomLayerIndex    # The index of the layer of bottomUnit
    }
    return boundaryNode

def make_ground_node(unitIndex, chipletIndex, layerIndex, side):
    groundNode = {
        "type": 3,
        "unitIndex": unitIndex,
        "chipletIndex": chipletIndex,
        "layerIndex": layerIndex,
        "side": side
    }
    return groundNode
def make_unit_ground_nodes(unitIndex, chipletIndex, layerIndex, groundNodes2D, model):
    groundNodes = []
    for i in range (len(groundNodes2D)):
        groundNodes.append(make_ground_node(unitIndex, chipletIndex, layerIndex, groundNodes2D[i]))
    groundNodes.extend(make_unit_ground_nodes_3D(unitIndex, chipletIndex, layerIndex, model))
    return groundNodes

    
"""Function that creates the nodes for a chiplet"""
def make_chiplet_nodes(chiplet, layerIndex, chipletIndex, model):
    chipletNodes = []  # This will be an array of the nodes of the chiplet
    for i in range (len(chiplet)):  # Go through each unit fo the chiplet
        # Make center node of the unit
        groundNodes = get_ground_nodes(chiplet, chiplet[i])
        centerNode = make_center_node(i, groundNodes, layerIndex, chipletIndex)
        chipletNodes.append(centerNode)
        chipletNodes.extend(make_unit_ground_nodes(i, chipletIndex, layerIndex, groundNodes, model))
    return chipletNodes

"""Function that returns an array of all the nodes on a layer"""
def make_layer_nodes(layer, layerIndex, model):
    nodes = []
    for i in range (len(layer)):
        nodes.extend(make_chiplet_nodes(layer[i], layerIndex, i, model))
    return nodes

"""Function that take a chiplet and returns a dictionary of its leftX, rightX, bottomY, and topY.
It also inculdes height and width to be able to check for superposition with are_superposed"""
def get_chiplet_coordinates(chiplet):
    leftX = chiplet[0]["leftX"] # Default leftX is the first unit's leftX
    bottomY = chiplet[0]["bottomY"] # Default bottomY is the first unit's bottomY
    rightX = chiplet[0]["leftX"]+chiplet[0]["width"]    # Default rightX is the first unit's rightX
    topY = chiplet[0]["bottomY"]+chiplet[0]["height"]   # Default topY is the first unit's topY
    for i in range (len(chiplet)):  # For each unit in the chiplet
        if chiplet[i]["leftX"]<leftX:   # If the unit's leftX is lower than the current definition of leftX (aka. more to the left), replace the current definiation of leftX with that.
            leftX = chiplet[i]["leftX"]
        if chiplet[i]["bottomY"]<bottomY:   # If the unit's bottomY is lower than the current definition of bottomY (aka. lower physically), replace the current definition of bottomY with that.
            bottomY = chiplet[i]["bottomY"]
        if (chiplet[i]["leftX"]+chiplet[i]["width"])>rightX:    # If the unit's rightX is higher than the current definition of rightX (aka. more to the right), replace the current definition of rightX with that.
            rightX = chiplet[i]["leftX"]+chiplet[i]["width"]
        if (chiplet[i]["bottomY"]+chiplet[i]["height"])>topY:   # If the unit's topY is higher than the current definition of topY (aka. higher physically), replace the current definition of topY with that.
            topY = chiplet[i]["bottomY"]+chiplet[i]["height"]
    # Once this loop is over, leftX corresponds to the leftmost part of the chip, bottomY the bottommost, etc.
    height = topY - bottomY
    width = rightX - leftX
    # We now fill the output dictionary and return it
    chipletCoordinates = {
        "bottomY": bottomY,
        "topY": topY,
        "leftX": leftX,
        "rightX": rightX,
        "height": height,
        "width": width
    }
    return chipletCoordinates

"""Function that determines if 2 chiplets are superposed.
NOTE: this function does NOT check if they are on adjacent layers"""
def chiplets_are_superposed(chiplet1, chiplet2):
    chiplet1Coords = get_chiplet_coordinates(chiplet1)  # Gets the coordinates for chiplets (bottomY, leftX, topY, rightX)
    chiplet2Coords = get_chiplet_coordinates(chiplet2)
    return(are_superposed(chiplet1Coords, chiplet2Coords))

"""Function that returns an array of the boundary nodes between 2 adjacent layers topLayer and bottomLayer."""
def make_3D_boundary_nodes(topLayer, bottomLayer, topLayerIndex, bottomLayerIndex):
    nodes = []
    for i in range (len(topLayer)):   # For each chiplet on layer1
        for j in range (len(bottomLayer)):   # For each chiplet on layer2
            if chiplets_are_superposed(topLayer[i], bottomLayer[j]):   # If the chiplets are not superposed, there will be no boundary nodes between the 2, we can therefore ignore these cases
                for a in range(len(topLayer[i])): # For each unit of the i-th chiplet of layer1
                    for b in range (len(bottomLayer[j])):    # For each unit of the j-th chiplet of layer2
                        if (are_superposed(topLayer[i][a], bottomLayer[j][b])):    # If the 2 units are superposed, we must create a boundary node between them. Otherwise, no boundary node needs to be created
                            nodes.append(make_boundary_node_3D(a, b, i, j, topLayerIndex, bottomLayerIndex))
    return nodes

"""Function that returns an array of all the nodes in the model"""
def make_nodes(model):
    nodes = []
    for i in range (len(model)):    # For each layer in the model
        nodes.extend(make_layer_nodes(model[i], i, model))
    return nodes

"""Function that initializes the G or C matrix to the correct size according to how many nodes the system has.
The G and C matrices are the same at initialization, so the function is the same.
There are as many rows&columns as there are nodes.
All values are initialized to 0."""
def initialize_GC_matrix(nodes):
    # matrix = np.zeros((len(nodes), len(nodes)))
    matrix = [] # Define the matrix
    for columns in range (len(nodes)):  # There are as many rows and columns as there are nodes
        row = []
        for rows in range (len(nodes)):
            row.append(0)   # Make row of 0s
        matrix.append(row)  # Append that row of 0s to the matrix
    return matrix




"""Function that populates the G matrix for a resistance from a center node to the ground, in accordance to the format of MNA (Modified Nodal Analysis) for the solver of the system."""
def populate_ground_G(centerNodeIndex, groundR):
    globalVar.GMatrix[centerNodeIndex][centerNodeIndex] += 1/groundR  # G is 1/R. We append the calculated G to ground to the matrix, conforming to the format of MNA.

"""Function that populates the G matrix for a resistance from a center node to a boundary node, in accordance to the format of MNA (Modified Nodal Analysis) for the solver of the system.
Returns the updated G matrix (G = 1/r)"""
def populate_center_to_boundary_G(centerNodeIndex, boundaryNodeIndex, r):
    globalVar.GMatrix[centerNodeIndex][centerNodeIndex] += 1/r
    globalVar.GMatrix[boundaryNodeIndex][boundaryNodeIndex] += 1/r
    globalVar.GMatrix[centerNodeIndex][boundaryNodeIndex] += -1/r
    globalVar.GMatrix[boundaryNodeIndex][centerNodeIndex] += -1/r

"""Function that returns an array of the indexes of all the 2D boundary nodes connected to the unit given"""
def find_unit_boundary_nodes_2D(nodes, unitIndex, chipletIndex, layerIndex):
    boundaryNodes = []
    for i in range (len(nodes)):    # Check every node in the system
        if nodes[i].get("layerIndex") == layerIndex:    # If node is in the correct layer
            if nodes[i].get("chipletIndex") == chipletIndex:    # If node is in the correct chiplet
                if (nodes[i].get("unit1Index") == unitIndex) or (nodes[i].get("unit2Index") == unitIndex):  # If one of the connecting units is the correct unit
                    if nodes[i].get("type") == 1:   # If this node is a 2D boundary node
                        boundaryNodes.append(i) # Append node index to the list
    return boundaryNodes

"""Function that returns an array of the indexes of all the 3D boundary nodes connected to the unit given"""
def find_unit_boundary_nodes_3D(nodes, unitIndex, chipletIndex, layerIndex):
    boundaryNodes = []
    # Find the boundary nodes to the bottom of the unit
    for i in range (len(nodes)):    # Check all the nodes in the system
        if nodes[i].get("topLayerIndex") == layerIndex: # If the top layer of the node is the layer of the unit
            if nodes[i].get("topChipletIndex") == chipletIndex: # If the chiplet of the node is the chiplet of the unit
                if nodes[i].get("topUnitIndex") == unitIndex:   # If the unit of the node is the unit we are looking for
                    if nodes[i].get("type") == 2:   # If the node is a 3D boundary node
                        boundaryNodes.append(i) # Append node index to the list
        elif nodes[i].get("bottomLayerIndex") == layerIndex: # If the bottom layer of the node is the layer of the unit
            if nodes[i].get("bottomChipletIndex") == chipletIndex: # If the chiplet of the node is the chiplet of the unit
                if nodes[i].get("bottomUnitIndex") == unitIndex:   # If the unit of the node is the unit we are looking for
                    if nodes[i].get("type") == 2:   # If the node is a 3D boundary node
                        boundaryNodes.append(i) # Append node index to the list
    return boundaryNodes

def find_unit_ground_nodes(nodes, unitIndex, chipletIndex, layerIndex):
    groundNodes = []
    for i in range (len(nodes)):    # Check every node in the system
        if nodes[i].get("layerIndex") == layerIndex:    # If node is in the correct layer
            if nodes[i].get("chipletIndex") == chipletIndex:    # If node is in the correct chiplet
                if nodes[i].get("unitIndex") == unitIndex: # If unit is the correct unit
                    if nodes[i].get("type") == 3:   # If this node is a 2D ground node
                        groundNodes.append(i) # Append node index to the list
    return groundNodes

def find_unit_ground_nodes_3D(nodes, unitIndex, chipletIndex, layerIndex):
    groundNodes = []
    for i in range (len(nodes)):    # Check every node in the system
        if nodes[i].get("layerIndex") == layerIndex:    # If node is in the correct layer
            if nodes[i].get("chipletIndex") == chipletIndex:    # If node is in the correct chiplet
                if nodes[i].get("unitIndex") == unitIndex: # If unit is the correct unit
                    if nodes[i].get("type") == 4:   # If this node is a 3D ground node
                        groundNodes.append(i) # Append node index to the list
    return groundNodes

"""Function that finds the area at the top of a unit that is connected to ground (not connected to any unit on top), then accordingly calculates the resistance to ground of the unit to the top side.
find_unit_top_ground_R gives non-infinite but very large resistance if not connected to ground (which is good/normal because that means no 1/0 in the R calculation"""
def find_unit_top_ground_R(model, layerIndex, boundaryUnits, unit):
    unitGroundArea = unit["height"] * unit["width"] # Initialize the ground area to the whole area of the unit. We will then chip away at it for each boundary.
    if layerIndex == len(model) - 1:
        return calculate_resistance(unitGroundArea, unit["conductivity"], unit["thickness"]/2)
    for i in range (len(boundaryUnits)):
        unitGroundArea -= get_shared_area_3D(unit, model[layerIndex + 1][boundaryUnits[i][0]][boundaryUnits[i][1]])   # Subtract the area that is shared with the unit below.
    bottomR = calculate_resistance(unitGroundArea, unit["conductivity"], unit["thickness"]/2)
    return bottomR   # Any area that is left is area that is not connected to a unit on the bottom, it is therefore connected to the ground.

"""Function that finds the area at the bottom of a unit that is connected to ground (not connected to any unit on the bottom), then accordingly calculates the resistance to ground of the unit to the bottom side."""
def find_unit_bottom_ground_R(model, layerIndex, boundaryUnits, unit):
    unitGroundArea = unit["height"] * unit["width"] # Initialize the ground area to the whole area of the unit. We will then chip away at it for each boundary.
    if layerIndex == 0:
        return calculate_resistance(unitGroundArea, unit["conductivity"], unit["thickness"]/2)
    for i in range (len(boundaryUnits)):
        unitGroundArea -= get_shared_area_3D(unit, model[layerIndex - 1][boundaryUnits[i][0]][boundaryUnits[i][1]])   # Subtract the area that is shared with the unit below.
    bottomR = calculate_resistance(unitGroundArea, unit["conductivity"], unit["thickness"]/2)
    return bottomR   # Any area that is left is area that is not connected to a unit on the bottom, it is therefore connected to the ground.

def find_unit_bottom_ground_area(layerIndex, chipletIndex, unitIndex, model):
    unit = model[layerIndex][chipletIndex][unitIndex]
    unitGroundArea = unit["height"] * unit["width"] # Initialize the ground area to the whole area of the unit. We will then chip away at it for each boundary.
    if layerIndex == 0:
        return unitGroundArea
    boundaryUnits = []
    for j in range (len(model[layerIndex-1])):   # For each chiplet on the bottom layer
        if chiplets_are_superposed(model[layerIndex][chipletIndex], model[layerIndex-1][j]):   # If the chiplets are not superposed, there will be no boundary nodes between the 2, we can therefore ignore these cases
            for b in range (len(model[layerIndex-1][j])):    # For each unit of the j-th chiplet of layer2
                if (are_superposed(unit, model[layerIndex-1][j][b])):    # If the 2 units are superposed, we must create a boundary node between them. Otherwise, no boundary node needs to be created
                    boundaryUnits.append(model[layerIndex-1][j][b])
    for i in range (len(boundaryUnits)):
        unitGroundArea -= get_shared_area_3D(unit, boundaryUnits[i])
    return unitGroundArea

def find_unit_top_ground_area(layerIndex, chipletIndex, unitIndex, model):
    unit = model[layerIndex][chipletIndex][unitIndex]
    unitGroundArea = unit["height"] * unit["width"] # Initialize the ground area to the whole area of the unit. We will then chip away at it for each boundary.
    if layerIndex == len(model)-1:
        return unitGroundArea
    boundaryUnits = []
    for j in range (len(model[layerIndex+1])):   # For each chiplet on the top layer
        if chiplets_are_superposed(model[layerIndex][chipletIndex], model[layerIndex+1][j]):   # If the chiplets are not superposed, there will be no boundary nodes between the 2, we can therefore ignore these cases
            for b in range (len(model[layerIndex+1][j])):    # For each unit of the j-th chiplet of layer2
                if (are_superposed(unit, model[layerIndex+1][j][b])):    # If the 2 units are superposed, we must create a boundary node between them. Otherwise, no boundary node needs to be created
                    boundaryUnits.append(model[layerIndex+1][j][b])
    for i in range (len(boundaryUnits)):
        unitGroundArea -= get_shared_area_3D(unit, boundaryUnits[i])
    return unitGroundArea


def make_ground_node_3D(unitIndex, chipletIndex, layerIndex, side, area):
    groundNode = {
        "type": 4,
        "unitIndex": unitIndex,
        "chipletIndex": chipletIndex,
        "layerIndex": layerIndex,
        "side": side,
        "groundArea": area
    }
    return groundNode

def make_unit_ground_nodes_3D(unitIndex, chipletIndex, layerIndex, model):
    groundNodes = []
    if find_unit_bottom_ground_area(layerIndex, chipletIndex, unitIndex, model) > 0:
        groundNodes.append(make_ground_node_3D(unitIndex, chipletIndex, layerIndex, 0, find_unit_bottom_ground_area(layerIndex, chipletIndex, unitIndex, model)))
    if find_unit_top_ground_area(layerIndex, chipletIndex, unitIndex, model) > 0:
        groundNodes.append(make_ground_node_3D(unitIndex, chipletIndex, layerIndex, 1, find_unit_top_ground_area(layerIndex, chipletIndex, unitIndex, model)))
    return groundNodes



"""Function that populates the GMatrix with all the resistances that it is connected to. Includes 2D and 3D."""
def make_center_node_resistances(centerNode, centerNodeIndex, nodes, model):
    unit = model[centerNode["layerIndex"]][centerNode["chipletIndex"]][centerNode["unitIndex"]]
    # Calculate resistances to ground
    groundNodes = find_unit_ground_nodes(nodes, centerNode["unitIndex"], centerNode["chipletIndex"], centerNode["layerIndex"])
    for i in range(len(groundNodes)):
        if nodes[groundNodes[i]]["side"] == 0 or nodes[groundNodes[i]]["side"] == 2:  # If the ground node is to the north or to the south
            populate_center_to_boundary_G(centerNodeIndex, groundNodes[i], calculate_resistance(unit["thickness"] * unit["width"], unit["conductivity"], unit["height"] / 2))  # Area adjacent to ground is thickness of the unit * width of the unit, distance from the middle X of the unit to the top/bottom X is height/2
        if nodes[groundNodes[i]]["side"] == 1 or nodes[groundNodes[i]]["side"] == 3:  # If the ground node is to the north or to the south
            populate_center_to_boundary_G(centerNodeIndex, groundNodes[i], calculate_resistance(unit["thickness"] * unit["height"], unit["conductivity"],unit["width"] / 2))  # Area adjacent to ground is thickness of the unit * height of the unit, distance from the middle X of the unit to the right/left X is width/2

    # Calculate 2D boundary resistances
    boundaryUnits = []

    chiplet = model[centerNode["layerIndex"]][centerNode["chipletIndex"]]
    for i in range (centerNode["unitIndex"]+1, len(chiplet)):
        if are_adjacent(unit, chiplet[i]):
            boundaryUnits.append(i)

    for i in range(len(boundaryUnits)):
        r = calculate_2D_res(unit, chiplet[boundaryUnits[i]])    # Calculate the resistance between the centerNode and the other unit's boundary
        r += calculate_2D_res(chiplet[boundaryUnits[i]], unit)   # Calculate the resistance between the other unit and the boundary
        populate_center_to_boundary_G(centerNodeIndex, find_unit_center_node_index(centerNode["layerIndex"], centerNode["chipletIndex"], boundaryUnits[i], nodes), r)  # Populate this value in the G matrix for the solver


    # Calculate 3D boundary resistances
    boundaryUnitsAbove = []
    if (centerNode["layerIndex"] + 1 != len(model)):  # If this is not the last layer
        for i in range(len(model[centerNode["layerIndex"] + 1])):   # For each chiplet in the layer above the unit
            if (chiplets_are_superposed(model[centerNode["layerIndex"]][centerNode["chipletIndex"]], model[centerNode["layerIndex"] + 1][i])):
                for j in range (len(model[centerNode["layerIndex"] + 1][i])):   # For each unit of each superposed chiplet
                    if are_superposed(unit, model[centerNode["layerIndex"] + 1][i][j]):
                        boundaryUnitsAbove.append([i,j])


    for i in range(len(boundaryUnitsAbove)):
        # Calculate the resistance between the centerNode and the boundaryNode
        r = calculate_3D_res(unit, model[centerNode["layerIndex"] + 1][boundaryUnitsAbove[i][0]][boundaryUnitsAbove[i][1]])
        r += calculate_3D_res(model[centerNode["layerIndex"] + 1][boundaryUnitsAbove[i][0]][boundaryUnitsAbove[i][1]], unit)
        populate_center_to_boundary_G(centerNodeIndex, find_unit_center_node_index(centerNode["layerIndex"] + 1, boundaryUnitsAbove[i][0], boundaryUnitsAbove[i][1], nodes), r)  # Populate this value in the G matrix for the solver

    # Calculate 3D ground resistances
    groundNodes3D = find_unit_ground_nodes_3D(nodes, centerNode["unitIndex"], centerNode["chipletIndex"], centerNode["layerIndex"])

    boundaryUnitsBelow = []
    if (centerNode["layerIndex"] != 0):  # If this is not the first layer
        for i in range(len(model[centerNode["layerIndex"] - 1])):   # For each chiplet in the layer below the unit
            if (chiplets_are_superposed(model[centerNode["layerIndex"]][centerNode["chipletIndex"]], model[centerNode["layerIndex"] - 1][i])):
                for j in range (len(model[centerNode["layerIndex"] - 1][i])):   # For each unit of each superposed chiplet
                    if are_superposed(unit, model[centerNode["layerIndex"] - 1][i][j]):
                        boundaryUnitsBelow.append([i,j])


    for i in range(len(groundNodes3D)):
        if nodes[groundNodes3D[i]]["side"] == 0:  # If ground is on bottom
            groundBottomR = find_unit_bottom_ground_R(model, centerNode["layerIndex"], boundaryUnitsBelow, unit)
            populate_center_to_boundary_G(centerNodeIndex, groundNodes3D[i], groundBottomR)
        if nodes[groundNodes3D[i]]["side"] == 1:  # If ground is on top
            groundTopR = find_unit_top_ground_R(model, centerNode["layerIndex"], boundaryUnitsAbove, unit)
            populate_center_to_boundary_G(centerNodeIndex, groundNodes3D[i], groundTopR)
            if len(model) - 1 == centerNode["layerIndex"]:
                unitArea = unit["width"] * unit["height"]

                r = 1/(1200*unitArea)
                populate_ground_G(groundNodes3D[i], r)



"""This function calculates capacitance (heat capacity) based on the thermal capacitance formula C = c*t*A
Where C is capacitance, c is volumetric heat capacity in J/(m^3*K), t is thickness, and A is area = height*width
Thermal resistance is in J/K"""
def calculate_capacitance(volumetricHeatCapacity, thickness, height, width):
    return volumetricHeatCapacity*thickness*height*width

"""Function that populates the C matrix for a capacitor from a center node to the ground, in accordance to the format of MNA (Modified Nodal Analysis) for the solver of the system."""
def populate_ground_C(centerNodeIndex, c):
    globalVar.CMatrix[centerNodeIndex][centerNodeIndex] += c

"""Function that returns the capacitance to ground of the given unit"""
def get_unit_capacitance(unit):
    return calculate_capacitance(unit["volumetricHeatCapacity"], unit["thickness"], unit["height"], unit["width"])

"""Function that creates and populates the C matrix used by the MNA solver for the whole system.
After calling this function, the matrix is ready to be sent to the solver."""
def populate_C_matrix(nodes, model):
    globalVar.CMatrix = initialize_GC_matrix(nodes)   # Initilize the C matrix as a global variable so that any function can access it and modify it
    for i in range (len(nodes)):    # Go through each node in the system
        if nodes[i]["type"] == 0:   # If the node is a center node. All capacitances are connected to exactly one center node and to ground, so by populating for each center node, we have populated the whole system. 
            populate_ground_C(i, get_unit_capacitance(model[nodes[i]["layerIndex"]][nodes[i]["chipletIndex"]][nodes[i]["unitIndex"]]))  # Populate the C matrix for the capacitance to ground connected to that center node.

"""Function that initializes the I vector, representing the power Dissipation in the thermal model, and the current sources in the electrical model.
It is a vector where each index represents a node, it is therefore as long as there are nodes.
Initial values of all elements are 0."""
def initialize_I_vector(nodes):
    vector = []    # Create vector (modeled as an array)
    for i in range (len(nodes)):
        vector.append(0)   # Add as many elements as there are nodes. Values of elements are all 0.
    return vector

"""Populates the value of the I vector for a center node, in accordance to the format of MNA (Modified Nodal Analysis) for the solver of the system.
I represents the power dissipation of the unit. It is considered that the power dissipation comes from ground to the center node of the unit."""
def populate_centerNode_I(centerNode, centerNodeIndex, model, nodes):
    if type(model[nodes[centerNodeIndex]["layerIndex"]][nodes[centerNodeIndex]["chipletIndex"]][nodes[centerNodeIndex]["unitIndex"]]["powerDissipation"]) == list:
        globalVar.IVector[centerNodeIndex] = model[centerNode["layerIndex"]][centerNode["chipletIndex"]][centerNode["unitIndex"]]["powerDissipation"][0]
    else:
        globalVar.IVector[centerNodeIndex] = model[centerNode["layerIndex"]][centerNode["chipletIndex"]][centerNode["unitIndex"]]["powerDissipation"]

"""Populates the I vector for all center nodes of the model. Once the IVector has gone through this function, it is ready to be sent to the solver."""
def populate_I_vector(nodes, model):
    globalVar.IVector = initialize_I_vector(nodes)
    for i in range (len(nodes)):
        if nodes[i]["type"] == 0:   # If the node is a center node (type 0 is a center node)
            populate_centerNode_I(nodes[i], i, model, nodes)


def populate_I_vector_vector_transient(nodes, model, steps):
    IVectorVector = []

    for i in range(steps):
        IVector = initialize_I_vector(nodes)
        for j in range (len(nodes)):
            if nodes[j]["type"] == 0:
                if type(model[nodes[j]["layerIndex"]][nodes[j]["chipletIndex"]][nodes[j]["unitIndex"]]["powerDissipation"]) == list:
                    if len(model[nodes[j]["layerIndex"]][nodes[j]["chipletIndex"]][nodes[j]["unitIndex"]]["powerDissipation"]) != steps:
                        print("Error: power dissipation list length does not match number of steps")
                        return
                    IVector[j] = model[nodes[j]["layerIndex"]][nodes[j]["chipletIndex"]][nodes[j]["unitIndex"]]["powerDissipation"][i]
                else:
                    IVector[j] = model[nodes[j]["layerIndex"]][nodes[j]["chipletIndex"]][nodes[j]["unitIndex"]]["powerDissipation"]
        IVectorVector.append(IVector)
    return IVectorVector



# Solvers

def solve_steady_state():
    return scipy.sparse.linalg.spsolve(globalVar.GMatrix, globalVar.IVector)




def divideMatrix(matrix, constant):
    dividedMatrix = deepcopy(matrix) # Create a dummy variable so that global variables are not modified by this function
    for i in range(len(dividedMatrix)):
        for j in range(len(dividedMatrix[i])):
            dividedMatrix[i][j] = dividedMatrix[i][j] / constant
    return dividedMatrix


def bEuler(nSteps, timeStep, GMatrix, CMatrix, IVector, oldX):
    # If not nSteps as input, then nSteps = (t2-t1)/h
    h = timeStep / nSteps
    # t2-t1 is the time interval between 2 lines
    # inputs: nSteps, timeInt
    # h=timeInt/nSteps
    XVector = []
    for i in range(1):
        # print("Backwards Euler progress: " + str(i*100/nSteps) + "%")
        # print("Computing step "+str(i)+"...")
        # oldX = np.zeros(len(GMatrix))
        A = np.add(GMatrix, divideMatrix(CMatrix, h))
        C = np.array(divideMatrix(CMatrix, h)).dot(oldX)
        B = np.add(IVector, C)
        newX = np.linalg.solve(A,B)
        XVector.append(newX)
        oldX = newX
        # printInfo(newX, nodes, model)
    return newX



def doBeuler(GMatrix, CMatrix, IVectorVector, initTempVector, stepDefinition):
    tTempVector = []
    for i in range(len(stepDefinition)):

        for j in range(stepDefinition[i]["steps"]):
            
            stepStartTime = time.time()
            progress = (i*100/len(stepDefinition)) + (j*100/stepDefinition[i]["steps"])/len(stepDefinition)
            print("Backwards Euler progress: " + str(progress) + "%")
            print("Computing step "+str(i+1)+", substep "+str(j+1)+"...")

            if (len(tTempVector) == 0):
                initTempVector = initTempVector
            else:
                initTempVector = tTempVector[-1]
            
            tTempVector.append(bEuler(stepDefinition[i]["steps"], stepDefinition[i]["duration"], GMatrix, CMatrix, IVectorVector[i], initTempVector))

            stepEndTime = time.time()

            print("Step time: " + str(stepEndTime-stepStartTime) + " seconds", end='\n')


    return tTempVector







# Helper functions

def find_center_temperatures(model, nodes, tempVector):
    centerNodeNumber = 0
    unitArray = []
    chipletArray = []
    layerArray = []
    modelArray = []
    currentLayer = 0
    currentChiplet = 0
    currentUnit = 0
    for i in range(len(nodes)):
        nodes[i]["temperature"] = tempVector[i]
    for i in range(len(nodes)):
        if nodes[i]["type"] == 0:   # If the node is a center node (type 0 is a center node)
            unit = model[nodes[i]["layerIndex"]][nodes[i]["chipletIndex"]][nodes[i]["unitIndex"]]
            if (unit["unitIndex"] == currentUnit and unit["chipletIndex"] == currentChiplet and unit["layerIndex"] == currentLayer):   # If node is in current unit, append temp, otherwise, create new array and update currentVars
                unitArray.append(nodes[i]["temperature"])
            if currentLayer != unit["layerIndex"]:
                chipletArray.append(unitArray)
                layerArray.append(chipletArray)
                modelArray.append(layerArray)
                unitArray = []
                chipletArray = []
                layerArray = []
                currentLayer = unit["layerIndex"]
                currentChiplet = unit["chipletIndex"]
                currentUnit = unit["unitIndex"]
                unitArray.append(nodes[i]["temperature"])
            elif currentChiplet != unit["chipletIndex"]:
                chipletArray.append(unitArray)
                layerArray.append(chipletArray)
                unitArray = []
                chipletArray = []
                currentChiplet = unit["chipletIndex"]
                currentUnit = unit["unitIndex"]
                unitArray.append(nodes[i]["temperature"])
            elif currentUnit != unit["unitIndex"]:
                chipletArray.append(unitArray)
                unitArray = []
                currentUnit = unit["unitIndex"]
                unitArray.append(nodes[i]["temperature"])
    chipletArray.append(unitArray)
    layerArray.append(chipletArray)
    modelArray.append(layerArray)

    return modelArray


def get_unit_average_temps(modelTempArray):
    modelAverageTempArray = []
    for layer in range (len(modelTempArray)):
        modelAverageTempArray.append([])
        for chiplet in range (len(modelTempArray[layer])):
            modelAverageTempArray[layer].append([])
            for unit in range (len(modelTempArray[layer][chiplet])):
                averageTemp = np.average(modelTempArray[layer][chiplet][unit])
                modelAverageTempArray[layer][chiplet].append(averageTemp)
    return modelAverageTempArray

def get_unit_max_temps(modelTempArray):
    modelAverageTempArray = []
    for layer in range (len(modelTempArray)):
        modelAverageTempArray.append([])
        for chiplet in range (len(modelTempArray[layer])):
            modelAverageTempArray[layer].append([])
            for unit in range (len(modelTempArray[layer][chiplet])):
                averageTemp = np.max(modelTempArray[layer][chiplet][unit])
                modelAverageTempArray[layer][chiplet].append(averageTemp)
    return modelAverageTempArray

def get_unit_min_temps(modelTempArray):
    modelAverageTempArray = []
    for layer in range (len(modelTempArray)):
        modelAverageTempArray.append([])
        for chiplet in range (len(modelTempArray[layer])):
            modelAverageTempArray[layer].append([])
            for unit in range (len(modelTempArray[layer][chiplet])):
                averageTemp = np.min(modelTempArray[layer][chiplet][unit])
                modelAverageTempArray[layer][chiplet].append(averageTemp)
    return modelAverageTempArray

def get_unit_center_temps(modelTempArray):
    """Get the center temperature(s) for each unit. Works with any grid size."""
    modelAverageTempArray = []
    for layer in range(len(modelTempArray)):
        modelAverageTempArray.append([])
        for chiplet in range(len(modelTempArray[layer])):
            modelAverageTempArray[layer].append([])
            for unit in range(len(modelTempArray[layer][chiplet])):
                temps = modelTempArray[layer][chiplet][unit]
                n = len(temps)
                
                if n == 1:
                    # Only one element, use it directly
                    averageTemp = temps[0]
                else:
                    # Try to determine if it's a square grid
                    side = int(np.sqrt(n))
                    if side * side == n:
                        # square grid
                        if side % 2 == 1:
                            # single center element
                            center_idx = (side // 2) * side + (side // 2)
                            averageTemp = temps[center_idx]
                        else:
                            # average of 4 center elements
                            half = side // 2
                            center_indices = [
                                (half - 1) * side + (half - 1),
                                (half - 1) * side + half,
                                half * side + (half - 1),
                                half * side + half
                            ]
                            averageTemp = np.average([temps[i] for i in center_indices])
                    else:
                        # Not a perfect square, use  middle element
                        averageTemp = temps[n // 2]
                
                modelAverageTempArray[layer][chiplet].append(averageTemp)
    return modelAverageTempArray

def printInfo(tempVector, nodes, model, outputFile):
    maxTemp = max(tempVector)
    # print("Max temperature: ", maxTemp)
    minTemp = min(tempVector)
    # print("Min temperature: ", minTemp)
    averageTemp = np.average(tempVector)
    # print("Average temperature: ", averageTemp)
    modelTemp = find_center_temperatures(model, nodes, tempVector)
    # print("Temperatures of center nodes: \n")
    # for i in range(len(modelTemp)):
        # print(modelTemp[i])
    with open(outputFile, 'w') as outfile:
        outfile.write('\n\n\n'.join(str(i) for i in modelTemp))
    averageUnitTemps = get_unit_average_temps(modelTemp)
    # print("Average temperature of the units:\n", averageUnitTemps)
    # print("All temps: \n", tempVector)
    maxUnitTemps = get_unit_max_temps(modelTemp)
    # print("Max temperature of the units: \n", maxUnitTemps)
    minUnitTemps = get_unit_min_temps(modelTemp)
    # print("Min temperature of the units: \n", minUnitTemps)
    centerUnitRunOne = get_unit_center_temps(modelTemp)
    # print("Center temperature of the units: \n", centerUnitRunOne)
    maxTemp = max(tempVector)
    # print("Max temperature: ", maxTemp)
    minTemp = min(tempVector)
    # print("Min temperature: ", minTemp)
    averageTemp = np.average(tempVector)
    # print("Average temperature: ", averageTemp)

def printInfoCenters(tempVector, nodes, model):
    maxTemp = max(tempVector)
    print("Max temperature: ", maxTemp)
    minTemp = min(tempVector)
    print("Min temperature: ", minTemp)
    averageTemp = np.average(tempVector)
    print("Average temperature: ", averageTemp)
    modelTemp = find_center_temperatures(model, nodes, tempVector)
    centerUnitRunOne = get_unit_center_temps(modelTemp)
    print("Center temperature of the units: \n", centerUnitRunOne)









def saveTransientInfo(tempVector, stepDefinition, nodes, model, fileName):
    outString = ""
    startTimeAtStep = 0
    startStepsAtStep = 0
    for i in range(len(stepDefinition)):
        for j in range(stepDefinition[i]["steps"]):
            outString += "Step " + str(i+1) + ", substep " + str(j+1) + ":\n"
            outString += "Time: " + str(startTimeAtStep + (j+1)*(stepDefinition[i]["duration"]/stepDefinition[i]["steps"])) + "s\n"
            outString += "Center temperatures:\n"
            modelTemp = find_center_temperatures(model, nodes, tempVector[startStepsAtStep + j])
            outString += str('\n\n\n'.join(str(i) for i in modelTemp)) + "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
        
        startTimeAtStep += stepDefinition[i]["duration"]
        startStepsAtStep += stepDefinition[i]["steps"]

    with open(fileName, 'w') as outfile:
        outfile.write(outString)





def find_center_nodes(nodes):
    centerNodes = []
    for i in range(len(nodes)):
        if nodes[i]["type"] == 0:   # If the node is a center node (type 0 is a center node)
            centerNodes.append(i)

    return centerNodes


"""Function that creates and populates the G matrix used by the MNA solver for the whole system.
After calling this function, the matrix is ready to be sent to the solver."""
def populate_G_matrix(nodes, model):
    centerNodes = find_center_nodes(nodes)
    for i in range(len(centerNodes)):   # All resistances are connected to exactly one center node, so by populating for each center node, we have populated the whole system.
        make_center_node_resistances(nodes[centerNodes[i]], centerNodes[i], nodes, model)   # Populate the G matrix for all resistances connected to that center node.




def find_unit_center_node_index(layerIndex, chipletIndex, unitIndex, nodes):
    for i in range (len(nodes)):
        if nodes[i]["layerIndex"] == layerIndex and nodes[i]["chipletIndex"] == chipletIndex and nodes[i]["unitIndex"] == unitIndex:
            return i