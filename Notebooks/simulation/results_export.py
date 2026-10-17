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
           
    "Shared_PV_balance_error_kw",
    "Shared_PV_transferred_kw",
    "VPP_power_balance_error_kw",
    
    "VPP_shared_pv_received_kwh",
    "VPP_shared_pv_supplied_kwh",
    "VPP_shared_pv_cost",
    "VPP_shared_pv_revenue",
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

def build_scenario_metrics(
    simulation,
    scenario_name
):
    """
    Build headline technical and financial metrics for one
    complete simulation scenario.
    """

    summary_df = pd.DataFrame(
        simulation.simulation_results_summary
    )

    # --------------------------------------------------------
    # FINANCIAL / GRID ENERGY
    # --------------------------------------------------------

    total_import_energy_kwh = (
        summary_df["VPP_import_energy_kwh"].sum()
    )

    total_export_energy_kwh = (
        summary_df["VPP_export_energy_kwh"].sum()
    )

    cumulative_import_cost = (
        summary_df[
            "VPP_cumulative_import_cost"
        ].iloc[-1]
    )

    cumulative_export_revenue = (
        summary_df[
            "VPP_cumulative_export_revenue"
        ].iloc[-1]
    )

    cumulative_net_cost = (
        summary_df[
            "VPP_cumulative_net_cost"
        ].iloc[-1]
    )

    # Effective value received per exported kWh.
    if total_export_energy_kwh > 0:
        effective_export_value_c_per_kwh = (
            cumulative_export_revenue
            / total_export_energy_kwh
            * 100
        )
    else:
        effective_export_value_c_per_kwh = 0.0

    # --------------------------------------------------------
    # SHARED PV
    # --------------------------------------------------------

    if "VPP_shared_pv_received_kwh" in summary_df.columns:
        total_shared_pv_kwh = (
            summary_df[
                "VPP_shared_pv_received_kwh"
            ].sum()
        )
    else:
        total_shared_pv_kwh = 0.0

    # --------------------------------------------------------
    # HOUSE-LEVEL TECHNICAL METRICS
    # --------------------------------------------------------

    total_pv_curtailment_kwh = 0.0
    total_battery_charge_kwh = 0.0
    total_battery_discharge_kwh = 0.0

    export_limit_active_timesteps = 0

    for house_name, house_log in (
        simulation.house_results_log.items()
    ):

        house_df = pd.DataFrame(
            house_log
        )

        if "pv_curtailment_kw" in house_df.columns:
            total_pv_curtailment_kwh += (
                house_df["pv_curtailment_kw"].sum()
                * simulation.timestep_hours
            )

        if "battery_charge_kw" in house_df.columns:
            total_battery_charge_kwh += (
                house_df["battery_charge_kw"].sum()
                * simulation.timestep_hours
            )

        if "battery_discharge_kw" in house_df.columns:
            total_battery_discharge_kwh += (
                house_df["battery_discharge_kw"].sum()
                * simulation.timestep_hours
            )


        if "export_limit_active" in house_df.columns:
            export_limit_active_timesteps += int(
                house_df[
                    "export_limit_active"
                ].sum()
            )

    # --------------------------------------------------------
    # VALIDATION METRICS
    # --------------------------------------------------------

    if "Shared_PV_balance_error_kw" in summary_df.columns:
        max_shared_pv_balance_error_kw = (
            summary_df[
                "Shared_PV_balance_error_kw"
            ].abs().max()
        )
    else:
        max_shared_pv_balance_error_kw = 0.0

    if "VPP_power_balance_error_kw" in summary_df.columns:
        max_vpp_power_balance_error_kw = (
            summary_df[
                "VPP_power_balance_error_kw"
            ].abs().max()
        )
    else:
        max_vpp_power_balance_error_kw = 0.0

    return {
        "Scenario":
            scenario_name,

        "Cumulative Import Cost ($)":
            cumulative_import_cost,

        "Cumulative Export Revenue ($)":
            cumulative_export_revenue,

        "Cumulative Net Cost ($)":
            cumulative_net_cost,

        "Total Import Energy (kWh)":
            total_import_energy_kwh,

        "Total Export Energy (kWh)":
            total_export_energy_kwh,

        "Effective Export Value (c/kWh)":
            effective_export_value_c_per_kwh,

        "Total Shared PV (kWh)":
            total_shared_pv_kwh,

        "Total PV Curtailment (kWh)":
            total_pv_curtailment_kwh,

        "Battery Charge Energy (kWh)":
            total_battery_charge_kwh,

        "Battery Discharge Energy (kWh)":
            total_battery_discharge_kwh,


        "Export Limit Active Count":
            export_limit_active_timesteps,

        "Max Shared PV Balance Error (kW)":
            max_shared_pv_balance_error_kw,

        "Max VPP Power Balance Error (kW)":
            max_vpp_power_balance_error_kw,
    }


