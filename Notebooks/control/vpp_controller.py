# ============================================================
# VPP SUPERVISORY CONTROLLER
# ============================================================

class VPPController:
    """
    Supervisory controller for the five-house residential VPP.

    The controller does not directly modify battery SOC or final
    premises power flows. Instead, it:

        1. evaluates the current aggregate VPP state,
        2. selects the active VPP operating mode,
        3. allocates network-support battery targets,
        4. coordinates available surplus PV between houses, and
        5. returns supervisory signals to each House object.

    House and Battery objects remain responsible for enforcing
    physical DER and connection-point constraints.

    Current operating priority:
        1. explicit network-support request,
        2. manual/test override,
        3. scheduled cheap-energy charging,
        4. scheduled peak shaving,
        5. grid-import-limit response,
        6. normal/default operation.

    PV sharing is treated as a secondary VPP action rather than
    a standalone operating mode.
    """

    def __init__(
        self,
        default_mode="self_consumption",
        peak_hours=None,
        cheap_energy_hours=None,
        grid_import_limit_kw=None,
        economic_export_reserve_percent=0
    ):

        # Normal operating mode when no higher-priority
        # supervisory action is required.
        self.default_mode = default_mode

        # Time periods during which scheduled peak-shaving
        # behaviour may be enabled.
        self.peak_hours = peak_hours or []

        # Time periods during which the current placeholder
        # arbitrage strategy may charge batteries from the grid.
        self.cheap_energy_hours = (
            cheap_energy_hours or []
        )

        # Optional aggregate VPP import threshold.
        # If exceeded, the controller can activate peak shaving.
        self.grid_import_limit_kw = (
            grid_import_limit_kw
        )

        self.economic_export_reserve_percent = (
            economic_export_reserve_percent
        )
        
    def get_signals(
        self,
        t,
        external_inputs=None,
        house_states=None
    ):
        """
        Evaluate the current VPP state and generate supervisory
        control signals for one simulation timestep.

        Parameters
        ----------
        t:
            Current simulation hour-of-day.

        external_inputs:
            External supervisory commands such as network-support,
            PV-sharing, peak-shaving or manual-mode requests.

        house_states:
            Pre-control state and available flexibility reported
            by each participating House object.
        """

        if external_inputs is None:
            external_inputs = {}

        if house_states is None:
            house_states = []


        # ----------------------------------------------------
        # AGGREGATE PRE-CONTROL VPP STATE
        # ----------------------------------------------------
        #
        # The VPP consists only of the five participating houses
        # and their DERs. Hospital and wind/DFIG resources are
        # external to this controller boundary.

        # Aggregate premises power before battery dispatch.
        #
        # Positive = net VPP grid import.
        # Negative = net VPP grid export.
        total_house_net_before_battery_kw = sum(
            state["net_power_kw_before_battery"]
            for state in house_states
        )

        vpp_net_power_before_battery_kw = (
            total_house_net_before_battery_kw
        )

        vpp_grid_import_before_battery_kw = max(
            vpp_net_power_before_battery_kw,
            0.0
        )


        # ----------------------------------------------------
        # AGGREGATE PV-SHARING FLEXIBILITY
        # ----------------------------------------------------

        # Genuine surplus PV remaining after source houses have
        # satisfied their own demand and local battery capability.
        total_shared_pv_available_kw = sum(
            state["shared_pv_available_kw"]
            for state in house_states
        )

        # Total ability of participating houses to receive shared
        # PV through either unmet demand or available battery
        # charging capability.
        total_shared_pv_receiving_capacity_kw = sum(
            state["shared_pv_receiving_capacity_kw"]
            for state in house_states
        )

        

        # ----------------------------------------------------
        # EXTERNAL SUPERVISORY INPUTS
        # ----------------------------------------------------

        # Explicit request for the VPP to provide network support.
        network_support_request = external_inputs.get(
            "network_support_request",
            False
        )

        # Aggregate battery support power requested from the VPP.
        requested_support_kw = external_inputs.get(
            "requested_support_kw",
            0.0
        )

        # Enables scheduled peak-shaving behaviour.
        peak_shaving_enabled = external_inputs.get(
            "peak_shaving_enabled",
            False
        )

        # Enables secondary VPP surplus-PV sharing.
        pv_sharing_enabled = external_inputs.get(
            "pv_sharing_enabled",
            False
        )

        # Direct operating-mode override retained for testing
        # and physical demonstrator development.
        manual_mode = external_inputs.get(
            "manual_mode"
        )

        # Enables deliberate battery export during the
        # configured high-value peak period.
        economic_export_enabled = external_inputs.get(
            "economic_export_enabled",
            False
        )

        # ----------------------------------------------------
        # INITIALISE HOUSE-LEVEL CONTROL TARGETS
        # ----------------------------------------------------

        # Battery discharge targets used during explicit
        # network-support operation.
        house_dispatch_targets = {}

        # Shared PV allocated to receiving VPP houses.
        house_shared_pv_targets = {}

        # A09:
        # Shared-PV export attributed back to the VPP houses
        # supplying the transferred surplus energy.
        house_shared_export_targets = {} 
        
        # Aggregate battery discharge capability currently
        # available to the VPP after physical battery and
        # connection constraints reported by each house.
        total_available_discharge_kw = sum(
            state["vpp_available_discharge_kw"]
            for state in house_states
        )
        
        # ====================================================
        # PRIMARY VPP OPERATING-MODE SELECTION
        # ====================================================
        #
        # Higher-priority conditions are evaluated first.
        # Only one primary operating mode is selected for the
        # current timestep.


        # ----------------------------------------------------
        # PRIORITY 1 - EXPLICIT NETWORK SUPPORT
        # ----------------------------------------------------

        if network_support_request:

            active_mode = "network_support"

            # Select battery-equipped houses that currently have
            # usable VPP discharge capability.
            available_houses = [
                state
                for state in house_states
                if state["has_battery"]
                and state["vpp_available_discharge_kw"] > 0
            ]

            # Remaining aggregate support request that has not yet
            # been allocated among participating batteries.
            remaining_support_kw = (
                requested_support_kw
            )

            # Iteratively divide the remaining request equally
            # between houses that still have discharge capacity.
            #
            # If one house reaches its available limit, its unused
            # share is redistributed among the remaining houses.
            while (
                available_houses
                and remaining_support_kw > 0
            ):

                equal_share_kw = (
                    remaining_support_kw
                    / len(available_houses)
                )

                still_available_houses = []

                for state in available_houses:

                    house_name = state["name"]

                    available_kw = state[
                        "vpp_available_discharge_kw"
                    ]

                    # Support already allocated to this house
                    # during a previous redistribution pass.
                    already_dispatched_kw = (
                        house_dispatch_targets.get(
                            house_name,
                            0.0
                        )
                    )

                    remaining_house_capacity_kw = (
                        available_kw
                        - already_dispatched_kw
                    )

                    dispatch_kw = min(
                        equal_share_kw,
                        remaining_house_capacity_kw
                    )

                    house_dispatch_targets[house_name] = (
                        already_dispatched_kw
                        + dispatch_kw
                    )

                    remaining_support_kw -= dispatch_kw
                    remaining_house_capacity_kw -= dispatch_kw

                    # Retain houses that can accept another share
                    # during the next redistribution pass.
                    if remaining_house_capacity_kw > 0:
                        still_available_houses.append(
                            state
                        )

                available_houses = (
                    still_available_houses
                )
                
       
        # ----------------------------------------------------
        # PRIORITY 2 - MANUAL / TEST OVERRIDE
        # ----------------------------------------------------

        elif manual_mode is not None:
            active_mode = manual_mode


        # ----------------------------------------------------
        # PRIORITY 3 - CHEAP-ENERGY CHARGING
        # ----------------------------------------------------
        #
        # Current placeholder for later tariff/economic
        # optimisation.

        elif t in self.cheap_energy_hours:
            active_mode = "arbitrage_charge"
        
        # ----------------------------------------------------
        # PRIORITY 4 - ECONOMIC PEAK EXPORT
        # ----------------------------------------------------
        
        elif (
            economic_export_enabled
            and t in self.peak_hours
        ):
            active_mode = "economic_export"

        
        # ----------------------------------------------------
        # PRIORITY 5 - SCHEDULED PEAK SHAVING
        # ----------------------------------------------------

        elif peak_shaving_enabled:
           
            active_mode = "peak_shaving"



        # ----------------------------------------------------
        # PRIORITY 6 - VPP IMPORT-LIMIT RESPONSE
        # ----------------------------------------------------

        elif (
            self.grid_import_limit_kw is not None
            and vpp_grid_import_before_battery_kw
            > self.grid_import_limit_kw
        ):
            active_mode = "peak_shaving"


        # ----------------------------------------------------
        # PRIORITY 7 - NORMAL VPP OPERATION
        # ----------------------------------------------------

        else:
            active_mode = self.default_mode

            
        # ====================================================
        # SECONDARY VPP ACTION - SURPLUS PV SHARING
        # ====================================================
        #
        # PV sharing is independent of the primary operating-mode
        # selection and is therefore treated as a secondary action.
        #
        # Sharing is currently permitted during normal
        # self-consumption and non-active peak-shaving operation,
        # but is disabled during explicit peak periods.

        shared_pv_transfer_allowed = (
            pv_sharing_enabled
            and active_mode in [
                "self_consumption",
                "peak_shaving"
            ]
            and not (
                peak_shaving_enabled
                and t in self.peak_hours
            )
        )
            
        if (
            shared_pv_transfer_allowed
            and total_shared_pv_available_kw > 0
            and total_shared_pv_receiving_capacity_kw > 0
        ):

            # Select every participating house that can currently
            # receive shared PV through unmet household demand,
            # battery charging capacity, or both.
            available_houses = [
                state
                for state in house_states
                if state[
                    "shared_pv_receiving_capacity_kw"
                ] > 0
            ]

            remaining_shared_pv_kw = (
                total_shared_pv_available_kw
            )

            # Allocate available shared PV equally between
            # receiving houses, redistributing unused shares when
            # an individual house reaches its receiving capacity.
            while (
                available_houses
                and remaining_shared_pv_kw > 0
            ):

                equal_share_kw = (
                    remaining_shared_pv_kw
                    / len(available_houses)
                )

                still_available_houses = []

                for state in available_houses:

                    house_name = state["name"]

                    available_kw = state[
                        "shared_pv_receiving_capacity_kw"
                    ]

                    already_allocated_kw = (
                        house_shared_pv_targets.get(
                            house_name,
                            0.0
                        )
                    )

                    remaining_house_capacity_kw = (
                        available_kw
                        - already_allocated_kw
                    )

                    # Shared-PV allocation may serve either
                    # household demand or battery charging.
                    allocation_kw = min(
                        equal_share_kw,
                        remaining_house_capacity_kw
                    )

                    house_shared_pv_targets[
                        house_name
                    ] = (
                        already_allocated_kw
                        + allocation_kw
                    )

                    remaining_shared_pv_kw -= (
                        allocation_kw
                    )

                    remaining_house_capacity_kw -= (
                        allocation_kw
                    )

                    if remaining_house_capacity_kw > 0:
                        still_available_houses.append(
                            state
                        )

                available_houses = (
                    still_available_houses
                ) 

        # ====================================================
        # A09 - ACTUAL SHARED-PV TRANSFER
        # ====================================================

        # Total PV actually allocated to receiving VPP houses.
        # This may be lower than the total PV available for sharing
        # if receiving demand/storage capacity is insufficient.
        total_shared_pv_transferred_kw = sum(
            house_shared_pv_targets.values()
        )


        # ----------------------------------------------------
        # ATTRIBUTE SHARED PV TO SOURCE HOUSES
        # ----------------------------------------------------
        #
        # Attribute the transferred energy back to houses with
        # genuine available PV surplus.
        #
        # These source targets are subsequently used by House.step()
        # when applying the A09 shared-PV-specific export allowance.

        remaining_shared_export_kw = (
            total_shared_pv_transferred_kw
        )

        for state in house_states:

            if remaining_shared_export_kw <= 0:
                break

            source_available_kw = state[
                "shared_pv_available_kw"
            ]

            if source_available_kw <= 0:
                continue

            source_export_kw = min(
                source_available_kw,
                remaining_shared_export_kw
            )

            house_shared_export_targets[
                state["name"]
            ] = source_export_kw

            remaining_shared_export_kw -= (
                source_export_kw
            )


        # ====================================================
        # RETURN SUPERVISORY CONTROL SIGNALS
        # ====================================================

        return {
            # Primary operating state
            "mode": active_mode,

            "is_peak_period":
                t in self.peak_hours,

            "is_grid_peak_limit_exceeded": (
                self.grid_import_limit_kw is not None
                and vpp_grid_import_before_battery_kw
                > self.grid_import_limit_kw
            ),

            "peak_shaving_enabled":
                peak_shaving_enabled,

            "pv_sharing_enabled":
                pv_sharing_enabled,
            "economic_export_enabled":
                economic_export_enabled,
            "economic_export_reserve_percent":
                self.economic_export_reserve_percent,

            # Network-support event state.
            "is_event_period":
                network_support_request,

            "is_cheap_energy_period":
                t in self.cheap_energy_hours,

            # Network-support request and house allocations
            "requested_support_kw":
                requested_support_kw,

            "house_dispatch_targets":
                house_dispatch_targets,

            # Aggregate pre-control VPP state
            "vpp_grid_import_before_battery_kw":
                vpp_grid_import_before_battery_kw,

            # Current VPP battery capability
            "total_available_discharge_kw":
                total_available_discharge_kw,

            # Shared-PV state
            "total_shared_pv_transferred_kw":
                total_shared_pv_transferred_kw,

            "total_shared_pv_available_kw":
                total_shared_pv_available_kw,

            "total_shared_pv_receiving_capacity_kw":
                total_shared_pv_receiving_capacity_kw,

            # House-level shared-PV allocations
            "house_shared_pv_targets":
                house_shared_pv_targets,

            "house_shared_export_targets":
                house_shared_export_targets,
        }
        
