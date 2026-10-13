
# ============================================================
# SCENARIO CONFIGURATION
# ============================================================
#
# Builds the coordinated VPP demonstration scenario from
# pre-processed household load/PV profiles.
# ============================================================


from models.residential import House, Battery
from models.external import LocalLoad, WindTurbine
from control.vpp_controller import VPPController
from simulation.vpp_simulation import VPPSimulation
from economics.financial_model import FinancialModel
from economics.tariffs import (BATTERY_STARTER,BATTERY_LITE,BATTERY_CHARGE)


# ============================================================
# BATTERY CONFIGURATION
# ============================================================

SIGEN_MODULE_USABLE_KWH = 8.76
SIGEN_MODULE_POWER_KW = 4.6
BESS_INVERTER_LIMIT_KW = 10.0


def create_sigenstor_spec(
    module_count,
    initial_soc_percent=50.0
):

    usable_capacity_kwh = (
        module_count * SIGEN_MODULE_USABLE_KWH
    )

    raw_stack_power_kw = (
        module_count * SIGEN_MODULE_POWER_KW
    )

    max_bess_power_kw = min(
        raw_stack_power_kw,
        BESS_INVERTER_LIMIT_KW
    )

    initial_soc_kwh = (
        usable_capacity_kwh
        * initial_soc_percent / 100.0
    )

    return {
        "capacity_kwh": usable_capacity_kwh,
        "initial_soc_kwh": initial_soc_kwh,
        "max_charge_kw": max_bess_power_kw,
        "max_discharge_kw": max_bess_power_kw,
        "efficiency": 0.95,
        "min_soc_kwh": 0.0,
        "manufacturer": "Sigenergy",
        "model": "SigenStor BAT 9.0",
        "module_count": module_count,
    }


# ============================================================
# COORDINATED VPP SCENARIO
# ============================================================

def create_coordinated_vpp_scenario(
    house_loads,
    house_pv,
    dynamic_export_profile_kw_per_phase,
    hospital_load_profile,
    wind_generation_profile,
    timestep_hours,
    num_steps,
    tariff=BATTERY_STARTER
):

    controller = VPPController(
        default_mode="self_consumption",
        peak_hours=[
            16.0, 16.5,
            17.0, 17.5,
            18.0, 18.5,
            19.0, 19.5,
            20.0, 20.5,
        ],
        cheap_energy_hours=[]
    )

    house1_battery = Battery(
        **create_sigenstor_spec(
            module_count=3
        )
    )

    house2_battery = Battery(
        **create_sigenstor_spec(
            module_count=2
        )
    )

    house4_battery = Battery(
        **create_sigenstor_spec(
            module_count=3
        )
    )

    house5_battery = Battery(
        **create_sigenstor_spec(
            module_count=5
        )
    )

    houses = [

        House(
            name="House 1",
            load_profile=house_loads["House 1"],
            generation_profile=house_pv["House 1"],
            battery=house1_battery,
            pv_array_kwp=13.3,
            pv_inverter_limit_kw=10.64,
            connection_type="single_phase",
            connection_phases=1,
            dynamic_export_profile_kw_per_phase=(
                dynamic_export_profile_kw_per_phase
            )
        ),

        House(
            name="House 2",
            load_profile=house_loads["House 2"],
            generation_profile=house_pv["House 2"],
            battery=house2_battery,
            pv_array_kwp=6.6,
            pv_inverter_limit_kw=5.28,
            connection_type="single_phase",
            connection_phases=1,
            dynamic_export_profile_kw_per_phase=(
                dynamic_export_profile_kw_per_phase
            )
        ),

        House(
            name="House 3",
            load_profile=house_loads["House 3"],
            generation_profile=house_pv["House 3"],
            battery=None,
            pv_array_kwp=13.3,
            pv_inverter_limit_kw=10.64,
            connection_type="single_phase",
            connection_phases=1,
            dynamic_export_profile_kw_per_phase=(
                dynamic_export_profile_kw_per_phase
            )
        ),

        House(
            name="House 4",
            load_profile=house_loads["House 4"],
            generation_profile=house_pv["House 4"],
            battery=house4_battery,
            pv_array_kwp=20.0,
            pv_inverter_limit_kw=16.0,
            connection_type="three_phase",
            connection_phases=3,
            dynamic_export_profile_kw_per_phase=(
                dynamic_export_profile_kw_per_phase
            )
        ),

        House(
            name="House 5",
            load_profile=house_loads["House 5"],
            generation_profile=house_pv["House 5"],
            battery=house5_battery,
            pv_array_kwp=0.0,
            pv_inverter_limit_kw=0.0,
            connection_type="single_phase",
            connection_phases=1,
            dynamic_export_profile_kw_per_phase=(
                dynamic_export_profile_kw_per_phase
            )
        ),
    ]

    hospital = LocalLoad(
        "Hospital",
        hospital_load_profile
    )

    wind = WindTurbine(
        "DFIG Wind Placeholder",
        wind_generation_profile
    )

    financial_model = FinancialModel(
        tariff=tariff
    )

    simulation = VPPSimulation(
        houses=houses,
        hospital=hospital,
        wind=wind,
        controller=controller,
        timestep_hours=timestep_hours,
        financial_model=financial_model,
        num_steps=num_steps
    )

    return simulation