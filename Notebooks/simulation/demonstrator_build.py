#!/usr/bin/env python
# coding: utf-8

# ============================================================
# EGH490 VIRTUAL POWER PLANT DEMONSTRATOR
# ============================================================
#
# Live hardware demonstrator using the representative
# one-week summer profiles.
#
# The one-week profiles repeat continuously.
#
# Three simulations run in parallel:
#
#   1. Coordinated VPP
#   2. Independent houses + dynamic envelope
#   3. Independent houses + fixed 5 kW/phase limit
#
# Only the coordinated simulation controls the physical
# demonstrator hardware.
#
# Simulation resolution: 30 minutes.
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import os
import sys
import time

import numpy as np
import pandas as pd


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = (
    "/home/jpobar/egh490_vpp_project"
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ============================================================
# PROJECT IMPORTS
# ============================================================

from scenarios.scenario_setup import (
    create_coordinated_vpp_scenario,
    create_independent_dynamic_scenario,
    create_independent_fixed_scenario,
)

from scenarios.dynamic_envelopes import (
    create_daily_dynamic_envelope
)

from economics.tariffs import (
    BATTERY_STARTER,
    BATTERY_LITE
)

from hardware.hardware_interface import (
    HardwareInterface
)


# ============================================================
# BASIC SIMULATION CONFIGURATION
# ============================================================

timestep_hours = 0.5

playback_delay_seconds = 1.0

fixed_export_limit_kw_per_phase = 5.0




# ============================================================
# DEMONSTRATOR CONTROL DEFAULTS
# ============================================================
#
# Normal operation:
#
#   - self consumption
#   - PV sharing enabled
#   - economic export disabled
#   - network-support event disabled
#
# These states will later be controlled by physical buttons.
# ============================================================

pv_sharing_enabled = True

economic_export_enabled = True

network_support_active = False

VPP_EVENT_REQUEST_KW = 15.0


# ============================================================
# VPP EVENT CONFIGURATION
# ============================================================
#
# Network-support events are limited to three simulated hours.
#
# At 30-minute resolution:
#
#       3 hours / 0.5 hours = 6 simulation steps
#
# Event reserve behaviour will be added to the controller /
# house dispatch separately.
# ============================================================

VPP_EVENT_DURATION_HOURS = 3.0

VPP_EVENT_DURATION_STEPS = int(
    VPP_EVENT_DURATION_HOURS
    / timestep_hours
)

vpp_event_end_step = None


# ============================================================
# LOAD SUMMER PROFILE DATA
# ============================================================

summer_data = pd.read_csv(
    "SUMMER Generation and Load profiles.csv"
)

print(
    "\n=== SUMMER PROFILE CHECK ==="
)

print(
    f"Rows loaded: "
    f"{len(summer_data)}"
)

print(
    f"Missing values: "
    f"{summer_data.isna().sum().sum()}"
)


# ============================================================
# HOUSE LOAD PROFILES
# ============================================================

house_1_load = (
    summer_data[
        "H1_HI_B_kW"
    ].to_numpy()
)

house_2_load = (
    summer_data[
        "H2_MED_B_kW"
    ].to_numpy()
)

house_3_load = (
    summer_data[
        "H3_LOW_A_kW"
    ].to_numpy()
)

house_4_load = (
    summer_data[
        "H4_HI_A_kW"
    ].to_numpy()
)

house_5_load = (
    summer_data[
        "H5_MED_A_kW"
    ].to_numpy()
)


# ============================================================
# HOUSE PV PROFILES
# ============================================================

house_1_pv = (
    summer_data[
        "PV_13.3kW_kW"
    ].to_numpy()
)

house_2_pv = (
    summer_data[
        "PV_6.6kW_kW"
    ].to_numpy()
)

house_3_pv = (
    summer_data[
        "PV_13.3kW_kW"
    ].to_numpy()
)

house_4_pv = (
    summer_data[
        "PV_20kW_kW"
    ].to_numpy()
)

house_5_pv = np.zeros(
    len(summer_data)
)


# ============================================================
# SIMULATION LENGTH
# ============================================================

num_steps = len(
    summer_data
)

simulation_hours = (
    num_steps
    * timestep_hours
)

simulation_days = (
    simulation_hours
    / 24
)

print(
    f"Simulation profile length: "
    f"{simulation_days:.1f} days"
)


# ============================================================
# EXTERNAL DEMONSTRATION PROFILES
# ============================================================

hospital_load_profile = np.full(
    num_steps,
    6.0
)

wind_generation_profile = np.zeros(
    num_steps
)


# ============================================================
# DEMONSTRATOR DYNAMIC EXPORT ENVELOPE
# ============================================================
#
# Moderate connection restriction through the solar period,
# with an aggressive restriction between 11:00 and 14:00.
# ============================================================

daily_dynamic_export_kw_per_phase = (
    create_daily_dynamic_envelope(
        timestep_hours=timestep_hours,
        default_limit_kw_per_phase=10.0,
        periods=[
            {
                "start_hour": 8.0,
                "end_hour": 10.0,
                "limit_kw_per_phase": 6.0,
            },
            {
                "start_hour": 10.0,
                "end_hour": 11.0,
                "limit_kw_per_phase": 3.0,
            },
            {
                "start_hour": 11.0,
                "end_hour": 14.0,
                "limit_kw_per_phase": 1.5,
            },
            {
                "start_hour": 14.0,
                "end_hour": 15.0,
                "limit_kw_per_phase": 3.0,
            },
        ]
    )
)

assert (
    len(
        daily_dynamic_export_kw_per_phase
    )
    == 48
)

repeat_count = int(
    np.ceil(
        num_steps
        / len(
            daily_dynamic_export_kw_per_phase
        )
    )
)

dynamic_export_profile_kw_per_phase = (
    np.tile(
        daily_dynamic_export_kw_per_phase,
        repeat_count
    )[:num_steps]
)


# ============================================================
# PROFILE DICTIONARIES
# ============================================================

house_loads = {
    "House 1": house_1_load,
    "House 2": house_2_load,
    "House 3": house_3_load,
    "House 4": house_4_load,
    "House 5": house_5_load,
}

house_pv = {
    "House 1": house_1_pv,
    "House 2": house_2_pv,
    "House 3": house_3_pv,
    "House 4": house_4_pv,
    "House 5": house_5_pv,
}


# ============================================================
# PROFILE LENGTH VALIDATION
# ============================================================

profiles = [
    house_1_load,
    house_2_load,
    house_3_load,
    house_4_load,
    house_5_load,

    house_1_pv,
    house_2_pv,
    house_3_pv,
    house_4_pv,
    house_5_pv,

    dynamic_export_profile_kw_per_phase,
    hospital_load_profile,
    wind_generation_profile,
]

profile_lengths = {
    len(profile)
    for profile in profiles
}

if len(profile_lengths) != 1:

    raise ValueError(
        "Demonstrator profiles are not "
        "the same length."
    )

print(
    "All demonstrator profiles "
    "are the same length."
)


# ============================================================
# HARDWARE STATE HELPER
# ============================================================

def get_hardware_states(
    simulation
):
    """
    Convert latest battery results into physical LED states.
    """

    states = {}

    tolerance = 1e-6

    for house in simulation.houses:

        if house.battery is None:

            states[
                house.name
            ] = {
                "state":
                    "no_battery",

                "soc_percent":
                    0.0,
            }

            continue

        latest = (
            simulation
            .house_results_log[
                house.name
            ][-1]
        )

        soc_kwh = latest[
            "battery_soc_kwh"
        ]

        charge_kw = latest[
            "battery_charge_kw"
        ]

        discharge_kw = latest[
            "battery_discharge_kw"
        ]

        soc_percent = latest[
            "battery_soc_percent"
        ]

        max_soc_kwh = (
            house.battery
            .capacity_kwh
        )

        min_soc_kwh = (
            house.battery
            .min_soc_kwh
        )

        if (
            soc_kwh
            >= max_soc_kwh
            - tolerance
        ):

            state = "full"

        elif (
            soc_kwh
            <= min_soc_kwh
            + tolerance
        ):

            state = "minimum"

        elif charge_kw > tolerance:

            state = "charging"

        elif discharge_kw > tolerance:

            state = "discharging"

        else:

            state = "idle"

        states[
            house.name
        ] = {
            "state":
                state,

            "soc_percent":
                soc_percent,
        }

    return states


# ============================================================
# CREATE SIMULATIONS
# ============================================================

coordinated_simulation = (
    create_coordinated_vpp_scenario(
        house_loads=house_loads,
        house_pv=house_pv,

        dynamic_export_profile_kw_per_phase=(
            dynamic_export_profile_kw_per_phase
        ),

        hospital_load_profile=(
            hospital_load_profile
        ),

        wind_generation_profile=(
            wind_generation_profile
        ),

        timestep_hours=timestep_hours,
        num_steps=num_steps,
        tariff=BATTERY_LITE
    )
)

independent_dynamic_simulation = (
    create_independent_dynamic_scenario(
        house_loads=house_loads,
        house_pv=house_pv,

        dynamic_export_profile_kw_per_phase=(
            dynamic_export_profile_kw_per_phase
        ),

        hospital_load_profile=(
            hospital_load_profile
        ),

        wind_generation_profile=(
            wind_generation_profile
        ),

        timestep_hours=timestep_hours,
        num_steps=num_steps,
        tariff=BATTERY_STARTER
    )
)


independent_fixed_simulation = (
    create_independent_fixed_scenario(
        house_loads=house_loads,
        house_pv=house_pv,

        hospital_load_profile=(
            hospital_load_profile
        ),

        wind_generation_profile=(
            wind_generation_profile
        ),

        timestep_hours=timestep_hours,
        num_steps=num_steps,
        tariff=BATTERY_STARTER,

        fixed_export_limit_kw_per_phase=(
            fixed_export_limit_kw_per_phase
        )
    )
)


# ============================================================
# BASELINE INPUTS
# ============================================================

coordinated_inputs = {
    "network_support_request":
        False,

    "requested_support_kw":
        0.0,

    "pv_sharing_enabled":
        True,

    "peak_shaving_enabled":
        False,

    "economic_export_enabled":
        True,

    "vpp_tariff_event":
        False,
}


independent_inputs = {
    "network_support_request":
        False,

    "requested_support_kw":
        0.0,

    "pv_sharing_enabled":
        False,

    "peak_shaving_enabled":
        False,

    "economic_export_enabled":
        False,

    "vpp_tariff_event":
        False,
}


# ============================================================
# INITIALISE HARDWARE
# ============================================================

hardware = HardwareInterface()


# ============================================================
# CONTINUOUS DEMONSTRATOR LOOP
# ============================================================
def build_live_state(
    coordinated_result,
    independent_dynamic_result,
    independent_fixed_result,
    hardware_states,
):
    """
    Build one dashboard snapshot from the latest
    demonstrator timestep.
    """

    houses = {}

    for house in coordinated_simulation.houses:

        latest = (
            coordinated_simulation
            .house_results_log[
                house.name
            ][-1]
        )

        houses[house.name] = {
            "state":
                hardware_states[
                    house.name
                ]["state"],

            "load_kw":
                latest["load_kw"],

            "pv_kw":
                latest["generation_kw"],

            "battery_soc_kwh":
                latest["battery_soc_kwh"],

            "battery_soc_percent":
                latest["battery_soc_percent"],

            "battery_charge_kw":
                latest["battery_charge_kw"],

            "battery_discharge_kw":
                latest["battery_discharge_kw"],

            "grid_import_kw":
                latest["external_grid_import_kw"],

            "grid_export_kw":
                latest["external_grid_export_kw"],

            "current_export_limit_kw":
                latest["current_export_limit_kw"],

            "vpp_event_target_kw":
                latest.get(
                    "vpp_event_target_kw",
                    0.0
                ),

            "vpp_event_export_kw":
                latest.get(
                    "vpp_event_export_kw",
                    0.0
                ),

            "normal_grid_export_kw":
                latest.get(
                    "normal_grid_export_kw",
                    0.0
                ),
        }

    total_event_export_kw = sum(
        data["vpp_event_export_kw"]
        for data in houses.values()
    )

    return {
        "simulation": {
            "step":
                coordinated_result[
                    "Simulation_step"
                ],

            "day":
                coordinated_result[
                    "Day_number"
                ],

            "hour":
                coordinated_result[
                    "Hour_of_day"
                ],

            "mode":
                coordinated_result[
                    "VPP_mode"
                ],
        },

        "controls": {
            "pv_sharing_enabled":
                pv_sharing_enabled,

            "economic_export_enabled":
                economic_export_enabled,

            "vpp_event_active":
                network_support_active,
        },

        "vpp": {
            "grid_import_kw":
                coordinated_result[
                    "VPP_grid_import_kw"
                ],

            "grid_export_kw":
                coordinated_result[
                    "VPP_grid_export_kw"
                ],

            "battery_power_kw":
                coordinated_result[
                    "Battery_power_kw"
                ],

            "battery_soc_kwh":
                coordinated_result[
                    "Battery_soc_kwh"
                ],

            "shared_pv_kw":
                coordinated_result[
                    "Shared_PV_transferred_kw"
                ],

            "requested_event_kw":
                coordinated_result[
                    "Requested_support_kw"
                ],

            "delivered_event_kw":
                total_event_export_kw,

            "available_event_kw":
                coordinated_result.get(
                    "VPP_event_available_kw",
                    0.0
                ),

            "net_cost":
                coordinated_result[
                    "VPP_cumulative_net_cost"
                ],
        },

        "comparison": {
            "coordinated_net_cost":
                coordinated_result[
                    "VPP_cumulative_net_cost"
                ],

            "independent_dynamic_net_cost":
                independent_dynamic_result[
                    "VPP_cumulative_net_cost"
                ],

            "independent_fixed_net_cost":
                independent_fixed_result[
                    "VPP_cumulative_net_cost"
                ],
        },

        "houses":
            houses,
    }


def step_demonstrator():

    global pv_sharing_enabled
    global economic_export_enabled
    global network_support_active
    global vpp_event_end_step

# try:

#     print(
#         "\nContinuous VPP demonstrator started."
#     )

#     print(
#         "Use interrupt / stop to end the run.\n"
#     )

    # while True:

        # ----------------------------------------------------
        # READ HARDWARE INPUTS
        # ----------------------------------------------------

    hardware_inputs = (
        hardware.read_inputs()
    )


    # ----------------------------------------------------
    # UPDATE DEMONSTRATOR TOGGLES
    # ----------------------------------------------------
    #
    # For now these use defaults plus any values already
    # provided by HardwareInterface.
    #
    # The HardwareInterface will be updated next so the
    # physical buttons directly toggle:
    #
    #   - PV sharing
    #   - economic export
    #   - VPP network-support event
    # ----------------------------------------------------

    if (
        "pv_sharing_enabled"
        in hardware_inputs
    ):

        pv_sharing_enabled = (
            hardware_inputs[
                "pv_sharing_enabled"
            ]
        )

    if (
        "economic_export_enabled"
        in hardware_inputs
    ):

        economic_export_enabled = (
            hardware_inputs[
                "economic_export_enabled"
            ]
        )


    # ----------------------------------------------------
    # NETWORK-SUPPORT EVENT TIMER
    # ----------------------------------------------------

    if hardware_inputs.get(
        "network_support_request",
        False
    ):

        if (
            vpp_event_end_step
            is None
        ):

            vpp_event_end_step = (
                coordinated_simulation
                .current_step
                + VPP_EVENT_DURATION_STEPS
            )

    if (
        vpp_event_end_step
        is not None
    ):

        network_support_active = (
            coordinated_simulation
            .current_step
            < vpp_event_end_step
        )

        if not network_support_active:

            vpp_event_end_step = None
            
            hardware.clear_network_support()

    else:

        network_support_active = False


    # ----------------------------------------------------
    # BUILD COORDINATED INPUTS
    # ----------------------------------------------------

    coordinated_inputs[
        "pv_sharing_enabled"
    ] = (
        pv_sharing_enabled
    )

    coordinated_inputs[
        "economic_export_enabled"
    ] = (
        economic_export_enabled
    )

    coordinated_inputs[
        "network_support_request"
    ] = (
        network_support_active
    )

    coordinated_inputs[
        "requested_support_kw"
    ] = (
        VPP_EVENT_REQUEST_KW
        if network_support_active
        else 0.0
    )
    
    coordinated_inputs[
        "vpp_tariff_event"
    ] = (
        network_support_active
    )


    # ----------------------------------------------------
    # STEP COORDINATED VPP
    # ----------------------------------------------------
   
    coordinated_result = (
        coordinated_simulation.step(
            coordinated_inputs
        )
    )


    # ----------------------------------------------------
    # STEP BACKGROUND COMPARISON SCENARIOS
    # ----------------------------------------------------

    independent_dynamic_result = (
        independent_dynamic_simulation
        .step(
            independent_inputs
        )
    )

    independent_fixed_result = (
        independent_fixed_simulation
        .step(
            independent_inputs
        )
    )


    # ----------------------------------------------------
    # UPDATE PHYSICAL HARDWARE
    # ----------------------------------------------------

    hardware_states = (
        get_hardware_states(
            coordinated_simulation
        )
    )

    hardware.update_outputs(
        coordinated_result,
        hardware_states
    )

    # ----------------------------------------------------
    # BUILD LIVE DASHBOARD STATE
    # ----------------------------------------------------


    live_state = build_live_state(
        coordinated_result,
        independent_dynamic_result,
        independent_fixed_result,
        hardware_states,
    )

    return live_state


def cleanup_demonstrator():

    hardware.cleanup()

    print(
        "Hardware interface cleaned up."
    )
