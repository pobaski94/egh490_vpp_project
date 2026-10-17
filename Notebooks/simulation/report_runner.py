# ============================================================
# REPORT SIMULATION RUNNER
# ============================================================
import pandas as pd

from scenarios.scenario_setup import (
    create_coordinated_vpp_scenario,
    create_independent_dynamic_scenario,
    create_independent_fixed_scenario,
    COORDINATED_INPUTS,
    INDEPENDENT_INPUTS,
)

from simulation.results_export import (
    export_comparison_results
)


def build_timestep_inputs(
    base_inputs,
    step,
    timestep_hours,
    events=None
):
    """
    Build the external-input dictionary for one simulation
    timestep.

    base_inputs:
        Normal scenario operating configuration.

    events:
        Optional list of temporary event dictionaries.
    """

    inputs = base_inputs.copy()

    # Explicit defaults for normal report operation.
    inputs.setdefault(
        "network_support_request",
        False
    )

    inputs.setdefault(
        "requested_support_kw",
        0.0
    )

    inputs.setdefault(
        "vpp_tariff_event",
        False
    )

    if events is None:
        events = []

    # Apply any event active during the current timestep.
    for event in events:

        start_step = int(
            (
                ((event["day"] - 1) * 24)
                + event["hour"]
            )
            / timestep_hours
        )

        duration_steps = int(
            event["duration_hours"]
            / timestep_hours
        )

        end_step = (
            start_step
            + duration_steps
        )

        if (
            start_step
            <= step
            < end_step
        ):
            inputs.update(
                event.get(
                    "overrides",
                    {}
                )
            )

    return inputs


def run_report_case(
    case_name,
    report_days,
    house_loads,
    house_pv,
    dynamic_export_profile_kw_per_phase,
    hospital_load_profile,
    wind_generation_profile,
    timestep_hours,
    num_steps,
    tariff,
    start_date,
    run_type="weekly",
    fixed_export_limit_kw_per_phase=5.0,
    coordinated_events=None,
    export_results=True
):
    """
    Run one complete three-scenario report comparison.

    Scenarios:
        1. Coordinated VPP + dynamic envelope
        2. Independent houses + dynamic envelope
        3. Independent houses + fixed export limit
    """

    # --------------------------------------------------------
    # CREATE FRESH SIMULATIONS
    # --------------------------------------------------------

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
            tariff=tariff
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
            tariff=tariff
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
            tariff=tariff,
            fixed_export_limit_kw_per_phase=(
                fixed_export_limit_kw_per_phase
            )
        )
    )

    # --------------------------------------------------------
    # SIMULATION LENGTH
    # --------------------------------------------------------

    report_steps = int(
        report_days
        * 24
        / timestep_hours
    )

    steps_per_day = int(
        24
        / timestep_hours
    )

    print(
        f"\nRunning case: {case_name}"
    )

    print(
        f"Duration: {report_days} days "
        f"({report_steps} timesteps)"
    )

    # --------------------------------------------------------
    # RUN SIMULATION
    # --------------------------------------------------------

    for step in range(report_steps):

        coordinated_inputs = (
            build_timestep_inputs(
                base_inputs=COORDINATED_INPUTS,
                step=step,
                timestep_hours=timestep_hours,
                events=coordinated_events
            )
        )

        independent_inputs = (
            build_timestep_inputs(
                base_inputs=INDEPENDENT_INPUTS,
                step=step,
                timestep_hours=timestep_hours
            )
        )

        coordinated_simulation.step(
            coordinated_inputs
        )

        independent_dynamic_simulation.step(
            independent_inputs
        )

        independent_fixed_simulation.step(
            independent_inputs
        )

        # Print one progress update per simulated day or month based on run type selected.
        if run_type == "weekly":
            
            if (
                (step + 1)
                % steps_per_day == 0
            ):
    
                completed_days = (
                    (step + 1)
                    // steps_per_day
                )
    
                print(
                    f"Completed "
                    f"{completed_days}/"
                    f"{report_days} days"
                )
        
        elif run_type == "yearly":
        
            current_timestamp = (
                pd.to_datetime(start_date)
                + pd.to_timedelta(
                    step * timestep_hours,
                    unit="h"
                )
            )
        
            next_timestamp = (
                pd.to_datetime(start_date)
                + pd.to_timedelta(
                    (step + 1) * timestep_hours,
                    unit="h"
                )
            )
        
            if (
                current_timestamp.month
                != next_timestamp.month
            ):
        
                print(
                    f"Completed month: "
                    f"{current_timestamp.strftime('%B')}"
                )
                
    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------

    filepath = None

    if export_results:

        filepath = export_comparison_results(
            coordinated_simulation=(
                coordinated_simulation
            ),
            independent_dynamic_simulation=(
                independent_dynamic_simulation
            ),
            independent_fixed_simulation=(
                independent_fixed_simulation
            ),
            case_name=case_name,
            start_date=start_date,
            run_type=run_type
        )

        print(
            f"Results exported to:\n"
            f"{filepath}"
        )

    print(
        f"Completed case: {case_name}\n"
    )

    return {
        "case_name":
            case_name,

        "coordinated":
            coordinated_simulation,

        "independent_dynamic":
            independent_dynamic_simulation,

        "independent_fixed":
            independent_fixed_simulation,

        "filepath":
            filepath,
    }

def run_report_batch(
    case_prefix,
    envelope_cases,
    report_days,
    house_loads,
    house_pv,
    hospital_load_profile,
    wind_generation_profile,
    timestep_hours,
    num_steps,
    tariff,
    start_date,
    run_type="yearly",
    coordinated_events=None,
    fixed_export_limit_kw_per_phase=5.0,
    export_results=True
):
    """
    Run multiple report cases sequentially.

    envelope_cases should be a dictionary like:

    {
        "default10kw": profile,
        "default5kw": profile,
        "mild": profile,
        "moderate": profile,
        "aggressive": profile,
    }
    """

    batch_results = {}

    total_cases = len(
        envelope_cases
    )

    for case_number, (
        envelope_name,
        envelope_profile
    ) in enumerate(
        envelope_cases.items(),
        start=1
    ):

        case_name = (
            f"{case_prefix}_"
            f"{envelope_name}"
        )

        print(
            "\n"
            "=================================================="
        )

        print(
            f"Running case "
            f"{case_number}/{total_cases}: "
            f"{case_name}"
        )

        print(
            "=================================================="
        )

        results = run_report_case(
            case_name=case_name,
            report_days=report_days,
            house_loads=house_loads,
            house_pv=house_pv,
            dynamic_export_profile_kw_per_phase=(
                envelope_profile
            ),
            hospital_load_profile=(
                hospital_load_profile
            ),
            wind_generation_profile=(
                wind_generation_profile
            ),
            timestep_hours=timestep_hours,
            num_steps=num_steps,
            tariff=tariff,
            start_date=start_date,
            run_type=run_type,
            fixed_export_limit_kw_per_phase=(
                fixed_export_limit_kw_per_phase
            ),
            coordinated_events=(
                coordinated_events
            ),
            export_results=export_results
        )

        batch_results[
            envelope_name
        ] = results

    print(
        "\nAll batch cases completed."
    )

    return batch_results