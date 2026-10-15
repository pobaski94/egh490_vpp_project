import os
from datetime import datetime

import pandas as pd


HOUSE_EXPORT_COLUMNS = [
    "load_kw",
    "available_generation_kw",
    "generation_kw",
    "pv_curtailment_kw",

    "battery_power_kw",
    "battery_charge_kw",
    "battery_discharge_kw",
    "battery_soc_kwh",
    "battery_soc_percent",

    "net_power_kw_before_battery",
    "net_power_kw",

    "dynamic_export_limit_kw",
    "current_export_limit_kw",
    "effective_export_limit_kw",
    "export_limit_active",

    "shared_pv_export_target_kw",

    "shared_pv_received_kw",
    "shared_pv_supplied_kw",
    "shared_pv_received_kwh",
    "shared_pv_supplied_kwh",
    
    "physical_net_power_kw",
    "physical_grid_import_kw",
    "physical_grid_export_kw",
    
    "external_grid_import_kw",
    "external_grid_export_kw",
    "external_grid_net_power_kw",
    
    "external_grid_import_kwh",
    "external_grid_export_kwh",

    "import_energy_kwh",
    "export_energy_kwh",
    "import_rate",
    "export_rate",
    

    "import_cost",
    "export_revenue",
    "net_cost",

    "cumulative_import_cost",
    "cumulative_export_revenue",
    "cumulative_net_cost",

    
]


SUMMARY_EXPORT_COLUMNS = [
    "Simulation_step",
    "Day_number",
    "Hour_of_day",
    "VPP_mode",

    "VPP_net_power_kw",

    "VPP_import_energy_kwh",
    "VPP_export_energy_kwh",

    "VPP_import_cost",
    "VPP_export_revenue",
    "VPP_net_cost",

    "VPP_cumulative_import_cost",
    "VPP_cumulative_export_revenue",
    "VPP_cumulative_net_cost",

    "PV_sharing_enabled",
    "Shared_PV_available_kw",

    "Requested_support_kw",
    "Battery_discharge_kw",

    "Tariff_plan",
    "VPP_tariff_event",

    "Shared_PV_received_kw",
    "Shared_PV_supplied_kw",            
    "Shared_PV_balance_error_kw",
]

def prepare_house_export(house_log):

    house_df = pd.DataFrame(
        house_log
    )

    available_columns = [
        column
        for column in HOUSE_EXPORT_COLUMNS
        if column in house_df.columns
    ]

    return house_df[
        available_columns
    ].round(3)


def prepare_summary_export(simulation):

    summary_df = pd.DataFrame(
        simulation.simulation_results_summary
    )

    available_columns = [
        column
        for column in SUMMARY_EXPORT_COLUMNS
        if column in summary_df.columns
    ]

    return summary_df[
        available_columns
    ].round(3)


