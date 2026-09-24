# VPP Demonstrator - Modelling Assumptions

This document records the assumptions and simplifications used in the
VPP demonstrator. Assumptions represent the implemented simulation model
and should not be interpreted as network, regulatory, or manufacturer
requirements unless an external source is explicitly identified.

Where an assumption is introduced specifically to investigate a research
scenario, it is identified as such.


### A01 - VPP Conceptual Boundary
**Type:** Model assumption

The VPP model consists only of the five participating houses and their associated DERs. The hospital and wind/DFIG systems are external demonstration elements used to enhance conceptual understanding and demonstrate external VPP services. They are not considered part of the VPP boundary.


### A02 - Grid Connections
**Type:** Model simplification

Residential connections are represented using aggregate kW power flows rather than explicit per-phase power flows to simplify the model.
Single-phase and three-phase connection types are retained as model attributes so that different aggregate connection and dynamic export limits can be represented.


### A03 - Export and Inverter Capacities
**Type:** Model assumption

For single-phase sites, PV and BESS inverter capacities may each be modelled up to 10 kW, allowing up to 20 kW of cumulative installed inverter capacity.
Installed inverter capacity does not represent the allowable connection-point export. Actual export is separately constrained by the site's applicable dynamic export limit and modelled maximum connection export capability.
For the three-phase site, a maximum aggregate connection export capability of 30 kW is modelled, based on a simplified 10 kW-per-phase representation.
Explicit per-phase power balance is outside the scope of the current model.


### A04 - Dynamic Export Limits
**Type:** Model assumption

Dynamic export limits may vary between 1.5 kW per phase and 10 kW per phase under the general model.
Lower limits may be deliberately applied during simulation testing to validate connection-limit, curtailment, and VPP control behaviour.


### A05 - Inverter and Connection Ratings
**Type:** Model architecture

PV inverter rating, BESS inverter rating, and premises connection/export limits are treated as independent constraints.
The capability of a DER therefore does not imply that its full available power can always be imported or exported through the premises connection.


### A06 - Battery Usable Capacity
**Type:** Battery model assumption

SigenStor usable battery capacity is modelled across 0-100% simulation SOC based on the manufacturer's specified usable energy and 100% depth-of-discharge capability.
Any minimum SOC reserve imposed by the VPP is treated as a supervisory control strategy rather than a reduction in the modelled physical usable capacity.


### A07 - BESS Power Capability
**Type:** Battery model assumption

Battery module continuous power capability is assumed to scale with installed module count, subject to the separately modelled BESS inverter/safety power limit.
Normal BESS power is therefore limited by both the available battery-module capability and the applicable inverter limit.


### A08 - Surplus PV Sharing
**Type:** VPP operational assumption

Surplus PV produced by participating VPP households is assumed to be available for coordinated sharing with other participating households that have available load or battery storage capacity.
This represents coordinated energy exchange through the distribution network rather than a dedicated physical electrical connection between household DERs.


### A09 - VPP Shared-PV Dynamic Export Exception
**Type:** VPP assumption / optimisation research scenario

VPP-directed surplus PV sharing may exceed a site's instantaneous dynamic export limit when the additional energy can be absorbed by another participating VPP household.
The total physical export from the source premises must remain within the site's modelled maximum connection export capability and applicable equipment constraints.
This is a demonstrator modelling assumption used to investigate the potential effect of VPP coordination on DER utilisation and PV curtailment. It is not intended to represent a confirmed DNSP operating rule.


### A10 - Network-Support Export-Limit Override
**Type:** Network-support research scenario

During an explicit external/DNSP network-support request, the model assumes that the normal dynamic export limit may be temporarily increased where additional VPP export is requested.
The temporary export allowance must remain within the site's modelled maximum connection export capability and applicable equipment constraints.
When the network-support event ends, the site returns to its applicable normal dynamic export limit.
This is a demonstrator modelling assumption and is not intended to represent a confirmed DNSP operating rule.


### A11 - PV Curtailment
**Type:** Control/network assumption

PV generation is curtailed when available generation cannot be consumed by local household demand, stored within available battery capacity, transferred through permitted VPP coordination, or exported within the applicable connection and equipment constraints.
Curtailed PV is explicitly recorded by the simulation rather than being treated as exported or consumed energy.


### A12 - Battery Power Ratings
**Type:** Simulation assumption

Normal battery operation uses continuous charge and discharge power ratings rather than short-duration peak ratings because the simulation timestep represents substantially longer operating intervals, typically 30 minutes to one hour.

### A13 - Load and PV Profile Temporal Alignment
**Type:** 

Household demand profiles and SAM PV generation profiles are derived from different source years. Representative PV periods are therefore aligned with the selected household load periods by calendar season/week rather than by matching historical date and weather conditions. The resulting profiles are intended to provide representative coincident residential demand and solar generation behaviour for the VPP demonstrator, rather than reproduce a specific historical operating period.

### A14 -Baseline PV Weather Selection
**Type:**

The default VPP simulation uses representative PV generation periods with generally favourable and consistent solar conditions. This provides a stable baseline for evaluating household DER behaviour and VPP control strategies. Periods exhibiting significant weather-related reductions in PV generation may be retained separately for later weather-affected simulation scenarios rather than being used in the baseline case.

