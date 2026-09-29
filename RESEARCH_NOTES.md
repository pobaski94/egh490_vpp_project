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



## R09 - 2025 QLD High-Price Market Opportunities

Analysis of the complete 2025 AEMO QLD1 five-minute dataset identified limited but significant periods of high wholesale electricity prices:

≥ $500/MWh: 18.50 hours/year
≥ $1,000/MWh: 12.33 hours/year
≥ $2,000/MWh: 7.58 hours/year
Approximately 95% of ≥$1,000/MWh intervals occurred between 4–9 PM.
≥$1,000/MWh conditions occurred across only 22 days, indicating that high-value periods are rare and concentrated.

Research avenue: Investigate how much energy the five-house VPP could realistically make available during these historical high-price periods, considering battery SOC, PV availability, household demand, inverter limits, and dynamic connection constraints. This could quantify the economic value of coordinated VPP dispatch during high-value market conditions.

Note: These price thresholds currently represent research-defined market conditions, not confirmed VPP activation thresholds. AEMO VPP research should be reviewed before defining the controller's event methodology.

## R10 — Overview of Australian VPP Operation

Australian residential VPP offerings generally coordinate distributed solar PV and battery systems so that household DER can provide value beyond individual self-consumption. The reviewed commercial offerings show that there is no single standard Australian VPP operating model.

Common characteristics identified across current offerings include:

Central battery control: VPP operators may remotely charge, discharge or hold participating batteries during selected operating periods or events.
Customer SOC reserves: Several providers maintain homeowner-selected or predefined battery reserves, commonly around 10–20%, preserving backup/customer energy while allowing VPP participation.
Normal energy operation: Outside VPP events, customers continue to import/export electricity under their applicable retail tariff and feed-in tariff.
Event-based incentives: Several offerings provide additional compensation for battery energy supplied during designated VPP events, with examples in the reviewed market offering approximately $1/kWh for eligible event energy.
Time-dependent incentives: Some offerings provide increased export value during particular peak periods, creating an incentive to preserve battery energy for later export.
Grid charging: Some programs allow or incentivise batteries to charge from the grid, meaning VPP optimisation is not necessarily restricted to storing excess rooftop PV.
Different commercial structures: Australian VPPs use combinations of fixed participation credits, event payments, enhanced feed-in tariffs, wholesale-price exposure and energy-plan benefits.

Project relevance: The demonstrator should therefore represent the VPP as a coordinator of flexible residential DER rather than a single fixed operating strategy. A representative model can combine normal household operation, economic battery dispatch, an SOC reserve, dynamic connection constraints, and externally initiated support events. This provides a basis for investigating whether coordinated operation improves the economic performance of the five participating prosumers.