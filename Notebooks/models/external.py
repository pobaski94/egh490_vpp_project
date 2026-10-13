# ============================================================
# EXTERNAL LOCAL LOAD MODEL
# ============================================================

class LocalLoad:
    """
    Represents an electrical load located outside the VPP
    participant boundary.

    In the current demonstrator this object represents the
    hospital load.

    The load contributes to the wider demonstration/network
    power balance but is not a participating VPP asset and is
    therefore not directly controlled by the VPP controller.

    The model uses a time-series demand profile so the external
    load can later be expanded without changing the main
    simulation architecture.
    """

    def __init__(
        self,
        name,
        demand_kw
    ):

        # Descriptive name used in simulation results.
        self.name = name

        # Time-series external demand profile in kW.
        self.demand_kw = demand_kw


    def step(self, t):
        """
        Return the external load demand for the current
        simulation timestep.
        """

        return {
            "name": self.name,
            "load_kw": self.demand_kw[t]
        }
# ============================================================
# EXTERNAL WIND GENERATION MODEL
# ============================================================

class WindTurbine:
    """
    Represents the external wind/DFIG generation element used
    by the physical demonstrator.

    Wind generation is outside the five-house VPP boundary.
    It contributes only to the wider demonstration/network
    power balance.

    The current model uses a predefined generation profile.
    More detailed wind-speed, turbine or DFIG behaviour can be
    added later if required by the demonstrator scope.
    """

    def __init__(
        self,
        name,
        generation_profile
    ):

        # Descriptive name used in simulation results.
        self.name = name

        # Time-series wind generation profile in kW.
        self.generation_profile = (
            generation_profile
        )


    def step(self, t):
        """
        Return external wind generation for the current
        simulation timestep.
        """

        return {
            "name": self.name,
            "generation_kw":
                self.generation_profile[t]
        }

