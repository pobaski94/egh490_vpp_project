# EGH490 Virtual Power Plant Demonstrator — Development Roadmap


# Current Development Priorities

The immediate development priorities are:

1. **Improve VPP supervisory control**
   - Implement automatic peak shaving
   - Implement free-energy charging
   - Implement hospital critical-load support
   - Implement DFIG support
   - Establish event-priority rules

2. **Develop realistic simulation inputs**
   - Clean residential load data
   - Develop realistic PV profiles
   - Improve hospital and wind profiles
   - Establish multi-day test scenarios

3. **Develop final physical I/O system**
   - Retain the current six-LED Jetson GPIO demonstrator during software development
   - Integrate the ESP32-S3 when hardware arrives
   - Test addressable RGB indicators
   - Test MCP23017 battery SOC indicators
   - Add physical event buttons

4. **Add power-system validation**
   - Develop the initial `pandapower` network
   - Connect simulation results to power-flow analysis

5. **Develop monitoring and visualisation**
   - Define final project KPIs
   - Develop the real-time dashboard
   - Separate numerical information from physical status indication

---

# Current Project Milestone

The project has progressed from a software-only VPP simulation to a continuously operating embedded demonstrator.

The current system can:

- Run a stateful multi-house VPP simulation continuously on the NVIDIA Jetson Orin Nano
- Model distributed residential batteries with persistent SOC
- Accept external network-support requests
- Determine the VPP's available battery-discharge capability
- Allocate constrained support across participating batteries
- Calculate grid import and export
- Record detailed simulation and house-level results
- Translate simulated battery behaviour into physical hardware states
- Drive a six-LED physical demonstrator in real time

The next major milestone is to transition from **functional VPP dispatch** to **automatic supervisory VPP control**, while replacing simplified profiles with realistic operating data.

---

# Development Principle

The project follows a modular design philosophy:

> **Simulation models determine the physical system state, the VPP controller determines coordinated behaviour, and the hardware communicates that behaviour to the user.**

The physical demonstrator should not contain independent control logic that bypasses the VPP simulation. Physical buttons provide inputs to the simulation/controller, while LEDs and the future dashboard represent the resulting simulated state.





## 1. Project Objective

The objective of this project is to design and implement a small-scale Virtual Power Plant (VPP) demonstrator that coordinates distributed energy resources across a simulated local network.

The system combines:

- Residential electrical loads
- Residential photovoltaic (PV) generation
- Battery energy storage systems (BESS)
- A critical local load representing a hospital
- Wind generation / DFIG representation
- Grid import and export
- VPP supervisory control
- External network and user events
- Physical hardware inputs and status indicators

The VPP simulation is deployed on an NVIDIA Jetson Orin Nano, which acts as the primary computing platform. The final demonstrator will combine the software simulation with physical controls, indicators, and a real-time user interface.

---

## 2. System Architecture

The project is being developed using a layered architecture:

```text
Realistic Load / Generation Profiles
                |
                v
        Simulation Models
   Houses / PV / Batteries /
     Hospital / Wind / Grid
                |
                v
          VPP Controller
   Operating Modes / Dispatch /
       External Events
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
```

The software simulation remains independent from the physical hardware. Hardware states are derived from simulation results through a hardware abstraction layer rather than being embedded directly into the simulation models.

---

## 3. Development Status

Status definitions:

- ✅ **Complete** — implemented and tested
- 🟡 **In Development** — functional but requires further development
- ⬜ **Planned** — required but not yet implemented
- 🔵 **Future / Extension** — optional extension after core project objectives

---

## Phase 1 — Core Simulation Engine

**Status: ✅ Complete**

### Implemented

- [x] Object-oriented simulation structure
- [x] Five residential houses
- [x] Individual house load profiles
- [x] Individual PV generation profiles
- [x] Battery-equipped and non-battery houses
- [x] Local hospital load
- [x] Wind generation placeholder
- [x] Configurable simulation timestep
- [x] Stateful continuous simulation using `VPPSimulation.step()`
- [x] Persistent battery state-of-charge between timesteps
- [x] Continuous execution beyond a single profile period
- [x] Profile wrapping using simulation profile index
- [x] Simulation step, elapsed time, day and hour tracking
- [x] Grid import and export calculation
- [x] Per-house results logging
- [x] VPP-level results logging
- [x] Excel results export

