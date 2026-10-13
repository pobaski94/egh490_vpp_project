# ============================================================
# RESIDENTIAL HOUSE / CONNECTION-POINT MODEL
# ============================================================

class House:
    """
    Represents one participating residential premises in the VPP.

    Each house may contain:
        - a household load profile,
        - a rooftop PV generation profile,
        - an optional battery energy storage system,
        - PV inverter metadata, and
        - a simplified grid connection/export constraint.

    The House object is responsible for enforcing local physical
    constraints after receiving supervisory targets from the
    VPP controller.

    Sign convention at the connection point:
        positive net power = grid import
        negative net power = grid export
    """

    def __init__(
        self,
        name,
        load_profile,
        generation_profile,
        battery=None,
        pv_array_kwp=0.0,
        pv_inverter_limit_kw=0.0,
        connection_type="single_phase",
        connection_phases=1,
        min_export_kw_per_phase=1.5,
        max_export_kw_per_phase=10.0,
        dynamic_export_profile_kw_per_phase=None
    ):

        self.name = name

        # Time-series profiles used by this premises.
        self.load_profile = load_profile
        self.generation_profile = generation_profile

        # Optional Battery object. A value of None represents
        # a participating house without battery storage.
        self.battery = battery

        # ----------------------------------------------------
        # PV SYSTEM METADATA
        # ----------------------------------------------------
        #
        # PV generation is supplied by the prepared SAM profile.
        # These ratings describe the installed system and are
        # retained for reporting rather than re-limiting the
        # imported AC generation profile here.
        self.pv_array_kwp = pv_array_kwp
        self.pv_inverter_limit_kw = pv_inverter_limit_kw

        # ----------------------------------------------------
        # GRID CONNECTION
        # ----------------------------------------------------

        self.connection_type = connection_type
        self.connection_phases = connection_phases

        self.min_export_kw_per_phase = (
            min_export_kw_per_phase
        )

        self.max_export_kw_per_phase = (
            max_export_kw_per_phase
        )
        

        # The simplified simulation uses aggregate connection
        # limits rather than modelling individual phase flows.
        self.min_export_limit_kw = (
            min_export_kw_per_phase
            * connection_phases
        )

        self.max_export_limit_kw = (
            max_export_kw_per_phase
            * connection_phases
        )

        # Optional time-varying dynamic export envelope.
        # None means the premises uses its maximum connection
        # capability as a constant export allowance.
        self.dynamic_export_profile_kw_per_phase = (
            dynamic_export_profile_kw_per_phase
        )

        # Normal dynamic export allowance applicable to the
        # premises. This can later be replaced by a time-varying
        # network/DNSP input.
        self.dynamic_export_limit_kw = (
            self.max_export_limit_kw
        )

        

        # Export limit currently applied to the premises.
        #
        # Under normal operation this equals the dynamic export
        # limit. A10 may temporarily increase it during an
        # explicit network-support event.
        self.current_export_limit_kw = (
            self.dynamic_export_limit_kw
        )
            
        
    def get_state(
        self,
        profile_index,
        timestep_hours
    ):
        """
        Determine the pre-control electrical state and available
        DER flexibility of this premises.

        This method does not dispatch the battery. It reports the
        quantities required by the VPP controller to make its
        supervisory decision for the current timestep.
        """

        # Current household demand and available PV generation
        # from the selected profile sample.
        load_kw = self.load_profile[profile_index]
        generation_kw = (
            self.generation_profile[profile_index]
        )

        # Connection-point power before any battery action.
        #
        # Positive = household deficit / potential grid import.
        # Negative = PV surplus / potential grid export.
        net_power_kw_before_battery = (
            load_kw - generation_kw
        )

        # Household demand that remains after using its own PV.
        local_import_kw = max(
            net_power_kw_before_battery,
            0.0
        )

        # PV remaining after satisfying this house's own load.
        local_pv_surplus_kw = max(
            -net_power_kw_before_battery,
            0.0
        )
        # A house without a battery can still receive shared PV
        # to offset its current household deficit.
        #
        # For battery-equipped houses this value is expanded
        # below to include remaining battery charging capability.
        shared_pv_receiving_capacity_kw = (
            local_import_kw
        )
        
        # Default values for houses without battery storage.
        battery_soc_kwh = None
        battery_soc_percent = None

        max_discharge_kw = 0.0
        max_charge_kw = 0.0

        available_discharge_kw = 0.0
        available_charge_kw = 0.0

        export_headroom_kw = 0.0
        vpp_available_discharge_kw = 0.0

        local_battery_charge_from_pv_kw = 0.0

        # Without a battery, all PV remaining after local demand
        # is potentially available for VPP sharing.
        shared_pv_available_kw = local_pv_surplus_kw

        vpp_available_charge_kw = 0.0
        
        

        if self.battery is not None:

            # Current physical battery state.
            battery_soc_kwh = (
                self.battery.get_soc_kwh()
            )

            battery_soc_percent = (
                self.battery.get_soc_percent()
            )

            max_discharge_kw = (
                self.battery.max_discharge_kw
            )

            max_charge_kw = (
                self.battery.max_charge_kw
            )

            # ------------------------------------------------
            # PHYSICAL BATTERY DISCHARGE CAPABILITY
            # ------------------------------------------------

            # Energy physically available above the battery's
            # minimum usable SOC.
            #
            # The future VPP operating reserve (e.g. 20% SOC)
            # will be a controller-level requirement and is
            # intentionally separate from this physical limit.
            available_energy_kwh = max(
                0.0,
                self.battery.soc_kwh
                - self.battery.min_soc_kwh
            )

            # Maximum discharge that can be sustained for the
            # complete simulation timestep, subject to both
            # stored energy and battery power capability.
            available_discharge_kw = min(
                self.battery.max_discharge_kw,
                available_energy_kwh
                * self.battery.efficiency
                / timestep_hours
            )

            # --------------------------------------------------
            # CONNECTION-CONSTRAINED VPP DISCHARGE CAPABILITY
            # ------------------------------------------------

            # PV export that would already exist without battery
            # discharge.
            export_before_battery_kw = max(
                -net_power_kw_before_battery,
                0.0
            )

            # Remaining export capacity under the CURRENT
            # connection limit.
            #
            # This deliberately does not use the A09 shared-PV
            # allowance. Any additional A09 export capacity is
            # reserved specifically for allocated shared PV and
            # must not create extra battery export capability.
            export_headroom_kw = max(
                self.current_export_limit_kw
                - export_before_battery_kw,
                0.0
            )

            # Battery discharge can:
            #   1. offset this house's existing grid import, then
            #   2. export through remaining connection headroom.
            connection_permitted_discharge_kw = (
                local_import_kw
                + export_headroom_kw
            )

            # VPP-visible discharge capability is therefore the
            # smaller of the physical battery capability and the
            # connection-permitted capability.
            vpp_available_discharge_kw = min(
                available_discharge_kw,
                connection_permitted_discharge_kw
            )
            
            # ------------------------------------------------
            # BATTERY CHARGING CAPABILITY
            # ------------------------------------------------

            # Remaining physical storage space.
            available_space_kwh = max(
                0.0,
                self.battery.capacity_kwh
                - self.battery.soc_kwh
            )

            # Maximum charging power that can be accepted for the
            # complete timestep without exceeding battery capacity.
            available_charge_kw = min(
                self.battery.max_charge_kw,
                available_space_kwh / (
                    timestep_hours
                    * self.battery.efficiency
                )
            )

            # Own surplus PV is allocated to the house's own
            # battery before that PV becomes available for
            # sharing with other VPP participants.
            local_battery_charge_from_pv_kw = min(
                local_pv_surplus_kw,
                available_charge_kw
            )

            # Genuine PV surplus remaining after:
            #   own household demand, then
            #   own battery charging capability.
            shared_pv_available_kw = max(
                local_pv_surplus_kw
                - local_battery_charge_from_pv_kw,
                0.0
            )

            # Battery charging capability remaining after allowing
            # for this house's own surplus PV.
            vpp_available_charge_kw = max(
                available_charge_kw
                - local_battery_charge_from_pv_kw,
                0.0
            )

            # Shared PV received from another participant can first
            # offset this house's unmet demand and can then use any
            # remaining battery charging capability.
            shared_pv_receiving_capacity_kw = (
                local_import_kw
                + vpp_available_charge_kw
            )

        return {
            # Identity and pre-control electrical state
            "name": self.name,
            "load_kw": load_kw,
            "generation_kw": generation_kw,
            "net_power_kw_before_battery":
                net_power_kw_before_battery,
            "local_import_kw": local_import_kw,

            # Battery presence and state
            "has_battery": self.battery is not None,
            "battery_soc_kwh": battery_soc_kwh,
            "battery_soc_percent": battery_soc_percent,

            # Physical battery capability
            "max_discharge_kw": max_discharge_kw,
            "max_charge_kw": max_charge_kw,
            "available_discharge_kw":
                available_discharge_kw,
            "available_charge_kw":
                available_charge_kw,

            # PV sharing capability
            "local_pv_surplus_kw":
                local_pv_surplus_kw,
            "local_battery_charge_from_pv_kw":
                local_battery_charge_from_pv_kw,
            "shared_pv_available_kw":
                shared_pv_available_kw,
            "vpp_available_charge_kw":
                vpp_available_charge_kw,
            "shared_pv_receiving_capacity_kw":
                shared_pv_receiving_capacity_kw,

            # Connection-constrained VPP capability
            "export_headroom_kw": export_headroom_kw,
            "vpp_available_discharge_kw":
                vpp_available_discharge_kw,

            # Installed PV and connection metadata
            "pv_array_kwp": self.pv_array_kwp,
            "pv_inverter_limit_kw":
                self.pv_inverter_limit_kw,

            "connection_type": self.connection_type,
            "connection_phases":
                self.connection_phases,

            "min_export_limit_kw":
                self.min_export_limit_kw,
            "max_export_limit_kw":
                self.max_export_limit_kw,

            "dynamic_export_limit_kw":
                self.dynamic_export_limit_kw,
            "current_export_limit_kw":
                self.current_export_limit_kw,
        }
            
    def update_export_limit(
        self,
        profile_index,
        network_support_request=False
    ):
        """
        Update the connection export limit applied to this house.
    
        Under normal operation, the premises is constrained by its
        current dynamic export limit.
    
        A10:
        During an explicit network-support event, the demonstrator
        assumes that additional network export capacity has been made
        available, allowing the premises to operate up to its modelled
        maximum connection export capability.
    
        This is a demonstrator scenario assumption and is separate
        from the A09 shared-PV-specific export allowance.
        """
    
        # ----------------------------------------------
        # UPDATE DYNAMIC EXPORT ENVELOPE
        # ----------------------------------------------
    
        if self.dynamic_export_profile_kw_per_phase is not None:
        
            envelope_kw_per_phase = max(
                self.dynamic_export_profile_kw_per_phase[
                    profile_index
                ],
                0.0
            )
        
            requested_dynamic_limit_kw = (
                envelope_kw_per_phase
                * self.connection_phases
            )
        
            self.dynamic_export_limit_kw = min(
                requested_dynamic_limit_kw,
                self.max_export_limit_kw
            )
        
        else:
        
            self.dynamic_export_limit_kw = (
                self.max_export_limit_kw
            )
    
        # ----------------------------------------------
        # APPLY NETWORK-SUPPORT OVERRIDE
        # ----------------------------------------------
    
        if network_support_request:
    
            self.current_export_limit_kw = (
                self.max_export_limit_kw
            )
    
        else:
    
            self.current_export_limit_kw = (
                self.dynamic_export_limit_kw
            )
  

        

    def step(
        self,
        t,
        timestep_hours,
        signals,
    ):
        """
        Execute one physical house timestep using the supervisory
        signals supplied by the VPP controller.

        The controller requests an operating behaviour, while this
        method applies that behaviour subject to the house's battery,
        PV and connection-point constraints.

        Battery power sign convention:
            positive = battery discharge
            negative = battery charge

        Connection-point sign convention:
            positive = grid import
            negative = grid export
        """

        # ----------------------------------------------------
        # CURRENT HOUSE ELECTRICAL STATE
        # ----------------------------------------------------

        # Retrieve household demand and available PV generation
        # for the current profile timestep.
        load_kw = self.load_profile[t]
        generation_kw = self.generation_profile[t]

        # Net premises power before battery action.
        #
        # Positive = household demand exceeds PV generation.
        # Negative = PV generation exceeds household demand.
        net_power_kw_bb = (
            load_kw - generation_kw
        )
        
        # ----------------------------------------------------
        # CONNECTION-POINT EXPORT LIMIT
        # ----------------------------------------------------

        # Current connection export limit applicable to normal
        # house operation.
        #
        # This normally equals the dynamic export limit, but may
        # already have been increased by A10 if an explicit
        # network-support event is active.
        current_export_limit_kw = (
            self.current_export_limit_kw
        )


        # ----------------------------------------------------
        # A09 - SHARED-PV-SPECIFIC EXPORT ALLOWANCE
        # ----------------------------------------------------

        # The controller may allocate genuine surplus PV from this
        # house to other participating VPP houses.
        shared_pv_export_target_kw = signals[
            "house_shared_export_targets"
        ].get(
            self.name,
            0.0
        )

        # A09:
        # If the allocated shared-PV export exceeds the normal
        # connection export allowance, the effective limit may be
        # temporarily increased only enough to accommodate that
        # shared-PV target.
        #
        # This additional allowance:
        #   - applies only when shared PV has been allocated,
        #   - cannot exceed the modelled maximum connection limit,
        #   - does NOT create additional battery export headroom.
        
        effective_export_limit_kw = min(
            max(
                current_export_limit_kw,
                shared_pv_export_target_kw
            ),
            self.max_export_limit_kw
        )
        
        # ----------------------------------------------------
        # NORMAL BATTERY EXPORT HEADROOM
        # ----------------------------------------------------

        # PV export that would already occur before battery action.
        export_before_battery_kw = max(
            -net_power_kw_bb,
            0.0
        )

        # Remaining connection capacity available for battery
        # export.
        #
        # Deliberately use current_export_limit_kw rather than
        # effective_export_limit_kw here. The additional A09
        # allowance is reserved for shared PV and must not increase
        # battery export capability.
        export_headroom_kw = max(
            current_export_limit_kw
            - export_before_battery_kw,
            0.0
        )

        # Quantities used later to record any restriction imposed
        # by the connection limit.
        battery_discharge_reduction_kw = 0.0
        pv_curtailment_kw = 0.0
        export_limit_active = False

        
        # ----------------------------------------------------
        # INITIALISE TIMESTEP BATTERY STATE
        # ----------------------------------------------------

        # Battery power remains zero for houses without storage
        # or whenever the active controller mode requests no
        # battery action.
        battery_power_kw = 0.0

        # Houses without batteries report zero SOC in the physical
        # timestep results used by the demonstrator and hardware
        # display.
        battery_soc_kwh = 0.0
        battery_soc_percent = 0.0
        
        
        # ----------------------------------------------------
        # BATTERY DISPATCH
        # ----------------------------------------------------

        
        if self.battery is not None:

            # Read the supervisory operating mode and supporting
            # controller flags for this timestep.
            mode = signals["mode"]

            is_peak_period = (
                signals["is_peak_period"]
            )

            is_grid_peak_limit_exceeded = (
                signals["is_grid_peak_limit_exceeded"]
            )


            is_cheap_energy_period = (
                signals["is_cheap_energy_period"]
            )

            
            
            # ------------------------------------------------
            # RECEIVED SHARED PV
            # ------------------------------------------------

            # Shared PV allocated to this house can first offset
            # its remaining household demand and can then create
            # surplus power available for battery charging.
            shared_pv_allocation_kw = signals[
                "house_shared_pv_targets"
            ].get(
                self.name,
                0.0
            )

            # Virtual net power used for battery dispatch after
            # accounting for the VPP-directed shared-PV allocation.
            #
            # The actual physical connection-point power is
            # calculated separately later in this method.
            effective_net_power_kw = (
                net_power_kw_bb
                - shared_pv_allocation_kw
            )


            # ------------------------------------------------
            # MODE: SELF CONSUMPTION
            # ------------------------------------------------
            #
            # Normal DER operation:
            #   - surplus energy charges the battery,
            #   - remaining household deficit is supplied by
            #     battery discharge where possible.
            if mode == "self_consumption":

                if effective_net_power_kw < 0:
                    # charge from remaining surplus
                    battery_power_kw = self.battery.charge(-effective_net_power_kw, timestep_hours)

            
                elif effective_net_power_kw > 0:
                    # discharge for remaining deficit
                    battery_power_kw = self.battery.discharge(effective_net_power_kw, timestep_hours)
                
                else: 
                    battery_power_kw = 0.0
            
            # ------------------------------------------------
            # MODE: BATTERY HOLD
            # ------------------------------------------------
            #
            # Preserve stored battery energy for a future
            # controller objective or higher-value period.
            elif mode == "battery_hold":
                battery_power_kw = 0.0

            # ------------------------------------------------
            # MODE: PEAK SHAVING
            # ------------------------------------------------
            #
            # During an enabled peak period or when the configured
            # VPP import threshold is exceeded, battery discharge
            # is used to reduce local demand.
            #
            # This mode does not intentionally discharge additional
            # battery energy for grid export.      
                
            elif mode == "peak_shaving":
                
                # Continue to absorb available surplus energy.
                if effective_net_power_kw < 0:
                    battery_power_kw = self.battery.charge(
                        -effective_net_power_kw,
                        timestep_hours
                    )
                # Discharge only enough to offset the remaining
                # local deficit during the applicable peak condition.
                elif (
                    effective_net_power_kw > 0
                    and (
                        is_peak_period
                        or is_grid_peak_limit_exceeded
                    )
                ):
                    battery_power_kw = self.battery.discharge(
                        effective_net_power_kw,
                        timestep_hours
                    )
            
                else:
                    battery_power_kw = 0.0

            # ------------------------------------------------
            # MODE: ECONOMIC EXPORT
            # ------------------------------------------------
            #
            # During a designated high-value export period,
            # deliberately discharge the battery beyond local
            # household demand so that available stored energy
            # may be exported to the grid.
            #
            # Unlike network-support operation, this mode does
            # not invoke A10. Battery export therefore remains
            # subject to the normal/current connection export
            # limit.
            
            elif mode == "economic_export":
            
                # Maximum discharge that can be accommodated
                # at the premises connection point consists of:
                #
                #   remaining local household demand
                #               +
                #   available grid-export headroom
            
                local_import_kw = max(
                    effective_net_power_kw,
                    0.0
                )
            
                maximum_connection_permitted_discharge_kw = (
                    local_import_kw
                    + export_headroom_kw
                )
            
                # Request the maximum economically available
                # battery discharge permitted by the connection.
                #
                # The Battery object subsequently enforces its
                # own physical power and stored-energy limits.
                battery_power_kw = self.battery.discharge(
                    maximum_connection_permitted_discharge_kw,
                    timestep_hours
                )
                    
            # ------------------------------------------------
            # MODE: NETWORK SUPPORT
            # ------------------------------------------------
            #
            # Respond to an explicit external network-support
            # request using the house-level discharge target
            # allocated by the VPP controller.
            #
            # Battery discharge first offsets this house's own
            # grid import. Any remaining requested discharge
            # becomes grid export and must remain within the
            # applicable connection export capability.
         
            elif mode == "network_support":

                requested_target_kw = signals[
                    "house_dispatch_targets"
                ].get(
                    self.name,
                    0.0
                )
            
                # Local demand that can be supplied without
                # creating grid export.
                local_import_kw = max(
                    effective_net_power_kw,
                    0.0
                )

                
                # Maximum battery discharge permitted at the
                # connection point:
                #
                #   local demand that can be offset
                #               +
                #   remaining battery export headroom
                
                maximum_connection_permitted_discharge_kw = (
                    local_import_kw
                    + export_headroom_kw
                )
                
                # Reduce the controller target if the connection
                # cannot accommodate the requested discharge.           
                
                permitted_target_kw = min(
                    requested_target_kw,
                    maximum_connection_permitted_discharge_kw
                )

                # Record any requested support that could not be
                # delivered because of the connection constraint.
                
                battery_discharge_reduction_kw = max(
                    requested_target_kw
                    - permitted_target_kw,
                    0.0
                )
                
                # Battery object applies its own remaining physical
                # power and stored-energy constraints.
                
                battery_power_kw = self.battery.discharge(
                    permitted_target_kw,
                    timestep_hours
                )

            # ------------------------------------------------
            # MODE: ARBITRAGE CHARGE
            # ------------------------------------------------
            #
            # Current placeholder for future economic operation.
            # During a designated cheap-energy period, request
            # maximum battery charging power.
            #
            # A later economic controller may replace this simple
            # rule with tariff- and forecast-based scheduling.
            
            elif mode == "arbitrage_charge":
                if is_cheap_energy_period:
                    battery_power_kw = self.battery.charge(self.battery.max_charge_kw, timestep_hours)

            
                
            # Unknown or unsupported modes default to no battery
            # action rather than creating an unintended dispatch.               
            else: 
                battery_power_kw = 0.0
            
            # Record battery SOC after the requested physical
            # battery action has been applied.
            
            battery_soc_kwh = self.battery.get_soc_kwh()
            battery_soc_percent = self.battery.get_soc_percent()
                   
        # ----------------------------------------------------
        # ACTUAL BATTERY POWER COMPONENTS
        # ----------------------------------------------------
        #
        # Convert the signed battery-power convention into
        # separate positive charge and discharge quantities for
        # logging, dashboard display and later energy accounting.

        battery_discharge_kw = max(battery_power_kw, 0.0)
        battery_charge_kw = -min(battery_power_kw, 0.0)

        # ----------------------------------------------------
        # POTENTIAL CONNECTION-POINT POWER
        # ----------------------------------------------------
        #
        # Calculate the premises power flow after the battery
        # action but before enforcing the final export constraint.
        #
        # Sign convention:
        #   positive = grid import
        #   negative = grid export

        potential_net_power_kw = (
            load_kw
            - generation_kw
            - battery_power_kw
        )

        # Convert negative net power into a positive export
        # magnitude for comparison with the export limit.
        potential_export_kw = max(
            -potential_net_power_kw,
            0.0
        )

        
        # ----------------------------------------------------
        # ENFORCE CONNECTION EXPORT LIMIT
        # ----------------------------------------------------
        #
        # Compare the potential premises export against the
        # effective export limit applicable to this timestep.
        #
        # The effective limit includes:
        #   - the normal/current connection limit, and
        #   - any A09 shared-PV-specific allowance.
        #
        # Battery discharge has already been constrained using
        # the normal/current connection limit, so any remaining
        # excess export at this stage is attributed to PV.

        if potential_export_kw > effective_export_limit_kw:

            export_limit_active = True

            excess_export_kw = (
                potential_export_kw
                - effective_export_limit_kw
            )

            # Curtail only the amount of PV required to bring the
            # premises export back within the applicable limit.
            #
            # Curtailment cannot exceed the PV generation that was
            # physically available during this timestep.
            pv_curtailment_kw = min(
                excess_export_kw,
                generation_kw
            )

        else:

            # The export-limit flag also records cases where a
            # requested battery discharge was reduced earlier
            # because of connection-point constraints.
            export_limit_active = (
                battery_discharge_reduction_kw > 0
            )


        # ----------------------------------------------------
        # ACTUAL PV GENERATION
        # ----------------------------------------------------

        # Available PV generation represents what the PV profile
        # could have produced before network-driven curtailment.
        #
        # Actual generation is the PV remaining after any required
        # export-limit curtailment.
        actual_generation_kw = (
            generation_kw
            - pv_curtailment_kw
        )


        # ----------------------------------------------------
        # FINAL CONNECTION-POINT POWER
        # ----------------------------------------------------
        #
        # Recalculate the actual premises grid exchange using:
        #   - household demand,
        #   - actual PV generation after curtailment, and
        #   - actual battery power.
        #
        # Shared-PV allocations are not directly subtracted here.
        # They represent VPP coordination between participating
        # premises, while this value represents the physical
        # meter flow at this individual connection point.

        final_net_power_kw = (
            load_kw
            - actual_generation_kw
            - battery_power_kw
        )
        
        # ----------------------------------------------------
        # BATTERY CONFIGURATION METADATA
        # ----------------------------------------------------
        #
        # Store installed battery information with the timestep
        # result so house-level exports remain self-describing.

        if self.battery is not None:

            battery_manufacturer = (
                self.battery.manufacturer
            )

            battery_model = (
                self.battery.model
            )

            battery_module_count = (
                self.battery.module_count
            )

            battery_capacity_kwh = (
                self.battery.capacity_kwh
            )

            battery_max_charge_kw = (
                self.battery.max_charge_kw
            )

            battery_max_discharge_kw = (
                self.battery.max_discharge_kw
            )

        else:

            # Explicit zero/None values allow non-battery houses
            # to use the same result structure as battery houses.
            battery_manufacturer = None
            battery_model = None
            battery_module_count = 0

            battery_capacity_kwh = 0.0
            battery_max_charge_kw = 0.0
            battery_max_discharge_kw = 0.0


            
        # ----------------------------------------------------
        # BUILD HOUSE TIMESTEP RESULT
        # ----------------------------------------------------
        #
        # Return both static configuration information and the
        # electrical results required for VPP aggregation,
        # analysis, dashboard display and later economic modelling.

        return {
            "name": self.name,

            # ------------------------------------------------
            # Physical house configuration
            # ------------------------------------------------
            "pv_array_kwp": self.pv_array_kwp,
            "pv_inverter_limit_kw":
                self.pv_inverter_limit_kw,

            "connection_type":
                self.connection_type,
            "connection_phases":
                self.connection_phases,

            "min_export_limit_kw":
                self.min_export_limit_kw,
            "max_export_limit_kw":
                self.max_export_limit_kw,
            "dynamic_export_limit_kw":
                self.dynamic_export_limit_kw,

            # ------------------------------------------------
            # Battery configuration
            # ------------------------------------------------
            "battery_manufacturer":
                battery_manufacturer,
            "battery_model":
                battery_model,
            "battery_module_count":
                battery_module_count,
            "battery_capacity_kwh":
                battery_capacity_kwh,
            "battery_max_charge_kw":
                battery_max_charge_kw,
            "battery_max_discharge_kw":
                battery_max_discharge_kw,

            # ------------------------------------------------
            # Household demand and PV generation
            # ------------------------------------------------
            "load_kw": load_kw,

            # PV available from the source profile before
            # connection-driven curtailment.
            "available_generation_kw":
                generation_kw,

            # PV prevented from being generated/exported because
            # of the applicable connection export constraint.
            "pv_curtailment_kw":
                pv_curtailment_kw,

            # PV actually retained after curtailment.
            "generation_kw":
                actual_generation_kw,

            # ------------------------------------------------
            # Connection-point state
            # ------------------------------------------------

            # Potential meter power before final PV curtailment.
            "potential_net_power_kw":
                potential_net_power_kw,

            # Normal/current connection export allowance.
            "current_export_limit_kw":
                current_export_limit_kw,

            # A09 shared-PV export allocation for this source
            # premises and the resulting effective export limit.
            "shared_pv_export_target_kw":
                shared_pv_export_target_kw,

            "effective_export_limit_kw":
                effective_export_limit_kw,

            # Records whether connection constraints affected
            # battery dispatch or PV export during this timestep.
            "export_limit_active":
                export_limit_active,

            "battery_discharge_reduction_kw":
                battery_discharge_reduction_kw,

            # ------------------------------------------------
            # Battery and final power-flow results
            # ------------------------------------------------
            "net_power_kw_before_battery":
                net_power_kw_bb,

            # Signed battery power:
            #   positive = discharge
            #   negative = charge
            "battery_power_kw":
                battery_power_kw,

            "battery_soc_kwh":
                battery_soc_kwh,
            "battery_soc_percent":
                battery_soc_percent,

            # Final physical premises grid exchange:
            #   positive = grid import
            #   negative = grid export
            "net_power_kw":
                final_net_power_kw,

            # Separate positive quantities retained for easier
            # energy accounting and dashboard display.
            "battery_charge_kw":
                battery_charge_kw,
            "battery_discharge_kw":
                battery_discharge_kw,
        }

        
