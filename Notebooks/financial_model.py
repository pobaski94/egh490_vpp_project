

class FinancialModel:

    def __init__(
        self,
        import_tariff,
        feed_in_tariff
    ):
        self.import_tariff = import_tariff
        self.feed_in_tariff = feed_in_tariff

    def calculate_timestep_cost(
        self,
        net_power_kw,
        timestep_hours
    ):

        # NOTE current house sign convention for net_power is:
        # positive net_power_kw -> grid import
        # negative net_power_kw -> grid export

        import_power_kw = max(net_power_kw, 0.0)
        export_power_kw = max(-net_power_kw, 0.0)

        # Convert power to energy using the sim timestep
        import_energy_kwh = import_power_kw * timestep_hours
        export_energy_kwh = export_power_kw * timestep_hours
        
        # Calculate the revenue and cost for the timestep and the net cost
        timestep_cost = import_energy_kwh * self.import_tariff 
        timestep_revenue = export_energy_kwh * self.feed_in_tariff
        net_cost = timestep_cost - timestep_revenue

        return {
            "import_energy_kwh": import_energy_kwh,
            "export_energy_kwh": export_energy_kwh,
            "import_cost": timestep_cost,
            "export_revenue": timestep_revenue,
            "net_cost": net_cost
        }

        
    def calculate_vpp_timestep(
            self,
            house_results,
            timestep_hours
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
        
                house_financials_results = self.calculate_timestep_cost(
                    result["net_power_kw"],
                    timestep_hours
                )
        
                financials_houses[house_name] = house_financials_results
        
                # Add this house's financial results to VPP totals
                for key in vpp_financials:
                    vpp_financials[key] += house_financials_results[key]
        
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
    