### Further Development

- [ ] Add formal simulation reset functionality
- [ ] Add controlled start / pause / single-step operation
- [ ] Finalise simulation timestep for realistic datasets

---

## Phase 2 — Distributed Energy Resource Models

**Status: 🟡 In Development**

### Implemented

- [x] PV generation model
- [x] Stateful battery energy model
- [x] Battery minimum and maximum SOC constraints
- [x] Maximum battery charge power
- [x] Maximum battery discharge power
- [x] Available discharge calculation
- [x] Battery charge/discharge energy tracking
- [x] Houses with different battery configurations
- [x] House without battery storage
- [x] House without PV generation

### Further Development

- [ ] Replace synthetic profiles with realistic multi-day data
- [ ] Improve wind generation representation
- [ ] Improve hospital / critical-load profile
- [ ] Validate battery parameters against realistic residential BESS
- [ ] Match PV system sizes and generation profiles to realistic installations

---

## Phase 3 — VPP Supervisory Controller

**Status: 🟡 In Development**

### Implemented

- [x] Central `VPPController`
- [x] Self-consumption mode
- [x] Battery hold mode
- [x] Peak-shaving mode framework
- [x] Export-support mode
- [x] Local-load-support mode
- [x] Arbitrage / cheap-energy charging mode framework
- [x] External network support requests
- [x] Calculation of total available VPP discharge power
- [x] Constrained battery dispatch
- [x] Dispatch respects individual battery power and energy limits
- [x] Requested support limited by actual VPP capability
- [x] Per-house battery support allocation

### Current Priority

Develop automatic supervisory decision-making so that VPP operating modes are selected from system conditions rather than primarily from predetermined test events.

### Next Tasks

- [ ] Automatic peak-shaving trigger
- [ ] Free-energy / zero-price charging event
- [ ] Hospital critical-load support event
- [ ] DFIG / wind support request
- [ ] Define event priority and arbitration rules
- [ ] Handle simultaneous VPP events
- [ ] Improve battery dispatch strategy
- [ ] Define SOC reserve strategy


---

## Phase 4 — External Inputs and VPP Events

**Status: 🟡 In Development**

### Implemented

- [x] `external_inputs` pathway into the simulation
- [x] External inputs passed independently from core simulation models
- [x] Network support request input
- [x] Requested support power input
- [x] Manual operating mode input
- [x] External requests passed to the VPP controller
- [x] Controller response reflected in battery dispatch and simulation results

### Planned Event Inputs

- [ ] Hospital critical-load event
- [ ] DFIG / wind support request
- [ ] Free-energy / zero-price electricity event
- [ ] Manual VPP operating-mode override
- [ ] Physical pushbutton inputs
- [ ] Dashboard / software-generated events

### Further Development

- [ ] Define priority between simultaneous events
- [ ] Define event start, duration and termination behaviour
- [ ] Distinguish manual commands from automatically detected conditions
- [ ] Record event history in simulation results

---

## Phase 5 — NVIDIA Jetson Deployment

**Status: ✅ Complete**

### Implemented

- [x] NVIDIA Jetson Orin Nano configured as primary VPP computing platform
- [x] Project repository deployed to Jetson
- [x] Python virtual environment configured
- [x] Required Python packages installed
- [x] JupyterLab development environment configured
- [x] Remote development through SSH
- [x] SSH port forwarding for remote JupyterLab access
- [x] VPP simulation successfully executed on Jetson
- [x] GPIO library configured
- [x] Jetson GPIO permissions configured
- [x] Required GPIO pins configured using Jetson-IO
- [x] Physical GPIO outputs verified electrically and visually

### Current Role of Jetson

The Jetson Orin Nano acts as the high-level computing platform responsible for:

- VPP simulation
- Supervisory control
- Battery and DER models
- Simulation logging
- Future power-system analysis
- Future dashboard / user interface
- Communication with the physical demonstrator

Low-level physical I/O will progressively be delegated to a dedicated microcontroller to separate high-level VPP computation from hardware control.

---

## Phase 6 — Physical Hardware Demonstrator

**Status: 🟡 In Development**

### Proof-of-Concept Hardware — Complete

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

### Final Demonstrator Architecture — In Development