def export_comparison_results(
    coordinated_simulation,
    independent_dynamic_simulation,
    independent_fixed_simulation,
    results_directory="results"
):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M"
    )

    filename = (
        f"SimulationResults_comparison_"
        f"{timestamp}.xlsx"
    )

    filepath = os.path.join(
        results_directory,
        filename
    )

    os.makedirs(
        results_directory,
        exist_ok=True
    )

    coordinated_summary_df = (
        prepare_summary_export(
            coordinated_simulation
        )
    )

    independent_dynamic_summary_df = (
        prepare_summary_export(
            independent_dynamic_simulation
        )
    )

    independent_fixed_summary_df = (
        prepare_summary_export(
            independent_fixed_simulation
        )
    )

    with pd.ExcelWriter(
        filepath,
        engine="openpyxl"
    ) as writer:

        # ------------------------------------------
        # Coordinated VPP
        # ------------------------------------------

        coordinated_summary_df.to_excel(
            writer,
            sheet_name="Coordinated_Summary",
            index=False
        )

        for house_name, house_log in (
            coordinated_simulation
            .house_results_log.items()
        ):

            house_df = prepare_house_export(
                house_log
            )

            sheet_name = (
                "Coordinated_"
                + house_name.replace(" ", "_")
            )

            house_df.to_excel(
                writer,
                sheet_name=sheet_name[:31],
                index=False
            )

        # ------------------------------------------
        # Independent dynamic
        # ------------------------------------------

        independent_dynamic_summary_df.to_excel(
            writer,
            sheet_name="IndDyn_Summary",
            index=False
        )

        for house_name, house_log in (
            independent_dynamic_simulation
            .house_results_log.items()
        ):

            house_df = prepare_house_export(
                house_log
            )

            sheet_name = (
                "IndDyn_"
                + house_name.replace(" ", "_")
            )

            house_df.to_excel(
                writer,
                sheet_name=sheet_name[:31],
                index=False
            )

        # ------------------------------------------
        # Independent fixed
        # ------------------------------------------

        independent_fixed_summary_df.to_excel(
            writer,
            sheet_name="IndFixed_Summary",
            index=False
        )

        for house_name, house_log in (
            independent_fixed_simulation
            .house_results_log.items()
        ):

            house_df = prepare_house_export(
                house_log
            )

            sheet_name = (
                "IndFixed_"
                + house_name.replace(" ", "_")
            )

            house_df.to_excel(
                writer,
                sheet_name=sheet_name[:31],
                index=False
            )

        # ------------------------------------------
        # Final comparison sheet
        # ------------------------------------------

        comparison_df = pd.DataFrame([
            {
                "Scenario": "Coordinated VPP",
                "Cumulative Import Cost ($)":
                    coordinated_summary_df[
                        "VPP_cumulative_import_cost"
                    ].iloc[-1],

                "Cumulative Export Revenue ($)":
                    coordinated_summary_df[
                        "VPP_cumulative_export_revenue"
                    ].iloc[-1],

                "Cumulative Net Cost ($)":
                    coordinated_summary_df[
                        "VPP_cumulative_net_cost"
                    ].iloc[-1],

                "Total Import Energy (kWh)":
                    coordinated_summary_df[
                        "VPP_import_energy_kwh"
                    ].sum(),

                "Total Export Energy (kWh)":
                    coordinated_summary_df[
                        "VPP_export_energy_kwh"
                    ].sum(),
            },

            {
                "Scenario":
                    "Independent Dynamic",

                "Cumulative Import Cost ($)":
                    independent_dynamic_summary_df[
                        "VPP_cumulative_import_cost"
                    ].iloc[-1],

                "Cumulative Export Revenue ($)":
                    independent_dynamic_summary_df[
                        "VPP_cumulative_export_revenue"
                    ].iloc[-1],

                "Cumulative Net Cost ($)":
                    independent_dynamic_summary_df[
                        "VPP_cumulative_net_cost"
                    ].iloc[-1],

                "Total Import Energy (kWh)":
                    independent_dynamic_summary_df[
                        "VPP_import_energy_kwh"
                    ].sum(),

                "Total Export Energy (kWh)":
                    independent_dynamic_summary_df[
                        "VPP_export_energy_kwh"
                    ].sum(),
            },

            {
                "Scenario":
                    "Independent Fixed 5 kW/phase",

                "Cumulative Import Cost ($)":
                    independent_fixed_summary_df[
                        "VPP_cumulative_import_cost"
                    ].iloc[-1],

                "Cumulative Export Revenue ($)":
                    independent_fixed_summary_df[
                        "VPP_cumulative_export_revenue"
                    ].iloc[-1],

                "Cumulative Net Cost ($)":
                    independent_fixed_summary_df[
                        "VPP_cumulative_net_cost"
                    ].iloc[-1],

                "Total Import Energy (kWh)":
                    independent_fixed_summary_df[
                        "VPP_import_energy_kwh"
                    ].sum(),

                "Total Export Energy (kWh)":
                    independent_fixed_summary_df[
                        "VPP_export_energy_kwh"
                    ].sum(),
            },
        ]).round(3)

        comparison_df.to_excel(
            writer,
            sheet_name="Comparison",
            index=False
        )

    return filepath