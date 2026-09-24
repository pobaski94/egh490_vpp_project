# EGH490 VPP — Research and Design Investigations

## Purpose

This document records research questions, controller concepts,
economic considerations, and potential future investigations that
emerge during development of the VPP demonstrator.

Items recorded here are not necessarily implemented design decisions
or simulation assumptions. They are retained for later investigation,
comparison, validation, or inclusion in the thesis.

---

## R01 — VPP Surplus-PV Allocation Hierarchy

### Observation

The current shared-PV implementation primarily considers surplus PV
as energy that can be allocated toward available battery charging
capacity at other participating houses.

Simulation testing identified that surplus PV could alternatively be
coordinated to meet the electrical demand of another VPP participant
before that participant discharges its own battery or imports energy
from the grid.

House 5 is particularly relevant because it has battery storage but
no local PV generation.

### Research Question

When surplus PV is available within the VPP, should coordinated
operation prioritise:

1. demand at other participating houses,
2. charging available VPP battery capacity,
3. grid export,
4. or some economically optimised combination of these actions?

### Economic Motivation

Where the retail electricity import tariff is greater than the
available feed-in tariff, using surplus PV to offset another
participant's grid import may provide greater aggregate value than
exporting that energy directly to the grid.

For a participant such as House 5, supplying its daytime demand from
surplus VPP PV may also preserve its battery SOC for later dispatch.

The preserved battery energy could potentially have greater value
during:

- higher-price periods,
- peak-shaving periods,
- network-support events,
- periods of low VPP generation,
- or future market/service events.

This suggests that a participant without PV may still provide
significant value to the VPP through its available storage capacity.

### Potential Controller Hierarchies to Compare

**Independent self-consumption**

Own PV -> own load -> own battery -> grid

**Coordinated load-priority sharing**

Own PV -> own load -> own battery
                     |
                     -> other VPP participant demand
                     -> other VPP battery capacity
                     -> grid export

**Economic optimisation**

Dispatch based on the relative value of:

- avoided grid imports,
- feed-in tariff revenue,
- battery charging/discharging losses,
- future electricity prices,
- available battery SOC,
- network-service value,
- and other VPP revenue streams.

### Future Investigation

Compare alternative dispatch strategies using identical household
load, PV generation, battery, and connection profiles.

Potential performance measures include:

- VPP grid import,
- VPP grid export,
- participant grid import,
- PV self-consumption/utilisation,
- PV curtailment,
- battery throughput,
- battery SOC availability,
- network-support capability,
- participant electricity cost,
- VPP revenue,
- and total economic benefit.

The preferred hierarchy should not be assumed in advance. It should
be evaluated using the simulation and later economic model.