The final hardware architecture separates the Jetson's high-level computation from low-level physical I/O.

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

### Planned Physical Indicators

#### Residential Houses

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

#### Grid / Substation

- [ ] RGB grid-status indicator
- [ ] Grid import state
- [ ] Grid export state
- [ ] Balanced / low-exchange state
- [ ] Free-energy / zero-price event indication

#### Hospital

- [ ] Green normal-operation indicator
- [ ] Red critical-event indicator
- [ ] Physical critical-event pushbutton

#### Wind / DFIG

- [ ] Green generating / operating indicator
- [ ] Yellow VPP-support indicator
- [ ] Physical support-request pushbutton

#### Simulation

- [x] Proof-of-concept simulation tick LED
- [ ] Integrate tick indicator into final microcontroller hardware

### Hardware Selected / Ordered

- [x] ESP32-S3-Zero microcontroller
- [x] MCP23017 16-channel digital I/O expansion module
- [x] 74AHCT125 logic-level buffer / level shifter
- [x] Addressable 5 mm RGB LEDs
- [x] Header pins

### Next Hardware Tasks

- [ ] Develop Jetson-to-ESP32 communication protocol
- [ ] Program ESP32 hardware interface
- [ ] Test addressable RGB LED chain
- [ ] Test MCP23017 SOC outputs
- [ ] Connect physical event buttons
- [ ] Integrate ESP32 with `external_inputs`
- [ ] Design final demonstrator wiring
- [ ] Transfer prototype from breadboard to final mounting system


---

## Phase 7 — Realistic Datasets and Operating Scenarios

**Status: 🟡 In Development**

### Implemented 

- [x] Initial residential load profiles
- [x] Initial PV generation profiles
- [x] Common simulation timeline
- [x] Initial hospital load profile
- [x] Placeholder wind-generation model


The current simulation architecture has been validated using simplified load and generation profiles. The next stage is to replace these profiles with realistic datasets while retaining the existing simulation and controller architecture.

### Residential Load Data

- [ ] Import realistic residential load data
- [ ] Clean and preprocess selected datasets
- [ ] Convert source data to the final simulation timestep
- [ ] Create representative load profiles for each house
- [ ] Preserve diversity between residential customers
- [ ] Develop realistic multi-day simulation periods

### PV Generation

- [ ] Select realistic PV system sizes for each applicable house
- [ ] Generate or obtain matching PV generation profiles
- [ ] Align PV data with residential load timestamps
- [ ] Develop multiple solar-generation scenarios
- [ ] Consider clear, cloudy and variable-weather conditions

### Hospital / Critical Load

- [ ] Replace placeholder hospital load with a more realistic critical-load profile
- [ ] Define normal and critical operating conditions
- [ ] Define required VPP response during critical events

### Wind Generation

- [ ] Replace placeholder wind generation with time-varying generation
- [ ] Develop a simplified DFIG operating representation
- [ ] Define VPP-to-DFIG support scenario
- [ ] Align wind generation with the common simulation timeline

### Scenario Development

Planned simulation scenarios include:

- [ ] Normal VPP operation
- [ ] High residential demand
- [ ] High PV generation
- [ ] Low renewable generation
- [ ] Peak grid-demand period
- [ ] Free-energy / zero-price period
- [ ] External network-support request
- [ ] Hospital critical-load event
- [ ] DFIG support request
- [ ] Multiple simultaneous events

---

## Phase 8 — Power-System Network Validation

**Status: ⬜ Planned**

The current VPP model operates primarily as an active-power and energy-management simulation. A network model will be added using `pandapower` to evaluate whether VPP control actions are also acceptable from a power-system perspective.

### Planned Development

- [ ] Develop simplified local distribution-network topology
- [ ] Represent residential houses as network loads / generators
- [ ] Represent hospital critical load
- [ ] Represent wind generation
- [ ] Represent grid connection / external network
- [ ] Map VPP simulation results into the network model
- [ ] Perform power-flow calculations
- [ ] Monitor bus voltages
- [ ] Monitor line / transformer loading
- [ ] Evaluate grid import and export conditions
- [ ] Compare operation with and without VPP control

### Possible Extensions

- [ ] Reactive-power representation
- [ ] Power-factor modelling
- [ ] Voltage-support strategies
- [ ] Network-constrained VPP dispatch

