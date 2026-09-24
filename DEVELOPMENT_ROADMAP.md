# EGH490 Virtual Power Plant Demonstrator — Development Roadmap

# Current Development Priorities

The project has progressed beyond development of the basic VPP simulation
engine and is now focused on defining, testing, and validating coordinated
VPP supervisory-control strategies.

The immediate development priorities are:

1. **Finalise VPP supervisory-control hierarchy**
   - Define participant-level energy-allocation priorities
   - Resolve the distinction between shared PV used for participant load
     support and shared PV used for battery charging
   - Define battery SOC reserve / energy-preservation strategy
   - Define event-priority and simultaneous-event behaviour
   - Continue validation of network-support dispatch
   - Compare alternative VPP coordination strategies

2. **Complete realistic operating scenarios**
   - Continue validation of the summer residential/PV dataset
   - Integrate and validate the prepared winter dataset
   - Replace the placeholder hospital profile with realistic demand
   - Develop a time-varying wind / DFIG generation profile
   - Establish repeatable comparison scenarios

3. **Develop the controller comparison framework**
   - Independent household self-consumption baseline
   - Coordinated VPP operation
   - PV-sharing strategy
   - Peak-shaving strategy
   - Network-support strategy
   - Later economic / tariff-based optimisation

4. **Continue physical demonstrator development**
   - Retain the existing Jetson GPIO demonstrator during software development
   - Integrate the ESP32-S3
   - Test addressable RGB indicators
   - Test MCP23017 battery SOC indicators
   - Add physical event controls

5. **Add network validation and later economic analysis**
   - Develop the initial `pandapower` network
   - Define technical performance KPIs
   - Develop tariff and economic models
   - Compare controller strategies using both technical and economic metrics

---

# Current Project Milestone

The project has progressed from a software-only VPP simulation to a
continuously operating embedded demonstrator with realistic residential
load and PV generation data and preliminary coordinated VPP control.

The current system can:

- Run a stateful five-house VPP simulation continuously on the
  NVIDIA Jetson Orin Nano
- Operate using a 30-minute simulation timestep
- Run multi-day residential load and PV profiles
- Continuously loop the available profile data
- Model different residential PV, battery, and connection configurations
- Model distributed residential batteries with persistent SOC
- Represent realistic battery module capacity and continuous power limits
- Represent separate PV and BESS inverter capacities
- Apply simplified premises connection/export constraints
- Calculate connection-constrained VPP battery capability
- Accept external network-support requests
- Allocate constrained network support across participating batteries
- Enable or disable experimental coordinated PV-sharing behaviour
- Calculate VPP grid import and export independently from external
  demonstration resources
- Calculate the wider demonstration/network power balance
- Record detailed simulation and house-level results
- Export accumulated results to Excel
- Translate simulated battery behaviour into physical hardware states
- Drive the current six-LED physical demonstrator in real time

The next major milestone is to transition from **preliminary coordinated
VPP control** to a **clearly defined and validated supervisory-control
hierarchy**.

The controller should ultimately support comparison between independent
household operation and coordinated VPP strategies without changing the
underlying physical DER models.

---

# Current Model Boundary and Design Decisions

The VPP consists of:

- Five participating residential premises
- Residential electrical loads
- Residential PV systems
- Residential battery energy storage systems
- The participating premises' grid connections

The hospital and wind / DFIG systems are **external demonstration
resources**.

They may interact with the VPP through supervisory-control scenarios,
but they are not themselves VPP assets.

The current simulation uses:

- 30-minute simulation timesteps
- Five distinct residential load profiles
- PV generation profiles derived from NREL SAM / PVWatts
- Persistent battery SOC
- Separate PV and BESS inverter representations
- Aggregate premises connection/export constraints rather than detailed
  phase-by-phase electrical modelling
- Continuous looping of multi-day profile data
- Explicit VPP and wider-network power balances
- External controller inputs for demonstration events and strategy toggles

The controller is intentionally separated from the physical DER models so
that alternative VPP coordination strategies can be evaluated without
changing the underlying household models.

Detailed model assumptions are maintained separately in `ASSUMPTIONS.md`.

Research questions, controller concepts, and unresolved design
investigations should be maintained separately in `RESEARCH_NOTES.md`.

---

# Development Principle

The project follows a modular design philosophy:

