import numpy as np


def create_daily_dynamic_envelope(
    timestep_hours=0.5,
    default_limit_kw_per_phase=10.0,
    periods=None
):
    """
    Create a 24-hour dynamic export envelope.

    periods should be a list of dictionaries with:
        start_hour
        end_hour
        limit_kw_per_phase
    """

    steps_per_day = int(
        24 / timestep_hours
    )

    profile = np.full(
        steps_per_day,
        default_limit_kw_per_phase,
        dtype=float
    )

    if periods is None:
        return profile

    for period in periods:

        start_step = int(
            period["start_hour"]
            / timestep_hours
        )

        end_step = int(
            period["end_hour"]
            / timestep_hours
        )

        profile[
            start_step:end_step
        ] = period["limit_kw_per_phase"]

    return profile


def create_dynamic_envelopes(
    timestep_hours=0.5
):

    default_10kw = (
        create_daily_dynamic_envelope(
            timestep_hours=timestep_hours,
            default_limit_kw_per_phase=10,
            periods=[]
        )
    )

    default_5kw = (
        create_daily_dynamic_envelope(
            timestep_hours=timestep_hours,
            default_limit_kw_per_phase=5,
            periods=[]
        )
    )
    
    mild_dynamic_envelope = (
        create_daily_dynamic_envelope(
            timestep_hours=timestep_hours,
            default_limit_kw_per_phase=10.0,
            periods=[
                {
                    "start_hour": 10.0,
                    "end_hour": 14.0,
                    "limit_kw_per_phase": 5.0,
                },
            ]
        )
    )

    moderate_dynamic_envelope = (
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
                    "end_hour": 15.0,
                    "limit_kw_per_phase": 3.0,
                },
            ]
        )
    )

    aggressive_dynamic_envelope = (
        create_daily_dynamic_envelope(
            timestep_hours=timestep_hours,
            default_limit_kw_per_phase=10.0,
            periods=[
                {
                    "start_hour": 6.0,
                    "end_hour": 9.0,
                    "limit_kw_per_phase": 6.0,
                },
                {
                    "start_hour": 9.0,
                    "end_hour": 15.0,
                    "limit_kw_per_phase": 1.5,
                },
            ]
        )
    )

    return {
        "default10kw" : default_10kw,
        "default5kw" : default_5kw,
        "mild": mild_dynamic_envelope,
        "moderate": moderate_dynamic_envelope,
        "aggressive": aggressive_dynamic_envelope,
    }


def expand_envelopes_to_length(
    envelope_dict,
    num_steps
):
    expanded = {}

    for name, daily_profile in (
        envelope_dict.items()
    ):

        repeat_count = int(
            np.ceil(
                num_steps
                / len(daily_profile)
            )
        )

        expanded[name] = np.tile(
            daily_profile,
            repeat_count
        )[:num_steps]

    return expanded