def build_monthly_house_metrics(
    simulation,
    start_date="2026-01-01"
):
    monthly_metrics = {}

    for house_name, house_log in (
        simulation.house_results_log.items()
    ):

        house_df = pd.DataFrame(
            house_log
        ).copy()

        house_df["timestamp"] = (
            pd.to_datetime(start_date)
            + pd.to_timedelta(
                house_df.index
                * simulation.timestep_hours,
                unit="h"
            )
        )

        house_df["month"] = (
            house_df["timestamp"]
            .dt.to_period("M")
            .astype(str)
        )

        for month, month_df in house_df.groupby(
            "month"
        ):

            if month not in monthly_metrics:
                monthly_metrics[month] = {
                    "PV Curtailment (kWh)": 0.0,
                    "Battery Charge Energy (kWh)": 0.0,
                    "Battery Discharge Energy (kWh)": 0.0,
                    "Export Limit Active Count": 0,
                }

            monthly_metrics[month][
                "PV Curtailment (kWh)"
            ] += (
                month_df[
                    "pv_curtailment_kw"
                ].sum()
                * simulation.timestep_hours
            )

            monthly_metrics[month][
                "Battery Charge Energy (kWh)"
            ] += (
                month_df[
                    "battery_charge_kw"
                ].sum()
                * simulation.timestep_hours
            )

            monthly_metrics[month][
                "Battery Discharge Energy (kWh)"
            ] += (
                month_df[
                    "battery_discharge_kw"
                ].sum()
                * simulation.timestep_hours
            )

            monthly_metrics[month][
                "Export Limit Active Count"
            ] += int(
                month_df[
                    "export_limit_active"
                ].sum()
            )

    return monthly_metrics