# ============================================================
# BATTERY ENERGY STORAGE MODEL
# ============================================================

class Battery:
    """
    Represents the physical battery energy storage system
    installed at a participating house.

    The Battery object enforces:
        - usable energy capacity,
        - charge power limit,
        - discharge power limit,
        - charge/discharge efficiency, and
        - physical minimum SOC.

    Higher-level VPP operating policies, such as a protected
    20% SOC reserve, belong to the VPP controller rather than
    this physical battery model.

    Battery power convention used by House:
        positive = discharge
        negative = charge
    """

    def __init__(
        self,
        capacity_kwh,
        initial_soc_kwh,
        max_charge_kw,
        max_discharge_kw,
        efficiency=0.95,
        min_soc_kwh=0.0,
        manufacturer=None,
        model=None,
        module_count=None
    ):

        # ----------------------------------------------------
        # ENERGY STORAGE STATE
        # ----------------------------------------------------

        # Total usable battery energy capacity represented by
        # the simulation.
        self.capacity_kwh = capacity_kwh

        # Current stored battery energy.
        self.soc_kwh = initial_soc_kwh
       
        # Physical minimum stored energy permitted by the battery
        # model. This is separate from any controller-level SOC
        # reserve maintained for VPP operation.
        self.min_soc_kwh = min_soc_kwh


        # ----------------------------------------------------
        # BATTERY POWER LIMITS
        # ----------------------------------------------------

        # Maximum continuous charge and discharge powers after
        # accounting for the installed battery/inverter limits
        # specified when each Battery object is created.
        self.max_charge_kw = max_charge_kw
        self.max_discharge_kw = max_discharge_kw


        # ----------------------------------------------------
        # BATTERY EFFICIENCY
        # ----------------------------------------------------

        # Efficiency applied when converting between electrical
        # energy at the battery interface and stored battery energy.
        self.efficiency = efficiency


        # ----------------------------------------------------
        # BATTERY METADATA
        # ----------------------------------------------------

        # Equipment information retained for result logging,
        # reporting and demonstrator documentation.
        self.manufacturer = manufacturer
        self.model = model
        self.module_count = module_count
        
    def charge(
        self,
        requested_power_kw,
        timestep_hours
    ):
        """
        Attempt to charge the battery at the requested electrical
        power for one simulation timestep.

        Charging is limited by:
            1. the battery maximum charge power,
            2. the remaining battery energy capacity.

        Returns signed battery power:
            negative = charging
            zero     = no charging
        """

        # Ignore zero or negative charge requests.
        if requested_power_kw <= 0:
            return 0.0


        # ----------------------------------------------------
        # APPLY CHARGE POWER LIMIT
        # ----------------------------------------------------

        # Restrict the requested electrical charging power to the
        # battery's maximum permitted charge power.
        charge_power_kw = min(
            requested_power_kw,
            self.max_charge_kw
        )


        # ----------------------------------------------------
        # CONVERT INPUT POWER TO STORED ENERGY
        # ----------------------------------------------------

        # Determine the energy that would be added to the battery
        # during this timestep after applying charging efficiency.
        requested_energy_kwh = (
            charge_power_kw
            * timestep_hours
            * self.efficiency
        )


        # ----------------------------------------------------
        # APPLY BATTERY ENERGY-CAPACITY LIMIT
        # ----------------------------------------------------

        # Remaining energy that can be stored before the battery
        # reaches its usable capacity.
        available_space_kwh = (
            self.capacity_kwh
            - self.soc_kwh
        )

        # Actual stored energy cannot exceed the remaining
        # available battery capacity.
        actual_energy_kwh = min(
            requested_energy_kwh,
            available_space_kwh
        )


        # ----------------------------------------------------
        # UPDATE BATTERY SOC
        # ----------------------------------------------------

        self.soc_kwh += actual_energy_kwh


        # ----------------------------------------------------
        # DETERMINE ACTUAL ELECTRICAL CHARGING POWER
        # ----------------------------------------------------

        # Convert the energy actually stored back to the
        # corresponding electrical charging power at the battery
        # interface.
        actual_charge_power_kw = (
            actual_energy_kwh
            / (
                timestep_hours
                * self.efficiency
            )
        )

        # House uses negative battery power to represent charging.
        battery_power_kw = (
            -actual_charge_power_kw
        )

        return battery_power_kw
        
    def discharge(
        self,
        requested_power_kw,
        timestep_hours
    ):
        """
        Attempt to discharge the battery at the requested
        electrical power for one simulation timestep.

        Discharging is limited by:
            1. the battery maximum discharge power,
            2. the energy available above physical minimum SOC.

        Returns signed battery power:
            positive = discharging
            zero     = no discharge
        """

        # Ignore zero or negative discharge requests.
        if requested_power_kw <= 0:
            return 0.0


        # ----------------------------------------------------
        # APPLY DISCHARGE POWER LIMIT
        # ----------------------------------------------------

        # Restrict requested output power to the battery's
        # maximum permitted discharge power.
        discharge_power_kw = min(
            requested_power_kw,
            self.max_discharge_kw
        )


        # ----------------------------------------------------
        # CONVERT OUTPUT POWER TO REQUIRED BATTERY ENERGY
        # ----------------------------------------------------

        # Determine how much stored battery energy must be removed
        # to provide the requested electrical output after losses.
        requested_energy_kwh = (
            discharge_power_kw
            * timestep_hours
            / self.efficiency
        )


        # ----------------------------------------------------
        # APPLY MINIMUM SOC / AVAILABLE ENERGY LIMIT
        # ----------------------------------------------------

        # Stored energy physically available for discharge above
        # the battery model's minimum SOC.
        available_energy_kwh = max(
            0.0,
            self.soc_kwh
            - self.min_soc_kwh
        )

        # Actual battery energy removed cannot exceed the energy
        # currently available above minimum SOC.
        actual_energy_kwh = min(
            available_energy_kwh,
            requested_energy_kwh
        )


        # ----------------------------------------------------
        # UPDATE BATTERY SOC
        # ----------------------------------------------------

        self.soc_kwh -= actual_energy_kwh


        # ----------------------------------------------------
        # DETERMINE ACTUAL ELECTRICAL DISCHARGE POWER
        # ----------------------------------------------------

        # Apply discharge efficiency to determine the electrical
        # power actually delivered by the battery.
        actual_discharge_power_kw = (
            actual_energy_kwh
            * self.efficiency
            / timestep_hours
        )

        # Positive battery power represents discharge.
        battery_power_kw = (
            actual_discharge_power_kw
        )

        return battery_power_kw
        
    def get_soc_percent(self):
        """
        Return the current battery state of charge as a percentage
        of the modelled usable battery capacity.
        """

        return (
            self.soc_kwh
            / self.capacity_kwh
        ) * 100


    def get_soc_kwh(self):
        """
        Return the current stored battery energy in kWh.
        """

        return self.soc_kwh