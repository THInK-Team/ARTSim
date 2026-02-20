# ARTSim

Welcome to **ARTSim**, A Robust Thermal Simulator! 

For a description on the "why?" and "how?" of ARTSim, check out our publications below:

<details>
<summary><b>ARTSim: A Robust Thermal Simulator for Heterogeneous Integration Platform [ECTC 2023]</b></summary>
<p>

```
@INPROCEEDINGS{10195756,
  author={Safari, Yousef and Corbier, Adam and Saleh, Dima Al and Vaisband, Boris},
  booktitle={2023 IEEE 73rd Electronic Components and Technology Conference (ECTC)}, 
  title={ARTSim: A Robust Thermal Simulator for Heterogeneous Integration Platforms}, 
  year={2023},
  volume={},
  number={},
  pages={1187-1193},
  keywords={Runtime;Simulation;Multichip modules;Electronic components;Thermal management;Electronic packaging thermal management;Steady-state;Thermal simulator;thermal management;computer-aided design;compact simulator;chiplet integration;heterogeneous integration;advanced packaging},
  doi={10.1109/ECTC51909.2023.00203}}

```
Link: [IEEE ECTC 2023 [IEEE Xplore]](https://ieeexplore.ieee.org/document/10195756)

</p>
</details>

<details>
<summary><b>Thermal Simulator for Advanced Packaging and Chiplet-Based Systems [TVLSI 2025]</b></summary>
<p>

```
@ARTICLE{10922775,
  author={Safari, Yousef and Corbier, Adam and Saleh, Dima Al and Amik, Fahad Rahman and Vaisband, Boris},
  journal={IEEE Transactions on Very Large Scale Integration (VLSI) Systems}, 
  title={Thermal Simulator for Advanced Packaging and Chiplet-Based Systems}, 
  year={2025},
  volume={33},
  number={6},
  pages={1638-1650},
  keywords={Thermal resistance;Computational modeling;Solid modeling;Three-dimensional displays;Accuracy;Electronic packaging thermal management;Finite element analysis;Multichip modules;Design automation;Costs;Advanced packaging;chiplet integration;compact simulator;computer-aided design (CAD);heterogeneous integration;thermal management;thermal simulator},
  doi={10.1109/TVLSI.2025.3545604}}

```
Link: [IEEE TVLSI 2025 [IEEE Xplore]](https://ieeexplore.ieee.org/document/10922775)

</p>
</details>

For questions on technical details of ARTSim, feel free to reach out to adam.corbier@mail.mcgill.ca.


## How ARTSim works?

ARTSim simulates models according to the following structure:
- The model is composed of one to many layers (*e.g.* an active layer, a heat sink, etc.), stacked on each other by the Z-axis.
- Each layer is composed of one to many chiplets, that are thermally isolated on the sides. This facilitates the use of the tool for heterogeneous integration. If your layer does not contain chiplets, then define the whole layer as a single chiplet.
- Each chiplet is composed of functional blocks defined by the user.

Functional blocks have the following properties:
- Starting coordinates (`leftX`, `bottomY`): the functional block's coordinates at the bottom-left corner. The system uses (0,0) as  the origin; going right increases X, going up increases Y. All distance measurements are in meters.
- Width (X-axis) and Height (Y-axis). Be sure to use meters for this (not microns!)
- Thickness (Z-axis). Usually will be the same throughout a layer.
- Power dissipation (W). Note this is not power density (Wm-3)!
- Material properties (Volumetric Heat Capacity and Conductivity). Default values for certain materials can be used from `materials.py`, or the user can input their own values.
- Resolution: In order to tailor simulation accuracy, the resolution for each block can be defined by the user. At runtime, this will subdivide the block into smaller blocks. The format for this is an array [X,Y], where X is the resolution on the X-axis, and Y is the resolution on the Y-axis. Therefore, the total number of `subblocks` at runtime will be X*Y. Note that large resolutions for many blocks at a time can quickly increase the simulation time. 

## How to use ARTSim

### Setup and installation

Please read the comments in `setup.sh` and make sure everything is compatible with you system before installation. Some commands may need modification, based on your system being `bash` or `csh`. 

Simply run the `setup.sh` from your terminal, and it will automatically install all required prerequisites:
 
```shell
git clone https://github.com/THInK-Team/ARTSim.git
cd setup
chmod +x setup.sh
./setup.sh
```

### Running ARTSim

- Create a Python model file the in `ARTSim/models` directory. 

- You can check and use the `example_model.py` as a template to define your own model.  

> [!NOTE]
> In the created model files, a `model` variable in the correct format must be defined, which will be passed to the simulator.

You can run steady state simulation or transient simulation by using their flag in the `make run` command, where you also define your model name:

```shell
# Template: transient and steady state
make run model=<model_name>  steady_state  transient
# Model A: only transient
make run model=A  transient
# Model B: only steady state
make run model=B  steady_state
```

The command below executes the `example_model` provided in the `ARTSim/models/` directory:

```shell
make run model=example_model  steady_state  transient
```

> [!NOTE]
> The `prepareModel()` function must always run before any simulation, in `ARTSim.py`.

> [!WARNING]
> If running a transient simulation, ensure to define the `stepDefinition` in `ARTSim.py`. 

All of the results are reported in degrees Kelvin, with the defualt baseline temperature assumed to be 318.15 (45 Celsius). You can change the baseline temperature using the `base_temp` option:

```shell
make run model=<model_name> transient base_temp=300.0 # 318.5 when not set manually
```

- The output files (exported in `logs/<model_name>_steadystate.log` or `logs/<model_name>_transientResult.log`) specify the temperature at the center of each block's subdivision (according to the given resolution), using the order provided by the `model` input. 

- Example: 

```
Input: [block1 (resolution=[2,2]), block2 (resolution=[1,1])]
Output: [b1temp1, b1temp2, b1temp3, b1temp4, b2temp]
```