The objective of this phase is to distinguish between an energy-management decision that is mathematically possible and one that is also suitable for the electrical network.

---

## Phase 9 — Data Logging, KPIs and Visualisation

**Status: 🟡 Partially Implemented**

### Implemented

- [x] Per-timestep VPP results
- [x] Per-house results history
- [x] Battery SOC logging
- [x] Battery charge/discharge logging
- [x] Grid import/export logging
- [x] Operating-mode logging
- [x] Requested network-support logging
- [x] Available VPP-support logging
- [x] Excel results export
- [x] Basic plotting within the development notebook

### Planned KPIs

- [ ] Total grid-import energy
- [ ] Total grid-export energy
- [ ] Total PV generation
- [ ] Total renewable generation
- [ ] Battery charge/discharge energy
- [ ] Peak grid import
- [ ] Peak-demand reduction
- [ ] Renewable self-consumption
- [ ] Renewable-energy utilisation
- [ ] VPP support requested versus delivered
- [ ] Critical-load support delivered
- [ ] Battery utilisation statistics

### Real-Time Dashboard

- [ ] Display current simulation time
- [ ] Display current VPP operating mode
- [ ] Display individual house demand and generation
- [ ] Display individual battery SOC
- [ ] Display battery charge/discharge power
- [ ] Display grid import/export power
- [ ] Display hospital state
- [ ] Display wind-generation state
- [ ] Display active external events
- [ ] Display historical graphs
- [ ] Provide simulation controls

The physical LEDs are intended to communicate system state at a glance, while the dashboard will communicate numerical values and detailed operating information.

---

## Phase 10 — Economic / Tariff Layer

**Status: ⬜ Planned**

An economic layer may be added after the core technical VPP controller is operational.

### Planned Development

- [ ] Define electricity import tariff
- [ ] Define electricity export tariff / feed-in tariff
- [ ] Represent time-varying electricity prices
- [ ] Represent zero-price / free-energy periods
- [ ] Calculate energy-import cost
- [ ] Calculate export revenue
- [ ] Compare uncontrolled and VPP-controlled operation
- [ ] Quantify savings from battery operation
- [ ] Evaluate economic benefit of peak shaving
- [ ] Evaluate economic benefit of energy arbitrage

### Possible Extension

Use both technical and economic conditions when selecting VPP operating modes.

---

## Phase 11 — Final Integration and Demonstration

**Status: ⬜ Planned**

This phase will integrate the completed software, controller, network model, hardware and user interface into the final VPP demonstrator.

### Final Integration

- [ ] Integrate realistic datasets
- [ ] Integrate final VPP supervisory controller
- [ ] Integrate pandapower network model
- [ ] Integrate ESP32 physical I/O
- [ ] Integrate final physical demonstrator
- [ ] Integrate dashboard
- [ ] Integrate event pushbuttons
- [ ] Validate continuous operation
- [ ] Test recovery from software / communication interruption

### Demonstration Scenarios

- [ ] Normal residential operation
- [ ] PV charging of distributed batteries
- [ ] Peak-shaving response
- [ ] External network-support request
- [ ] Free-energy battery charging
- [ ] Hospital critical-load support
- [ ] DFIG support event
- [ ] VPP resource-limitation scenario
- [ ] Simultaneous-event priority demonstration

### Validation

- [ ] Verify battery energy conservation
- [ ] Verify battery operating constraints
- [ ] Verify controller dispatch constraints
- [ ] Verify event-priority behaviour
- [ ] Verify hardware indicators against simulation state
- [ ] Verify dashboard against simulation results
- [ ] Perform repeatable scenario tests
- [ ] Document final test results

---

## Phase 12 — Future Extensions

**Status: 🔵 Future / Extension**

These features are outside the immediate core demonstrator and should only be pursued after the primary project objectives are complete.

- [ ] Electric vehicle / EV charging model
- [ ] Vehicle-to-grid operation
- [ ] More detailed DFIG model
- [ ] Physical wind-turbine motor demonstration
- [ ] Reactive-power VPP control
- [ ] Larger VPP population
- [ ] Forecast-based control
- [ ] Optimisation-based dispatch
- [ ] Machine-learning forecasting or control
- [ ] Additional DER technologies

---
