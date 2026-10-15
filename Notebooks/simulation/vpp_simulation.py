# ============================================================
# VPP SIMULATION ORCHESTRATOR
# ============================================================


class VPPSimulation:
    """
    Coordinates the VPP simulation at each discrete timestep.

    The simulation object does not decide how DER should operate.
    Instead, it:

        1. selects the current load/PV profile values,
        2. updates connection constraints,
        3. gathers the pre-control state of each house,
        4. requests control signals from the VPP controller,
        5. executes each house and battery response,
        6. calculates VPP and wider-network power balances,
        7. stores results for analysis and hardware display.

    The VPP boundary contains the five participating houses only.
    Hospital and wind resources are external demonstration elements.
    """

    
    def __init__(self,
                 houses,
                 hospital,
                 wind,
                 controller,
                 timestep_hours,
                 financial_model,
                 num_steps
                ):
        
        # Participating residential VPP assets.
        self.houses = houses

        # External demonstration resources.
        # These are included in the wider network power balance,
        # but are not internal VPP assets.
        self.hospital = hospital
        self.wind = wind

        # Supervisory controller responsible for selecting the
        # VPP operating mode and issuing house-level targets.
        self.controller = controller

         #Economic modelelling
        self.financial_model = financial_model

        # Duration of one logical simulation timestep and number
        # of available profile samples.
        self.timestep_hours = timestep_hours
        self.num_steps = num_steps

        # Absolute simulation step. This continues increasing even
        # when the finite profile dataset loops back to its start.
        self.current_step = 0

        # VPP-level results recorded once per simulation timestep.
        self.simulation_results_summary = []

        # Separate timestep results retained for each house.
        self.house_results_log = {
            house.name: [] for house in houses
        }

        

        
    def step(self, external_inputs=None):

        """
        Execute one logical VPP simulation timestep.

        external_inputs contains supervisory commands originating
        outside the normal controller logic, such as simulated or
        physical network-support and PV-sharing inputs.
        """
        
        
        if external_inputs is None:
            
            external_inputs = {}

        # Loop the finite load/PV dataset continuously.
        # current_step continues increasing while profile_index
        # wraps back to zero after the final profile sample.
            
        profile_index = self.current_step % self.num_steps

        # Convert the absolute simulation step into time-of-day.
        # For a 0.5 h timestep:
        #   step 0  = 00:00
        #   step 1  = 00:30
        #   step 32 = 16:00
        
        hour_of_day = (
            self.current_step * self.timestep_hours
        ) % 24

        
        # --------------------------------------------------------
        # UPDATE CONNECTION EXPORT LIMITS
        # --------------------------------------------------------
        #
        # A10:
        # During an explicit network-support event, the
        # demonstrator assumes that additional connection export
        # capacity may temporarily be made available up to the
        # modelled maximum connection capability.
        #
        # Export limits are updated BEFORE house states are passed
        # to the controller so that reported VPP discharge
        # capability reflects the applicable connection limit.

        network_support_request = external_inputs.get(
            "network_support_request",
            False
        )
        
        for house in self.houses:
            house.update_export_limit(
                profile_index,
                network_support_request
            )
        
        # --------------------------------------------------------
        # GATHER PRE-CONTROL SYSTEM STATE
        # --------------------------------------------------------

        # Each house reports its electrical state and available
        # DER flexibility before any control action is applied.

        house_states = [
            house.get_state(
                profile_index,
                self.timestep_hours
                )
                for house in self.houses
        ]
        
        # Evaluate external demonstration resources separately.
        # These resources are not included in the VPP boundary.   
        hospital_result = self.hospital.step(profile_index)
        wind_result = self.wind.step(profile_index)

    
        # --------------------------------------------------------
        # VPP SUPERVISORY CONTROL
        # --------------------------------------------------------

        # Determine the operating mode and any house-level
        # dispatch or shared-PV targets for this timestep.
        signals = self.controller.get_signals(
            hour_of_day,
            external_inputs,
            house_states,
        )


        # --------------------------------------------------------
        # EXECUTE HOUSE AND DER RESPONSE
        # --------------------------------------------------------

        # Each house applies the controller signals while its
        # House and Battery objects enforce local physical limits.

        house_results = [
            house.step(
                profile_index,
                self.timestep_hours,
                signals
            )
            for house in self.houses
        ]

        total_shared_pv_received_kw = sum(
            result["shared_pv_received_kw"]
            for result in house_results
        )

        total_shared_pv_supplied_kw = sum(
            result["shared_pv_supplied_kw"]
            for result in house_results
        )
        
        shared_pv_balance_error_kw = (
            total_shared_pv_supplied_kw - total_shared_pv_received_kw
        )
        

        # --------------------------------------------------------
        # SIMULATION TIME
        # --------------------------------------------------------

        # Absolute elapsed simulation time does not reset when
        # the underlying profile dataset loops.

        elapsed_hours = self.current_step * self.timestep_hours
        day_number = int(elapsed_hours // 24) + 1
        

        
        # --------------------------------------------------------
        # FINANCIAL ACCOUNTING
        # --------------------------------------------------------
        
        financial_results = (
            self.financial_model
            .calculate_vpp_timestep(
                house_results,
                self.timestep_hours,
                hour_of_day,
                day_number,
                vpp_event=external_inputs.get(
                    "vpp_tariff_event",
                    False
                )
            )
        )
        
        # Attach financial outcomes to each house result
        for result in house_results:
            house_name = result["name"]
        
            result.update(
                financial_results["houses"][house_name]
            )

        # --------------------------------------------------------
        # AGGREGATE PARTICIPATING HOUSE RESULTS
        # --------------------------------------------------------

        total_house_demand_kw = sum(
            h["load_kw"]
            for h in house_results
        )

        total_house_generation_kw = sum(
            h["generation_kw"]
            for h in house_results
        )

        total_house_net_power_kw = sum(
            h["net_power_kw"]
            for h in house_results
        )

        total_house_net_power_before_battery_kw = sum(
            h["net_power_kw_before_battery"]
            for h in house_results
        )

        # Positive battery power represents discharge.
        # Negative battery power represents charging.
        total_battery_power_kw = sum(
            h["battery_power_kw"]
            for h in house_results
        )

        # Aggregate stored battery energy across all
        # battery-equipped VPP participants.
        total_battery_soc_kwh = sum(
            h["battery_soc_kwh"]
            for h in house_results
        )

        total_battery_discharge_kw = sum(
            h["battery_discharge_kw"]
            for h in house_results
        )

        total_battery_charge_kw = sum(
            h["battery_charge_kw"]
            for h in house_results
        )

        # External demonstration quantities.
        total_local_load_kw = (
            hospital_result["load_kw"]
        )

        total_wind_generation_kw = (
            wind_result["generation_kw"]
        )

        # --------------------------------------------------------
        # VPP GRID EXCHANGE
        # --------------------------------------------------------
        #
        # Only the five participating houses belong to the VPP.
        #
        # Sign convention:
        #   positive VPP net power = net grid import
        #   negative VPP net power = net grid export

        
        vpp_net_power_kw = total_house_net_power_kw
        
        vpp_grid_import_kw = max(
            vpp_net_power_kw,
            0.0
        )
        
        vpp_grid_export_kw = -min(
            vpp_net_power_kw,
            0.0
        )
        
        
        # --------------------------------------------------------
        # WIDER DEMONSTRATION / NETWORK POWER BALANCE
        # --------------------------------------------------------
        #
        # Hospital and wind/DFIG are included here only to show
        # the interaction between the VPP and external resources.
        # They do not alter the defined VPP asset boundary.
        
        network_net_power_kw = (
            vpp_net_power_kw
            + total_local_load_kw
            - total_wind_generation_kw
        )
        
        network_grid_import_kw = max(
            network_net_power_kw,
            0.0
        )
        
        network_grid_export_kw = -min(
            network_net_power_kw,
            0.0
        )
        
        

        # --------------------------------------------------------
        # BUILD TIMESTEP RESULT
        # --------------------------------------------------------
        #
        # Store the quantities required for:
        #   - technical analysis,
        #   - later economic analysis,
        #   - dashboard visualisation,
        #   - debugging and result export.

        timestep_result = {
            "Simulation_step": self.current_step,
            "Profile_index": profile_index,
            "Elapsed_hours": elapsed_hours,
            "Day_number": day_number,
            "Hour_of_day": hour_of_day,

            "House_demand_kw": total_house_demand_kw,
            "House_generation_kw": total_house_generation_kw,
            "House_net_power_before_battery_kw":
                total_house_net_power_before_battery_kw,

            "Battery_power_kw": total_battery_power_kw,
            "Battery_soc_kwh": total_battery_soc_kwh,
            "Battery_discharge_kw": total_battery_discharge_kw,
            "Battery_charge_kw": total_battery_charge_kw,
            
            "Battery_discharge_kwh": total_battery_discharge_kw * self.timestep_hours,

            "Battery_charge_kwh": total_battery_charge_kw * self.timestep_hours,

            "Dynamic_export_limits_kw": {
                house.name:
                    house.dynamic_export_limit_kw
                for house in self.houses
            },
            
            "Current_export_limits_kw": {
                house.name:
                    house.current_export_limit_kw
                for house in self.houses
            },

            # VPP power balance
            "VPP_net_power_kw": vpp_net_power_kw,
            "VPP_grid_import_kw": vpp_grid_import_kw,
            "VPP_grid_export_kw": vpp_grid_export_kw,
            
            # External demonstration resources
            "Hospital_load_kw": total_local_load_kw,
            "Wind_generation_kw": total_wind_generation_kw,
            
            # Wider demonstration/network power balance
            "Network_net_power_kw": network_net_power_kw,
            "Network_grid_import_kw": network_grid_import_kw,
            "Network_grid_export_kw": network_grid_export_kw,

            "VPP_mode": signals["mode"],
            "is_peak_period": signals["is_peak_period"],
            "Is_event_period": signals["is_event_period"],
            "Is_cheap_energy_period":signals["is_cheap_energy_period"],
            "PV_sharing_enabled": signals["pv_sharing_enabled"],

            "Requested_support_kw": signals["requested_support_kw"],
            "Available_VPP_discharge_kw":signals["total_available_discharge_kw"],
            
            "Shared_PV_available_kw": signals["total_shared_pv_available_kw"],
            "Shared_PV_transferred_kw": signals["total_shared_pv_transferred_kw"],
            
            "house_shared_pv_targets": signals["house_shared_pv_targets"],
            "House_shared_export_targets": signals["house_shared_export_targets"],
            "VPP_available_charge_kw": {
                house.name: state["vpp_available_charge_kw"]
                for house, state in zip(
                    self.houses,
                    house_states
                )
            },
            
            # Active tariff configuration
            "Tariff_plan":
                self.financial_model.tariff["name"],
            "VPP_tariff_event":
                external_inputs.get(
                    "vpp_tariff_event",
                    False
                ),

            "Shared_PV_received_kw":
                total_shared_pv_received_kw,
            
            "Shared_PV_supplied_kw":
                total_shared_pv_supplied_kw,
            
            "Shared_PV_balance_error_kw":
                shared_pv_balance_error_kw,
            
            # VPP financial accounting
            "VPP_import_energy_kwh":
                financial_results["VPP"]["import_energy_kwh"],
            
            "VPP_export_energy_kwh":
                financial_results["VPP"]["export_energy_kwh"],
            
            "VPP_import_cost":
                financial_results["VPP"]["import_cost"],
            
            "VPP_export_revenue":
                financial_results["VPP"]["export_revenue"],
            
            "VPP_net_cost":
                financial_results["VPP"]["net_cost"],
            
            "VPP_cumulative_import_cost":
                financial_results["VPP"]["cumulative_import_cost"],
            
            "VPP_cumulative_export_revenue":
                financial_results["VPP"]["cumulative_export_revenue"],
            
            "VPP_cumulative_net_cost":
                financial_results["VPP"]["cumulative_net_cost"]
        }


        # Store the VPP-level result for this timestep.
        self.simulation_results_summary.append(timestep_result)


        # Store detailed individual-house results separately.
        for result in house_results:
            house_name = result["name"]
            self.house_results_log[house_name].append(result)


        # Advance the absolute simulation clock.
        # Profile wrapping occurs at the beginning of the next
        # call through the modulo operation on profile_index.
        
        self.current_step += 1


        # Return the latest result
        return timestep_result
