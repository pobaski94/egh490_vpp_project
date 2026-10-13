

class FinancialModel:

    def __init__(
        self,
        tariff
    ):
        self.tariff = tariff

        # Daily counters required by tariffs such as
        # Origin Battery Charge
        self.current_day = None

        self.daily_free_import_kwh = 0.0
        self.daily_peak_export_kwh = 0.0

        self.house_totals = {}

        self.vpp_totals = {
            "cumulative_import_cost": 0.0,
            "cumulative_export_revenue": 0.0,
            "cumulative_net_cost": 0.0,
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
        hour_of_day,
        vpp_event=False
    ):
    
        if (
            vpp_event
            and "event_export_rate" in self.tariff
        ):
            return self.tariff[
                "event_export_rate"
            ]
    
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

        
    def calculate_timestep_cost(
        self,
        net_power_kw,
        timestep_hours,
        hour_of_day,
        day_number,
        vpp_event=False
    ):

        # NOTE current house sign convention for net_power is:
        # positive net_power_kw -> grid import
        # negative net_power_kw -> grid export

        import_power_kw = max(net_power_kw, 0.0)
        export_power_kw = max(-net_power_kw, 0.0)

        # Convert power to energy using the sim timestep
        import_energy_kwh = import_power_kw * timestep_hours
        export_energy_kwh = export_power_kw * timestep_hours


        import_rate = self.get_import_rate(
            hour_of_day
        )
        
        export_rate = self.get_export_rate(
            hour_of_day,
            vpp_event
        )
        
        # Calculate the revenue and cost for the timestep and the net cost
        import_cost = (
            import_energy_kwh
            * import_rate
        )
        
        export_revenue = (
            export_energy_kwh
            * export_rate
        )
        
        net_cost = (
            import_cost
            - export_revenue
        )

        return {
            "import_energy_kwh":
                import_energy_kwh,
        
            "export_energy_kwh":
                export_energy_kwh,
        
            "import_rate":
                import_rate,
        
            "export_rate":
                export_rate,
        
            "import_cost":
                import_cost,
        
            "export_revenue":
                export_revenue,
        
            "net_cost":
                net_cost
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
            "import_cost": 0.0,
            "export_revenue": 0.0,
            "net_cost": 0.0
        }
    
        for result in house_results:
    
            house_name = result["name"]
    
            house_financials = (
                self.calculate_timestep_cost(
                    result["net_power_kw"],
                    timestep_hours,
                    hour_of_day,
                    day_number,
                    vpp_event
                )
            )

            if house_name not in self.house_totals:
                self.house_totals[house_name] = {
                    "cumulative_import_cost": 0.0,
                    "cumulative_export_revenue": 0.0,
                    "cumulative_net_cost": 0.0,
                }
            self.house_totals[house_name]["cumulative_import_cost"] += (
                house_financials["import_cost"]
            )
            
            self.house_totals[house_name]["cumulative_export_revenue"] += (
                house_financials["export_revenue"]
            )
            
            self.house_totals[house_name]["cumulative_net_cost"] += (
                house_financials["net_cost"]
            )
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
    
        self.vpp_totals["cumulative_import_cost"] += (
            vpp_financials["import_cost"]
        )
    
        self.vpp_totals["cumulative_export_revenue"] += (
            vpp_financials["export_revenue"]
        )
    
        self.vpp_totals["cumulative_net_cost"] += (
            vpp_financials["net_cost"]
        )
    
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
    
