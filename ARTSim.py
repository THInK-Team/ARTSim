# Author: Adam Corbier (@Ad2Am2)

import time
from src import globalVar
from src import nub_ctm as ctm
# Use name of model file instead of example_model
from models.example_model import model
from src.runSimulations import *

def prepareModel(model):

    model = ctm.flatten_model(model)
    print("Making nodes...")
    stepStart = time.time()
    globalVar.nodes = ctm.make_nodes(model)
    nodes = globalVar.nodes
    stepEnd = time.time()
    print("Step time: " + str(stepEnd-stepStart))
    print("Initializing matrices...")
    stepStart = time.time()
    globalVar.GMatrix = ctm.initialize_GC_matrix(nodes)   # Initilize the C matrix as a global variable so that any function can access it and modify it
    globalVar.CMatrix = ctm.initialize_GC_matrix(nodes)   # Initilize the C matrix as a global variable so that any function can access it and modify it
    globalVar.IVector = ctm.initialize_I_vector(nodes)
    stepEnd = time.time()
    print("Step time: " + str(stepEnd-stepStart))
    print("Making center resistances...")
    stepStart = time.time()
    ctm.populate_G_matrix(nodes, model)    
    ctm.populate_C_matrix(nodes, model)
    ctm.populate_I_vector(nodes, model)

    stepEnd = time.time()
    print("Model prepared! Step time: " + str(stepEnd-stepStart))

    globalVar.model = model

    globalVar.modelPrepared = True

# NOTE: make sure to call prepareModel before running the simulation

simStart = time.time()

# Mandatory run before any simulation
prepareModel(model)

# Runs steady state analysis on the model, result in given logs file

runSteadyState("logs/example_model_steadystate.log")

# Transient simulation

# Definition of the transient steps
# Each element of the array must match an element of the power dissipation array of blocks. If power dissipation is a single value, the same value will be used for all timesteps.
# Each phase of the transient simulation may be subdivided into steps for accuracy and/or analysis. Each step is an equal subdivision of the timestep duration.
# Example stepDefinition:
stepDefinition = [{"duration": 0.001, "steps": 2}, {"duration": 0.009, "steps": 2}, {"duration": 0.09, "steps": 2}, {"duration": 0.9, "steps": 2}, {"duration": 1, "steps": 2}]

runTransient(stepDefinition, "logs/example_model_transientResult.log")


simEnd = time.time()
print("Done! Simulation ran in " + str(simEnd-simStart) + " seconds")