### A15 -  PV System Configuration
**Type:**

The VPP demonstrator uses representative residential PV system capacities rather than modelling specific commercial installations. The following DC nameplate capacities are assumed:

- House 1: 13.3 kWdc
- House 2: 6.6 kWdc
- House 3: 13.3 kWdc
- House 4: 20.0 kWdc
- House 5: No PV system

House 4 represents a larger three-phase PV installation, while the remaining PV-equipped houses represent single-phase residential installations.

All PV systems are modelled in NREL SAM using the PVWatts model with a common DC/AC ratio of 1.25. This gives representative inverter capacities of approximately 10.64 kWac for the 13.3 kWdc systems, 5.28 kWac for the 6.6 kWdc system, and 16.0 kWac for the 20.0 kWdc three-phase system.
These inverter capacities are modelling assumptions and are treated separately from the premises connection-point export limits.

### A16 - PV Orientation and System Performance
**Type:**

All VPP PV systems are modelled as fixed, north-facing rooftop arrays with a 27° tilt. Identical orientation is assumed across participating houses to isolate the effects of PV system capacity, household demand and VPP control behaviour.
The following common PVWatts assumptions are used:

- Module type: Premium
- Tracking: Fixed / no tracking
- Tilt: 27°
- Azimuth: 0° (North)
- DC/AC ratio: 1.25
- Inverter efficiency: 96%
- Total system losses: 14%
- Ground coverage ratio (GCR): SAM default
  
These parameters provide a consistent representative PV model across all participating houses rather than attempting to reproduce the exact physical characteristics of individual residential installations.


### A17 - PV Inverter and Generation Profile Modelling
**Type:**

PV generation profiles imported into the VPP simulation represent the AC output of the PV inverter rather than raw DC array production.
PV inverter conversion efficiency, DC/AC sizing and inverter clipping are therefore accounted for within the NREL SAM PVWatts model. These effects are not reapplied to the imported generation profile within the Python VPP simulation.
PV inverter capacity, battery inverter capacity and premises connection-point export capacity are treated as separate constraints. House 4 is represented using a three-phase PV inverter, while individual phase power flows are not explicitly modelled.


### A18 - Simulation Temporal Resolution
**Type:**

The VPP demonstrator operates using 30-minute timesteps (0.5 h) to align the PV generation profiles with the available residential household demand data.
Load and PV generation profiles represent average power over each 30-minute interval. Energy quantities are determined using the corresponding 0.5-hour simulation timestep.


### A1 -
**Type:**

































### A01 - VPP conceptual boundary
**Type:** Model assumption

The VPP model consists of only the 5 houses and their associated DERs. The hospital and wind/DFIG systems are external demonstrations elements to enhance user conceptual understanding and are not a part of the imediate network/grid

### A02 - Grid Connections
**Type:** Model simplification

The residential connections are represented using aggregate kW flows rather than explicite per phase power flows to simplify the model. single or three phase connections are represented to portray the dynamic connection export limits found
in the QLD network.

### A03 - Export Capacities
**Type:** Model Assumption

the single phase connections have a modelled export capacity of 10kW export limit for both the PV and BESS inverters (20kW cumulative). The three phase connections have a cumulative 30kW aggregated maximum under the 10kW per phase dynamic 
export limits available in QLD

### A04 - Dynamic Export Limits
**Type:** Model Assumption

Dynamic export limits may vary between 1.5kW/phase and 10kW/phase under the general model.

### A05 - Inverter Ratings
**Type:** Model Architecture

PV and BESS inverter ratings and premisis connection/export limit are indepentdant constraints.

### A06 - Battery capacities
**Type:** Battery Model Assumption

The SigenStor usable battery capacity and depth of charge is modelled from 0-100% SOC based on the specs provided by the manufacturers datasheet/website. any reserves are VPP strategy rather than hardware constraints

### A07 - BESS power capacity 
**Type:** Battery Model Assumption

Based off manufactures specs the battery modules power capacity scalues with module count and instanteous power capacity cannot exceed inverter safetey limits (10kW)

### A08 - Surpluss PV sharing
**Type:** VPP operation assumption

Any surplus PV that is produced within the VPP network is assumed to be shareable/storeable with other VPP households with available capacity. This represents VPP coordinated network strategy rather than a physical connection between household
resources. 

### A09 - Export Cap exceptions
**Type:** VPP assumption/optimisation research area

VPP directed PV surplus may exceed a site's current dynamic export cap (assuming it falls within safety measures) to share or store surplus within available capacity in the VPP network.

Additionally during external/DNSP network support request events it is assumed that dynamic caps will be raised to maximum safe limit if required to meet demand of request. 

### A10 - PV Curtailment
**Type:** Control/Network Assumption

When PV generation exceeds residential load demand, export caps, VPP network storage capacity and inverter safety caps, then remaining surplus will be curtailed.    

### A11 - Battery Power ratings
**Type:** Simulation assumption

Normal battery operation uses continuous power ratings rather than shor duration peak ratings because simulation timesteps represent longer operating intervals (30 min to 1 hr)