> **Simulation models determine the physical system state, the VPP
> controller determines coordinated behaviour, and the hardware
> communicates that behaviour to the user.**

The physical demonstrator should not contain independent control logic
that bypasses the VPP simulation.

Physical buttons provide inputs to the simulation/controller, while LEDs
and the future dashboard represent the resulting simulated state.

---

# 1. Project Objective

The objective of this project is to design and implement a small-scale
Virtual Power Plant demonstrator that coordinates distributed energy
resources across a simulated local network.

The VPP itself combines:

- Residential electrical loads
- Residential photovoltaic generation
- Residential battery energy storage systems
- Grid import and export
- VPP supervisory control
- External network and user inputs

The wider demonstrator additionally contains:

- A critical local load representing a hospital
- Wind generation / DFIG representation

These external resources provide scenarios through which the behaviour
and capabilities of the residential VPP can be demonstrated.

The VPP simulation is deployed on an NVIDIA Jetson Orin Nano, which acts
as the primary computing platform.

The final demonstrator will combine the software simulation with physical
controls, indicators, network validation, data visualisation, and
repeatable VPP operating scenarios.

---

# 2. System Architecture

The project is being developed using a layered architecture:

```text
Residential Load / PV Profiles
External Demonstration Profiles
                |
                v
        Simulation Models
 Houses / PV / Batteries /
 Hospital / Wind / Connections
                |
                v
          VPP Controller
 Operating Modes / Dispatch /
 Strategy Toggles / Events
                |
                v
        Simulation Results
                |
        +-------+-------+
        |               |
        v               v
 Hardware Interface   Dashboard
        |
        v
 Physical Demonstrator
 LEDs / Buttons / Indicators

The residential houses and their DERs form the VPP.

Hospital and wind / DFIG models exist outside the VPP boundary but are
included in the wider demonstration environment.

The software simulation remains independent from the physical hardware.

Hardware states are derived from simulation results through a hardware
abstraction layer rather than being embedded directly into the simulation
models.

---

# 3. Development Status

Status definitions:

- ✅ **Complete** — implemented and tested sufficiently for the current stage
- 🟡 **In Development** — functional but requires further development
- ⬜ **Planned** — required but not yet implemented
- 🔵 **Future / Extension** — optional extension after core objectives

---

# Phase 1 — Core Simulation Engine

**Status: ✅ Complete**

## Implemented

- [x] Object-oriented simulation structure
- [x] Five residential houses
- [x] Individual house load profiles
- [x] Individual PV generation profiles
- [x] Battery-equipped and non-battery houses
- [x] External hospital load representation
- [x] External wind-generation representation
- [x] Configurable simulation timestep
- [x] 30-minute simulation timestep selected for current datasets
- [x] Stateful continuous simulation using `VPPSimulation.step()`
- [x] Persistent battery state-of-charge between timesteps
- [x] Continuous execution beyond a single profile period
- [x] Profile wrapping using simulation profile index
- [x] Separate profile index and controller clock time
- [x] Simulation step, elapsed time, day and hour tracking
- [x] VPP grid import and export calculation
- [x] Separate wider-network power balance
- [x] Per-house results logging
- [x] VPP-level results logging
- [x] Excel results export

## Optional / Later Improvements

- [ ] Add formal simulation reset functionality if required
- [ ] Add controlled start / pause / single-step operation if useful
- [ ] Add scenario configuration system
- [ ] Add profile/scenario selection without editing the main script

Continuous profile looping is intentional for the physical demonstrator.
Battery SOC currently persists across profile boundaries rather than being
automatically reset.

---

# Phase 2 — Distributed Energy Resource Models

**Status: ✅ Core Model Complete / Validation Ongoing**

## Implemented

- [x] PV generation representation
- [x] Realistic PV generation profiles
- [x] Finalised residential PV system sizes for the current model
- [x] PV inverter-capacity metadata
- [x] Stateful battery energy model
- [x] Battery minimum and maximum SOC constraints
- [x] Maximum continuous battery charge power
- [x] Maximum continuous battery discharge power
- [x] Available battery discharge calculation
- [x] Available battery charging calculation
- [x] Battery charge/discharge energy tracking
- [x] Battery charging/discharging efficiency
- [x] Realistic residential BESS module parameters
- [x] Different battery module counts between houses
- [x] BESS inverter power cap
- [x] House without battery storage
- [x] House without PV generation
- [x] Separate PV and battery inverter concepts
- [x] Premises connection metadata
- [x] Single-phase and simplified three-phase connection representation
- [x] Aggregate premises export constraints
- [x] PV curtailment when export constraints are exceeded

## Current Residential DER Configuration

- **House 1**
  - 13.3 kWdc PV
  - 10.64 kW representative PV inverter capacity
  - 3 battery modules
  - Single-phase connection

- **House 2**
  - 6.6 kWdc PV
  - 5.28 kW representative PV inverter capacity
  - 2 battery modules
  - Single-phase connection

- **House 3**
  - 13.3 kWdc PV
  - 10.64 kW representative PV inverter capacity
  - No battery
  - Single-phase connection

- **House 4**
  - 20.0 kWdc PV
  - 16.0 kW representative aggregate PV inverter capacity
  - 3 battery modules
  - Simplified three-phase connection

- **House 5**
  - No PV
  - 5 battery modules
  - Single-phase connection

## Further Development

- [ ] Validate operation across additional profile scenarios
- [ ] Validate winter operation
- [ ] Consider weather-variable PV scenarios
- [ ] Review battery model detail if required by final analysis
- [ ] Add controller-level SOC reserve rather than changing physical capacity

---

# Phase 3 — VPP Supervisory Controller

**Status: 🟡 In Development — Current Major Software Priority**

## Implemented

- [x] Central `VPPController`
- [x] Self-consumption mode
- [x] Battery hold mode
- [x] Peak-shaving mode framework
- [x] Export-support mode framework
- [x] Local/network-load-support mode
- [x] Arbitrage / cheap-energy charging mode framework
- [x] External network-support requests
- [x] Calculation of total available VPP discharge power
- [x] Connection-constrained VPP discharge capability
- [x] Constrained battery dispatch
- [x] Dispatch respects individual battery power and energy limits
- [x] Requested support limited by actual VPP capability
- [x] Per-house battery support allocation
- [x] Equal-share redistribution when individual batteries reach constraints
- [x] Experimental PV-sharing strategy
- [x] PV-sharing enable / disable input
- [x] Calculation of surplus PV potentially available to the VPP
- [x] Calculation of available VPP battery charging capability
- [x] Preliminary allocation of shared PV between participants
- [x] Attribution of transferred shared PV to source houses
- [x] Interaction between VPP actions and premises export limits
- [x] Temporary network-support export-limit override
- [x] Separate normal dynamic and maximum export limits

## Current Priority

The controller is now sufficiently developed to expose higher-level
questions about how coordinated VPP operation should behave.

The current priority is therefore to **define and validate the VPP
operating hierarchy**, rather than continuing to add isolated controller
features.

## Next Tasks

- [ ] Finalise coordinated VPP operating hierarchy
- [ ] Separate shared PV used for participant load support from shared PV
      used for participant battery charging
- [ ] Define participant energy-allocation priorities
- [ ] Define SOC reserve / energy-preservation strategy
- [ ] Define dispatch fairness / allocation strategy
- [ ] Define event-priority rules
- [ ] Handle simultaneous VPP events
- [ ] Improve battery dispatch strategy
- [ ] Validate peak-shaving behaviour using realistic profiles
- [ ] Compare independent self-consumption against coordinated VPP operation
- [ ] Define repeatable controller comparison scenarios
- [ ] Integrate economic signals after technical controller validation

Detailed questions concerning the preferred hierarchy should be recorded
in `RESEARCH_NOTES.md` until they become formal design decisions.

---

# Phase 4 — External Inputs and VPP Events

**Status: 🟡 In Development**

## Implemented

- [x] `external_inputs` pathway into the simulation
- [x] External inputs passed independently from core simulation models
- [x] Network-support request input
- [x] Requested support power input
- [x] Manual operating-mode input pathway
- [x] Peak-shaving enable / disable input
- [x] PV-sharing enable / disable input
- [x] Scheduled test events
- [x] Daily repeating PV-sharing test window
- [x] External requests passed to the VPP controller
- [x] Controller response reflected in battery dispatch
- [x] Controller state reflected in simulation results

## Planned Event Inputs

- [ ] Hospital critical-load event
- [ ] DFIG / wind support request
- [ ] Free-energy / zero-price electricity event
- [ ] Physical manual operating-mode override
- [ ] Physical pushbutton inputs
- [ ] Dashboard / software-generated events

## Further Development

- [ ] Define priority between simultaneous events
- [ ] Define event start, duration and termination behaviour
- [ ] Decide which demonstration events repeat with profile cycles
- [ ] Distinguish manual commands from automatically detected conditions
- [ ] Record detailed event history in simulation results
- [ ] Replace hard-coded test schedules with configurable scenarios

---

# Phase 5 — NVIDIA Jetson Deployment

**Status: ✅ Complete**

## Implemented

- [x] NVIDIA Jetson Orin Nano configured as primary VPP computing platform
- [x] Project repository deployed to Jetson
- [x] Python virtual environment configured
- [x] Required Python packages installed
- [x] JupyterLab development environment configured
- [x] Remote development through SSH
- [x] SSH port forwarding for remote JupyterLab access
- [x] VPP simulation successfully executed on Jetson
- [x] GPIO library configured
- [x] Required GPIO pins configured
- [x] Physical GPIO outputs verified electrically and visually
- [x] Continuous realistic-profile simulation operating on Jetson

## Current Role of Jetson

The Jetson Orin Nano acts as the high-level computing platform responsible
for:

- VPP simulation
- Supervisory control
- Battery and DER models
- Profile processing
- Simulation logging
- Future power-system analysis
- Future economic analysis
- Future dashboard / user interface
- Communication with the physical demonstrator

Low-level physical I/O will progressively be delegated to a dedicated
microcontroller to separate high-level VPP computation from hardware
control.

---

# Phase 6 — Physical Hardware Demonstrator

**Status: 🟡 In Development**

## Proof-of-Concept Hardware — Complete

- [x] External 5 V breadboard power supply tested
- [x] Common-ground interface between Jetson and external circuitry
- [x] BC337 transistor switching circuit tested
- [x] GPIO-controlled LED successfully demonstrated
- [x] Five independent house status LEDs
- [x] Simulation timestep / tick LED
- [x] Six-LED physical demonstrator operational
- [x] `HardwareInterface` Python abstraction created
- [x] Simulation results translated into physical LED states
- [x] Charging represented by slow flashing
- [x] Discharging represented by fast flashing
- [x] Full battery represented by solid LED
- [x] Continuous simulation successfully drives physical LEDs in real time

## Final Demonstrator Architecture — In Development

```text
NVIDIA Jetson Orin Nano
        |
        | USB Serial
        v