def build_monthly_summary(
    simulation,
    start_date="2026-01-01"
):
    summary_df = pd.DataFrame(
        simulation.simulation_results_summary
    ).copy()

    summary_df["timestamp"] = (
        pd.to_datetime(start_date)
        + pd.to_timedelta(
            summary_df["Simulation_step"]
            * simulation.timestep_hours,
            unit="h"
        )
    )

    summary_df["month"] = (
        summary_df["timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    house_metrics = build_monthly_house_metrics(
        simulation,
        start_date=start_date
    )

    monthly_rows = []

    for month, month_df in summary_df.groupby(
        "month"
    ):

        technical = house_metrics.get(
            month,
            {}
        )
        
        monthly_export_energy_kwh = (
            month_df[
                "VPP_export_energy_kwh"
            ].sum()
        )
        
        monthly_export_revenue = (
            month_df[
                "VPP_export_revenue"
            ].sum()
        )
        
        if monthly_export_energy_kwh > 0:
            effective_export_value = (
                monthly_export_revenue
                / monthly_export_energy_kwh
                * 100
            )
        else:
            effective_export_value = 0.0
        row = {
            "Month": month,

            "Import Energy (kWh)":
                month_df[
                    "VPP_import_energy_kwh"
                ].sum(),
            
            "Export Energy (kWh)":
                monthly_export_energy_kwh,

            "Import Cost ($)":
                month_df[
                    "VPP_import_cost"
                ].sum(),

            "Export Revenue ($)":
                monthly_export_revenue,
            
            "Net Cost ($)":
                month_df[
                    "VPP_net_cost"
                ].sum(),

            "Effective Export Value (c/kWh)":
                effective_export_value,

            "Shared PV (kWh)":
                month_df.get(
                    "VPP_shared_pv_received_kwh",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum(),

            "PV Curtailment (kWh)":
                technical.get(
                    "PV Curtailment (kWh)",
                    0.0
                ),

            "Battery Charge Energy (kWh)":
                technical.get(
                    "Battery Charge Energy (kWh)",
                    0.0
                ),

            "Battery Discharge Energy (kWh)":
                technical.get(
                    "Battery Discharge Energy (kWh)",
                    0.0
                ),

            "Export Limit Active Count":
                technical.get(
                    "Export Limit Active Count",
                    0
                ),
        }

        monthly_rows.append(row)

    monthly_df = pd.DataFrame(
        monthly_rows
    )

    return monthly_df.round(3)
    
def prepare_monthly_house_export(
    house_log,
    timestep_hours,
    start_date
):
    house_df = pd.DataFrame(
        house_log
    ).copy()

    house_df["timestamp"] = (
        pd.to_datetime(start_date)
        + pd.to_timedelta(
            house_df.index
            * timestep_hours,
            unit="h"
        )
    )

    house_df["month"] = (
        house_df["timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_rows = []

    for month, month_df in house_df.groupby(
        "month"
    ):

        row = {
            "Month": month,

            "Load Energy (kWh)":
                month_df.get(
                    "load_kw",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum()
                * timestep_hours,

            "Available PV Energy (kWh)":
                month_df.get(
                    "available_generation_kw",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum()
                * timestep_hours,

            "PV Generation Energy (kWh)":
                month_df.get(
                    "generation_kw",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum()
                * timestep_hours,

            "PV Curtailment Energy (kWh)":
                month_df.get(
                    "pv_curtailment_kw",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum()
                * timestep_hours,

            "Battery Charge Energy (kWh)":
                month_df.get(
                    "battery_charge_kw",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum()
                * timestep_hours,

            "Battery Discharge Energy (kWh)":
                month_df.get(
                    "battery_discharge_kw",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum()
                * timestep_hours,

            "Shared PV Received (kWh)":
                month_df.get(
                    "shared_pv_received_kwh",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum(),

            "Shared PV Supplied (kWh)":
                month_df.get(
                    "shared_pv_supplied_kwh",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum(),

            "External Grid Import (kWh)":
                month_df.get(
                    "external_grid_import_kwh",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum(),

            "External Grid Export (kWh)":
                month_df.get(
                    "external_grid_export_kwh",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum(),

            "Import Cost ($)":
                month_df.get(
                    "import_cost",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum(),

            "Export Revenue ($)":
                month_df.get(
                    "export_revenue",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum(),

            "Net Cost ($)":
                month_df.get(
                    "net_cost",
                    pd.Series(
                        0.0,
                        index=month_df.index
                    )
                ).sum(),

            "Export Limit Active Count":
                int(
                    month_df.get(
                        "export_limit_active",
                        pd.Series(
                            0,
                            index=month_df.index
                        )
                    ).sum()
                ),

            "Export Limit Active Hours":
                month_df.get(
                    "export_limit_active",
                    pd.Series(
                        0,
                        index=month_df.index
                    )
                ).sum()
                * timestep_hours,
        }

        monthly_rows.append(
            row
        )

    return pd.DataFrame(
        monthly_rows
    ).round(3)


def export_comparison_results(
    coordinated_simulation,
    independent_dynamic_simulation,
    independent_fixed_simulation,
    case_name="comparison",
    results_directory="results",
    start_date="2026-01-01",
    run_type="weekly"
):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M"
    )

    safe_case_name = (
        case_name
        .strip()
        .replace(" ", "_")
        .replace("/", "-")
    )
    
    filename = (
        f"{safe_case_name}_"
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
    
    if run_type == "weekly":
    
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
    
    elif run_type == "yearly":
    
        coordinated_summary_df = (
            build_monthly_summary(
                coordinated_simulation,
                start_date=start_date
            )
        )
    
        independent_dynamic_summary_df = (
            build_monthly_summary(
                independent_dynamic_simulation,
                start_date=start_date
            )
        )
    
        independent_fixed_summary_df = (
            build_monthly_summary(
                independent_fixed_simulation,
                start_date=start_date
            )
        )
    
    else:
    
        raise ValueError(
            f"Unsupported run_type: {run_type}"
        )



    comparison_df = pd.DataFrame([
        build_scenario_metrics(
            coordinated_simulation,
            "Coordinated VPP"
        ),
    
        build_scenario_metrics(
            independent_dynamic_simulation,
            "Independent Dynamic"
        ),
    
        build_scenario_metrics(
            independent_fixed_simulation,
            "Independent Fixed 5 kW/phase"
        ),
    ])

    with pd.ExcelWriter(
        filepath,
        engine="openpyxl"
    ) as writer:


        # ------------------------------------------
        # Comparison - Sheet 1
        # ------------------------------------------
    
        comparison_df.round(3).to_excel(
            writer,
            sheet_name="Comparison",
            index=False
        )
        

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

            if run_type == "weekly":

                house_df = prepare_house_export(
                    house_log
                )
            
            elif run_type == "yearly":
            
                house_df = prepare_monthly_house_export(
                    house_log=house_log,
                    timestep_hours=(
                        coordinated_simulation
                        .timestep_hours
                    ),
                    start_date=start_date
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

            if run_type == "weekly":
            
                house_df = prepare_house_export(
                    house_log
                )
            
            elif run_type == "yearly":
            
                house_df = (
                    prepare_monthly_house_export(
                        house_log=house_log,
                        timestep_hours=(
                            independent_dynamic_simulation
                            .timestep_hours
                        ),
                        start_date=start_date
                    )
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

            if run_type == "weekly":
            
                house_df = prepare_house_export(
                    house_log
                )
            
            elif run_type == "yearly":
            
                house_df = (
                    prepare_monthly_house_export(
                        house_log=house_log,
                        timestep_hours=(
                            independent_fixed_simulation
                            .timestep_hours
                        ),
                        start_date=start_date
                    )
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

    return filepath