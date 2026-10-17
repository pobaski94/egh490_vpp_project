

class FinancialModel:

    def __init__(
        self,
        tariff,
        shared_pv_purchase_rate=0.0,
        shared_pv_supplier_rate=0.0
    ):
        self.tariff = tariff
        
        self.shared_pv_purchase_rate = (
            shared_pv_purchase_rate
        )

        self.shared_pv_supplier_rate = (
            shared_pv_supplier_rate
        )


        # Daily counters required by tariffs such as
        # Origin Battery Charge
        self.current_day = None

        self.daily_free_import_kwh = 0.0
        self.daily_peak_export_kwh = 0.0

        self.house_totals = {}

        self.vpp_totals = {
            "cumulative_import_cost": 0.0,
            "cumulative_export_revenue": 0.0,
            "cumulative_shared_pv_cost": 0.0,
            "cumulative_shared_pv_revenue": 0.0,
            "cumulative_net_cost": 0.0,
            "cumulative_normal_export_kwh": 0.0,
            "cumulative_vpp_event_export_kwh": 0.0,
            "cumulative_normal_export_revenue": 0.0,
            "cumulative_vpp_event_export_revenue": 0.0,
        }

        
    def reset_daily_counters_if_needed(
        self,
        day_number
    ):
        
        if self.current_day != day_number:
    
            self.current_day = day_number
    
            self.daily_free_import_kwh = 0.0
            self.daily_peak_export_kwh = 0.0

    def get_import_rate(
        self,
        hour_of_day
    ):
    
        if (
            self.tariff["peak_start_hour"]
            <= hour_of_day
            < self.tariff["peak_end_hour"]
        ):
            return self.tariff[
                "peak_import_rate"
            ]
    
        return self.tariff[
            "off_peak_import_rate"
        ]
    def get_export_rate(
        self,
        hour_of_day
    ):
    
        if (
            self.tariff["peak_start_hour"]
            <= hour_of_day
            < self.tariff["peak_end_hour"]
        ):
            return self.tariff[
                "peak_export_rate"
            ]
    
        return self.tariff[
            "off_peak_export_rate"
        ]
        
    def get_event_export_rate(
        self,
        hour_of_day
    ):
    
        # Use the dedicated event tariff when one exists.
        if "event_export_rate" in self.tariff:
            return self.tariff[
                "event_export_rate"
            ]
    
        # Tariffs without a special event rate fall back
        # to the normal export tariff.
        return self.get_export_rate(
            hour_of_day
        )
    
        
    def calculate_timestep_cost(
        self,
        external_grid_import_kwh,
        external_grid_export_kwh,
        vpp_event_export_kwh,
        shared_pv_received_kwh,
        shared_pv_supplied_kwh,
        hour_of_day,
        day_number,
    ):
    
        import_rate = self.get_import_rate(
            hour_of_day
        )
    
        normal_export_rate = self.get_export_rate(
            hour_of_day
        )
        
        event_export_rate = self.get_event_export_rate(
            hour_of_day
        )

        normal_grid_export_kwh = max(
            external_grid_export_kwh
            - vpp_event_export_kwh,
            0.0
        )
        
        # External grid settlement
        import_cost = (
            external_grid_import_kwh
            * import_rate
        )
    
        normal_export_revenue = (
            normal_grid_export_kwh
            * normal_export_rate
        )
        
        vpp_event_export_revenue = (
            vpp_event_export_kwh
            * event_export_rate
        )
        
        export_revenue = (
            normal_export_revenue
            + vpp_event_export_revenue
        )
    
        # Internal VPP PV-sharing settlement
        shared_pv_cost = (
            shared_pv_received_kwh
            * self.shared_pv_purchase_rate
        )
    
        shared_pv_revenue = (
            shared_pv_supplied_kwh
            * self.shared_pv_supplier_rate
        )
    
        net_cost = (
            import_cost
            + shared_pv_cost
            - export_revenue
            - shared_pv_revenue
        )
    
        return {
            "import_energy_kwh":
                external_grid_import_kwh,
    
            "export_energy_kwh":
                external_grid_export_kwh,

            "normal_export_energy_kwh":
                normal_grid_export_kwh,
            
            "vpp_event_export_kwh":
                vpp_event_export_kwh,
                
            "shared_pv_received_kwh":
                shared_pv_received_kwh,
    
            "shared_pv_supplied_kwh":
                shared_pv_supplied_kwh,
    
            "import_rate":
                import_rate,
    
            # Retained as the normal FiT for compatibility with
            # existing reporting code.
            "export_rate":
                normal_export_rate,
            
            "normal_export_rate":
                normal_export_rate,
            
            "vpp_event_export_rate":
                event_export_rate,
    
            "shared_pv_purchase_rate":
                self.shared_pv_purchase_rate,
    
            "shared_pv_supplier_rate":
                self.shared_pv_supplier_rate,
    
            "import_cost":
                import_cost,
    
            "export_revenue":
                export_revenue,
            
            "normal_export_revenue":
                normal_export_revenue,
            
            "vpp_event_export_revenue":
                vpp_event_export_revenue,
    
            "shared_pv_cost":
                shared_pv_cost,
    
            "shared_pv_revenue":
                shared_pv_revenue,
    
            "net_cost":
                net_cost,
        }

        
    def calculate_vpp_timestep(
        self,
        house_results,
        timestep_hours,
        hour_of_day,
        day_number,
        vpp_event=False
    ):
        financials_houses = {}
    
        # Initialise aggregate financial results
        vpp_financials = {
            "import_energy_kwh": 0.0,
            "export_energy_kwh": 0.0,
        
            "normal_export_energy_kwh": 0.0,
            "vpp_event_export_kwh": 0.0,

            
        
            "shared_pv_received_kwh": 0.0,
            "shared_pv_supplied_kwh": 0.0,
        
            "import_cost": 0.0,
        
            "export_revenue": 0.0,
            "normal_export_revenue": 0.0,
            "vpp_event_export_revenue": 0.0,
        
            "shared_pv_cost": 0.0,
            "shared_pv_revenue": 0.0,
        
            "net_cost": 0.0
        }
    
        for result in house_results:
    
            house_name = result["name"]
    
            house_financials = self.calculate_timestep_cost(
                external_grid_import_kwh=(
                    result["external_grid_import_kwh"]
                ),
                external_grid_export_kwh=(
                    result["external_grid_export_kwh"]
                ),
                vpp_event_export_kwh=(
                    result.get(
                        "vpp_event_export_kwh",
                        0.0
                    )
                ),
                shared_pv_received_kwh=(
                    result["shared_pv_received_kwh"]
                ),
                shared_pv_supplied_kwh=(
                    result["shared_pv_supplied_kwh"]
                ),
                hour_of_day=hour_of_day,
                day_number=day_number,
            )

            if house_name not in self.house_totals:
                self.house_totals[house_name] = {
                    "cumulative_import_cost": 0.0,
                    "cumulative_export_revenue": 0.0,
                    "cumulative_shared_pv_cost": 0.0,
                
                    "cumulative_shared_pv_revenue": 0.0,
                    "cumulative_normal_export_revenue":0.0,
                    "cumulative_vpp_event_export_revenue": 0.0,
            
                    "cumulative_shared_pv_received_kwh": 0.0,
                    "cumulative_shared_pv_supplied_kwh": 0.0,
                    "cumulative_normal_export_kwh": 0.0,
                    "cumulative_vpp_event_export_kwh": 0.0,
                
                    "cumulative_net_cost": 0.0,
                }
            self.house_totals[house_name][
                "cumulative_import_cost"
            ] += house_financials["import_cost"]
            
            self.house_totals[house_name][
                "cumulative_export_revenue"
            ] += house_financials["export_revenue"]
            
            self.house_totals[house_name][
                "cumulative_shared_pv_cost"
            ] += house_financials["shared_pv_cost"]
            
            self.house_totals[house_name][
                "cumulative_shared_pv_revenue"
            ] += house_financials["shared_pv_revenue"]
            
            self.house_totals[house_name][
                "cumulative_shared_pv_received_kwh"
            ] += house_financials["shared_pv_received_kwh"]
            
            self.house_totals[house_name][
                "cumulative_shared_pv_supplied_kwh"
            ] += house_financials["shared_pv_supplied_kwh"]
            
            self.house_totals[house_name][
                "cumulative_net_cost"
            ] += house_financials["net_cost"]

            self.house_totals[house_name][
                "cumulative_normal_export_kwh"
            ] += house_financials[
                "normal_export_energy_kwh"
            ]
            
            self.house_totals[house_name][
                "cumulative_vpp_event_export_kwh"
            ] += house_financials[
                "vpp_event_export_kwh"
            ]
            
            self.house_totals[house_name][
                "cumulative_normal_export_revenue"
            ] += house_financials[
                "normal_export_revenue"
            ]
            
            self.house_totals[house_name][
                "cumulative_vpp_event_export_revenue"
            ] += house_financials[
                "vpp_event_export_revenue"
            ]
            
            house_financials.update(
                self.house_totals[house_name]
            )
            
    
            financials_houses[house_name] = house_financials
    
            # Add this house's financial results to VPP totals
            for key in vpp_financials:
                vpp_financials[key] += house_financials[key]

                
        # --------------------------------------------------
        # VPP CUMULATIVE FINANCIAL RESULTS
        # --------------------------------------------------
    
        self.vpp_totals[
            "cumulative_import_cost"
        ] += vpp_financials["import_cost"]
        
        self.vpp_totals[
            "cumulative_export_revenue"
        ] += vpp_financials["export_revenue"]
        
        self.vpp_totals[
            "cumulative_shared_pv_cost"
        ] += vpp_financials["shared_pv_cost"]
        
        self.vpp_totals[
            "cumulative_shared_pv_revenue"
        ] += vpp_financials["shared_pv_revenue"]
        
        self.vpp_totals[
            "cumulative_net_cost"
        ] += vpp_financials["net_cost"]

        self.vpp_totals[
            "cumulative_normal_export_kwh"
            ] += vpp_financials["normal_export_energy_kwh"]

        self.vpp_totals[
            "cumulative_vpp_event_export_kwh"
            ] += vpp_financials["vpp_event_export_kwh"]

        self.vpp_totals[
            "cumulative_normal_export_revenue"
            ] += vpp_financials["normal_export_revenue"]

        self.vpp_totals[
            "cumulative_vpp_event_export_revenue"
            ] += vpp_financials["vpp_event_export_revenue"]
        
    
        # Add cumulative totals after all houses are aggregated
        vpp_financials.update(
            self.vpp_totals
        )
    
        return {
            "houses": financials_houses,
            "VPP": vpp_financials
        }
                                

        





if __name__ == "__main__":

    # PLace holder tariff values
    import_tariff = 0.3134 # $/kWh
    feed_in_tariff = 0.1000 # $/kWh

    # Create financial model
    financial_model = FinancialModel(import_tariff, feed_in_tariff)
    # placeholder timestep
    net_power_kw = -8.4
    timestep_hours = 0.5

    result = financial_model.calculate_timestep_cost(net_power_kw, timestep_hours)

    print(result)
    