ESP32-S3 Microcontroller
        |
        +---- Addressable RGB Status LEDs
        |
        +---- MCP23017 I/O Expander
        |           |
        |           +---- Battery SOC LEDs
        |
        +---- Physical Event Buttons
        |
        +---- Hospital Indicators
        |
        +---- Wind / DFIG Indicators
        |
        +---- Simulation Tick Indicator
```
## Planned Physical Indicators

### Residential Houses

- [ ] RGB status indicator for each of five houses
- [ ] Four-segment SOC indicator for House 1
- [ ] Four-segment SOC indicator for House 2
- [ ] House 3 represented without battery SOC indicator
- [ ] Four-segment SOC indicator for House 4
- [ ] Four-segment SOC indicator for House 5

Proposed RGB state representation:

- Green — charging
- Red — discharging
- Blue — idle / available
- Yellow — VPP support operation
- Additional colours may represent special operating states

### Grid / Substation

- [ ] RGB grid-status indicator
- [ ] Grid import state
- [ ] Grid export state
- [ ] Balanced / low-exchange state
- [ ] Free-energy / zero-price event indication

### Hospital

- [ ] Green normal-operation indicator
- [ ] Red critical-event indicator
- [ ] Physical critical-event pushbutton

### Wind / DFIG

- [ ] Green generating / operating indicator
- [ ] Yellow VPP-support indicator
- [ ] Physical support-request pushbutton

### Simulation

- [x] Proof-of-concept simulation tick LED
- [ ] Integrate tick indicator into final microcontroller hardware

## Hardware Selected / Ordered

- [x] ESP32-S3-Zero microcontroller
- [x] MCP23017 16-channel digital I/O expansion module
- [x] 74AHCT125 logic-level buffer / level shifter
- [x] Addressable 5 mm RGB LEDs
- [x] Header pins

## Next Hardware Tasks

- [ ] Develop Jetson-to-ESP32 communication protocol
- [ ] Program ESP32 hardware interface
- [ ] Test addressable RGB LED chain
- [ ] Test MCP23017 SOC outputs
- [ ] Connect physical event buttons
- [ ] Integrate ESP32 with `external_inputs`
- [ ] Design final demonstrator wiring
- [ ] Transfer prototype from breadboard to final mounting system

---

# Phase 7 — Realistic Datasets and Operating Scenarios

**Status: 🟡 In Development — Residential Summer Integration Complete**

## Residential Summer Dataset — Implemented

- [x] Import realistic residential load data
- [x] Clean and preprocess selected residential datasets
- [x] Convert residential data to 30-minute timestep
- [x] Create representative load profiles for all five houses
- [x] Preserve diversity between residential customers
- [x] Create seven-day residential simulation period
- [x] Integrate profiles into the continuous simulation
- [x] Validate equal profile lengths
- [x] Validate residential profile timestamps

## PV Generation — Implemented for Current Summer Scenario

- [x] Select PV system sizes for applicable houses
- [x] Generate PV profiles using NREL SAM / PVWatts
- [x] Define representative PV inverter capacities
- [x] Integrate PV generation profiles with house models
- [x] Align PV and load profiles by simulation timestep / time of day
- [x] Use common seven-day simulation length
- [x] Validate PV timestamps
- [x] Avoid duplicate inverter clipping within Python because imported
      profiles already represent SAM AC output

The current load and PV source datasets represent different source
periods and are treated as representative seasonal profiles rather than
an exact historical coincidence.

## Winter Dataset

- [x] Winter dataset prepared and available to the simulation project
- [x] Winter dataset imported by the current script
- [ ] Integrate winter profile selection into scenario execution
- [ ] Validate winter household behaviour
- [ ] Validate winter PV behaviour
- [ ] Compare summer and winter VPP performance

## Future PV / Weather Scenarios

- [ ] Retain representative clear/favourable generation scenario
- [ ] Develop cloudy / variable-weather scenario
- [ ] Develop lower-renewable-generation scenario
- [ ] Compare VPP behaviour under different renewable conditions

## Hospital / Critical Load

Current implementation uses a constant placeholder hospital load.

- [ ] Replace placeholder with realistic critical-load profile
- [ ] Define normal and critical operating conditions
- [ ] Define required VPP response during critical events
- [ ] Define whether hospital support represents network support,
      emergency support, or another explicit demonstration service

## Wind Generation

Current implementation uses a zero-generation placeholder profile.

- [ ] Replace placeholder with time-varying wind generation
- [ ] Develop simplified DFIG operating representation
- [ ] Define VPP-to-DFIG support scenario
- [ ] Align wind generation with the common simulation timeline

## Scenario Development

- [ ] Independent household self-consumption baseline
- [ ] Coordinated VPP operation
- [ ] PV-sharing enabled / disabled comparison
- [ ] High residential demand
- [ ] High PV generation
- [ ] Low renewable generation
- [ ] Peak grid-demand period
- [ ] Free-energy / zero-price period
- [x] External network-support request test
- [ ] Hospital critical-load event
- [ ] DFIG support request
- [ ] Multiple simultaneous events
- [ ] Summer versus winter comparison

---

# Phase 8 — Detailed Power-System Network Analysis

**Status: 🔵 Future / Optional Extension**

The core demonstrator models active-power and energy management at
participating premises' connection points.

Detailed distribution-network power-flow modelling is not required for
the minimum viable VPP demonstrator.

The current model instead represents simplified premises connection and
export constraints directly within the residential models.

A detailed network model could be added in future if investigation of
network-specific effects becomes relevant.

Possible future analysis could include:

- [ ] Distribution-network topology
- [ ] Bus-voltage analysis
- [ ] Line and transformer loading
- [ ] Network losses
- [ ] Reactive-power representation
- [ ] Power-factor modelling
- [ ] Phase imbalance
- [ ] Voltage-constrained VPP dispatch
- [ ] Network-constrained export limits

---

# Phase 9 — Data Logging, KPIs and Visualisation

**Status: 🟡 Partially Implemented**

## Implemented

- [x] Simulation-step logging
- [x] Profile-index logging
- [x] Elapsed simulation time
- [x] Day and hour-of-day logging
- [x] Per-timestep VPP results
- [x] Per-house results history
- [x] Household demand logging
- [x] Household PV generation logging
- [x] PV available versus actual generation
- [x] PV curtailment logging
- [x] Battery SOC logging
- [x] Battery charge/discharge logging
- [x] Battery configuration metadata
- [x] PV configuration metadata
- [x] Connection configuration metadata
- [x] Connection export-limit logging
- [x] VPP grid import/export logging
- [x] Wider-network import/export logging
- [x] Operating-mode logging
- [x] PV-sharing enable-state logging
- [x] Shared-PV availability logging
- [x] Shared-PV transfer logging
- [x] Per-house shared-PV targets
- [x] Requested network-support logging
- [x] Available VPP-support logging
- [x] Excel results export
- [x] Basic plotting / debugging within the development notebook

## Planned Technical KPIs

- [ ] Total VPP grid-import energy
- [ ] Total VPP grid-export energy
- [ ] Per-participant grid-import energy
- [ ] Per-participant grid-export energy
- [ ] Total PV generation
- [ ] Total PV curtailment
- [ ] Battery charge/discharge energy
- [ ] Peak grid import
- [ ] Peak-demand reduction
- [ ] PV self-consumption
- [ ] VPP renewable-energy utilisation
- [ ] Shared-PV utilisation
- [ ] VPP support requested versus delivered
- [ ] Critical-load support delivered
- [ ] Battery utilisation statistics
- [ ] Battery SOC availability during external events

## Controller Comparison KPIs

- [ ] Compare independent and coordinated operation
- [ ] Compare PV sharing enabled versus disabled
- [ ] Compare grid import reduction
- [ ] Compare PV curtailment reduction
- [ ] Compare battery utilisation
- [ ] Compare retained battery capability for later VPP events

## Real-Time Dashboard

- [ ] Display current simulation time
- [ ] Display current VPP operating mode
- [ ] Display active controller strategies
- [ ] Display individual house demand and generation
- [ ] Display individual battery SOC
- [ ] Display battery charge/discharge power
- [ ] Display VPP grid import/export power
- [ ] Display wider-network state
- [ ] Display hospital state
- [ ] Display wind-generation state
- [ ] Display active external events
- [ ] Display historical graphs
- [ ] Provide simulation controls

The physical LEDs are intended to communicate system state at a glance,
while the dashboard will communicate numerical values and detailed
operating information.

---

# Phase 10 — Economic / Tariff Layer

**Status: ⬜ Planned**

The economic layer will be developed after the core technical controller
and comparison scenarios are sufficiently stable.

Its purpose is not only to calculate electricity costs, but also to
evaluate the economic consequences of alternative VPP coordination
strategies.

## Planned Development

- [ ] Define electricity import tariff
- [ ] Define electricity export tariff / feed-in tariff
- [ ] Represent time-varying electricity prices
- [ ] Represent zero-price / free-energy periods
- [ ] Calculate participant energy-import costs
- [ ] Calculate participant export revenue
- [ ] Calculate aggregate VPP energy cost / value
- [ ] Compare independent and VPP-coordinated operation
- [ ] Quantify savings from battery operation
- [ ] Evaluate economic benefit of peak shaving
- [ ] Evaluate economic benefit of energy arbitrage
- [ ] Evaluate the value of coordinated PV utilisation
- [ ] Evaluate the value contributed by storage-only participants
- [ ] Consider battery efficiency losses in economic dispatch
- [ ] Consider future network-service / VPP-service value

## Future Controller Investigation

The economic model may later be used to determine whether surplus
generation is more valuable when:

- exported immediately,
- used to offset another participant's grid import,
- used to charge another participant's battery,
- or preserved indirectly by avoiding battery discharge for later use.

These alternatives should be evaluated rather than assumed to have a
predetermined preferred outcome.

Detailed hypotheses and research questions should be maintained in
`RESEARCH_NOTES.md`.

---

# Phase 11 — Final Integration and Demonstration

**Status: ⬜ Planned**

This phase will integrate the completed software, controller, network
model, hardware, and user interface into the final VPP demonstrator.

## Final Integration

- [ ] Integrate summer and winter scenario selection
- [ ] Integrate realistic hospital profile
- [ ] Integrate realistic wind / DFIG profile
- [ ] Integrate final VPP supervisory controller
- [ ] Integrate controller comparison framework
- [ ] Integrate `pandapower` network model
- [ ] Integrate ESP32 physical I/O
- [ ] Integrate final physical demonstrator
- [ ] Integrate dashboard
- [ ] Integrate event pushbuttons
- [ ] Validate continuous operation
- [ ] Test recovery from software / communication interruption

## Demonstration Scenarios

- [ ] Independent residential self-consumption
- [ ] Coordinated VPP operation
- [ ] PV charging of distributed batteries
- [ ] Coordinated surplus-PV utilisation
- [ ] Peak-shaving response
- [ ] External network-support request
- [ ] Free-energy battery charging
- [ ] Hospital critical-load support
- [ ] DFIG support event
- [ ] VPP resource-limitation scenario
- [ ] Simultaneous-event priority demonstration
- [ ] Summer / winter operating comparison

## Validation

- [ ] Verify household power balance
- [ ] Verify VPP-level power balance
- [ ] Verify shared-energy accounting
- [ ] Verify battery energy conservation
- [ ] Verify battery operating constraints
- [ ] Verify connection/export constraints
- [ ] Verify PV curtailment behaviour
- [ ] Verify controller dispatch constraints
- [ ] Verify event-priority behaviour
- [ ] Verify hardware indicators against simulation state
- [ ] Verify dashboard against simulation results
- [ ] Perform repeatable scenario tests
- [ ] Document final test results

---

# Phase 12 — Future Extensions

**Status: 🔵 Future / Extension**

These features are outside the immediate core demonstrator and should
only be pursued after the primary project objectives are complete.

- [ ] Electric vehicle / EV charging model
- [ ] Vehicle-to-grid operation
- [ ] More detailed DFIG model
- [ ] Physical wind-turbine motor demonstration
- [ ] Reactive-power VPP control
- [ ] Larger VPP population
- [ ] Forecast-based control
- [ ] Optimisation-based dispatch
- [ ] Machine-learning forecasting or control
- [ ] Detailed phase-by-phase network representation
- [ ] Additional DER technologies
- [ ] More advanced participant benefit / settlement mechanisms

---

# Current Development Sequence

The recommended development sequence from the current project state is:

1. **Freeze and validate the current residential physical model**
   - Summer load profiles
   - PV profiles
   - Battery configurations
   - Connection constraints
   - Continuous 30-minute simulation

2. **Finalise the VPP supervisory-control hierarchy**
   - Independent self-consumption baseline
   - Coordinated PV / load / battery behaviour
   - Peak shaving
   - Network support
   - SOC reserve
   - Event priority

3. **Develop repeatable controller comparison scenarios**
   - Ensure alternative strategies operate on identical input datasets
   - Define technical KPIs
   - Validate energy and power accounting

4. **Complete external demonstration models**
   - Hospital profile and event
   - Wind / DFIG profile and event

5. **Integrate and validate winter operation**

6. **Continue final physical demonstrator development**
   - ESP32-S3
   - RGB indicators
   - SOC indicators
   - Physical event controls

7. **Develop power-system network validation**
   - `pandapower`
   - Voltage and loading checks
   - Network-constrained operating analysis

8. **Develop economic / tariff analysis**
   - Participant costs
   - Feed-in revenue
   - Coordinated VPP value
   - Alternative dispatch-strategy comparison

9. **Develop final dashboard and KPI presentation**

10. **Complete final system integration and repeatable demonstration testing**

---

# Project Documentation Structure

The project should maintain three separate forms of design documentation:

## `DEVELOPMENT_ROADMAP.md`

Records:

- Current development state
- Completed implementation
- Current priorities
- Future implementation tasks
- Development sequence

## `ASSUMPTIONS.md`

Records:

- Simulation assumptions
- Simplified physical representations
- Connection assumptions
- DER modelling assumptions
- Demonstrator-specific control assumptions

## `RESEARCH_NOTES.md`

Records:

- Unresolved research questions
- Potential controller strategies
- Economic hypotheses
- Alternative dispatch hierarchies
- Participant fairness considerations
- Ideas requiring later investigation
- Findings that may influence the final controller or thesis discussion

This separation allows an idea to be investigated without prematurely
turning it into either a model assumption or an implementation
requirement.