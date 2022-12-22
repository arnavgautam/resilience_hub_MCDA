from math import ceil
from pathlib import Path
import numpy as np
from pandas import concat, DataFrame
import pareto

from constant import CO2_INTENSITY, CRITERIA, DIESEL_POWER_OUTPUT, FIXED_COSTS, NOX_AIR_POLLUTANT_INTENSITY, PM_AIR_POLLUTANT_INTENSITY, SO2_AIR_POLLUTANT_INTENSITY, PVWATTS_HOURLY_8760, SOFC_POWER_OUTPUT, STORAGE_ENERGY_CAPACITY, STORAGE_MAX_DISCHARGE_RATE, TECH_LABELS, VARIABLE_COSTS, Technology, STORAGE_ENERGY_CAPACITY, STORAGE_MAX_DISCHARGE_RATE, TECH_LABELS, VARIABLE_COSTS, Technology

class TechnologyEvaluator():

    def __init__(self, categories = CRITERIA, CNSP_THRESHOLD = 0.2):
        self.categories = categories
        self.CNSP_THRESHOLD = CNSP_THRESHOLD
        self.tech_criteria_data = DataFrame(columns = self.categories)
        self.oversized_tech_criteria_data = DataFrame(columns = self.categories)
        self.CNSP_failing_tech_criteria_data = DataFrame(columns = self.categories)
        self.tech_output_timeseries = dict()

    def compile_tech_outputs(self, start, end):
        self.tech_output_timeseries[Technology.SOFC] = [10000] * (end - start)
        self.tech_output_timeseries[Technology.DIESEL] = [10000] * (end - start)
        self.tech_output_timeseries[Technology.SOLAR_STORAGE] = PVWATTS_HOURLY_8760["AC System Output (W)"][start:end].tolist() # Battery behavior is modeled separately


        # For solar + storage, we assume that max output is the battery discharging at max rate and the solar panel also sending its power to the grid
        # self.SOLAR_STORAGE_POWER_OUTPUT = max(self.SOLAR_OUTPUT) + STORAGE_MAX_DISCHARGE_RATE
        # For solar + storage, we assume that the total energy is the energy generated by the solar panel, plus the full capacity of the battery
        # self.SOLAR_STORAGE_ENERGY_OUTPUT = sum(self.SOLAR_OUTPUT) + STORAGE_ENERGY_CAPACITY
        
        # self.POWER_OUTPUTS = {Technology.SOLAR_STORAGE:self.SOLAR_STORAGE_POWER_OUTPUT, Technology.SOFC:SOFC_POWER_OUTPUT, Technology.DIESEL: DIESEL_POWER_OUTPUT}

    def gather_tech_performance(self, tech, number_of_systems, total_kW_gen):
        fixed_cost = number_of_systems * FIXED_COSTS[tech]
        variable_cost = total_kW_gen * VARIABLE_COSTS[tech]
        co2_emissions = total_kW_gen * CO2_INTENSITY[tech]
        NOx_air_pollutant_emissions = total_kW_gen * NOX_AIR_POLLUTANT_INTENSITY[tech]
        PM_air_pollutant_emissions = total_kW_gen * PM_AIR_POLLUTANT_INTENSITY[tech]
        SO2_air_pollutant_emissions = total_kW_gen * SO2_AIR_POLLUTANT_INTENSITY[tech]
        tech_data = [fixed_cost + variable_cost, co2_emissions, NOx_air_pollutant_emissions, PM_air_pollutant_emissions, SO2_air_pollutant_emissions]
        return np.array(tech_data)
    
    def evaluate_technologies(self, kW_gen_data, hourly_EWOMP, technology_sets):
        CNSP_failing_systems = list()
        overlarge_systems = list()
        for tech_set in technology_sets:
            individual_tech_outputs = dict()
            system_output = self.get_system_output_timeseries(tech_set, kW_gen_data, individual_tech_outputs)
            
            combined_data = None
            for tech, tech_number_of_systems in tech_set.items():
                tech_data = self.gather_tech_performance(tech, tech_number_of_systems, sum(individual_tech_outputs[tech]))
                if combined_data is None:
                    combined_data = tech_data
                else:
                    combined_data = np.add(combined_data, tech_data)
            
            customer_not_supplied_probability = self.get_customer_not_supplied_probability(system_output, kW_gen_data)
            EWOMP = self.get_EWOMP(system_output, kW_gen_data, hourly_EWOMP)
            combined_data = np.append(combined_data, customer_not_supplied_probability)
            combined_data = np.append(combined_data, -EWOMP)

            system_label = ' & '.join([f'{tech_set[tech]} {TECH_LABELS[tech]}' + ('s' if False and tech_set[tech] > 1 else '') for tech in tech_set])
            
            if self.system_is_oversized(system_output, kW_gen_data, multiplier = 1.1):
                overlarge_systems.append(tech_set)
                self.oversized_tech_criteria_data.loc[system_label] = combined_data
                continue
            if customer_not_supplied_probability > self.CNSP_THRESHOLD:
                CNSP_failing_systems.append(tech_set)
                self.CNSP_failing_tech_criteria_data.loc[system_label] = combined_data
                continue

            self.tech_criteria_data.loc[system_label] = combined_data
        return CNSP_failing_systems, overlarge_systems
    
    def system_is_oversized(self, system_output, kW_gen_data, multiplier = 1.5):
        return np.all(system_output > multiplier * np.array(kW_gen_data))

    def get_system_output_timeseries(self, tech_set, kW_gen_data, individual_tech_outputs):
        system_output = np.zeros(len(kW_gen_data))
        for tech in tech_set:
            individual_tech_outputs[tech] = np.multiply(self.tech_output_timeseries[tech], tech_set[tech])
            system_output += individual_tech_outputs[tech]

        # Adjust battery behavior as possible and as needed
        if tech_set[Technology.SOLAR_STORAGE] > 0:
            max_charge_rate = STORAGE_MAX_DISCHARGE_RATE * tech_set[Technology.SOLAR_STORAGE]
            starting_energy_stored = STORAGE_ENERGY_CAPACITY * tech_set[Technology.SOLAR_STORAGE]
            cumulative_energy = starting_energy_stored
            for i in range(len(kW_gen_data)):
                present_generation = system_output[i]
                needed_generation = kW_gen_data[i]
                if needed_generation > present_generation and cumulative_energy > 0:
                    storage_outflow = min(needed_generation - present_generation, max_charge_rate, cumulative_energy)
                    cumulative_energy -= storage_outflow
                    system_output[i] += storage_outflow
                elif present_generation > needed_generation and cumulative_energy < starting_energy_stored:
                    storage_inflow = min(present_generation - needed_generation, max_charge_rate)
                    cumulative_energy = min(starting_energy_stored, cumulative_energy + storage_inflow)
                    system_output[i] -= storage_inflow

        return system_output
        
    def get_customer_not_supplied_probability(self, tech_output, kW_gen_data):
        # Check Loss of Load Probability for this tech set
        lost_load_hours = np.sum(tech_output < kW_gen_data)
        customer_not_supplied_probability = lost_load_hours / len(kW_gen_data)
        return customer_not_supplied_probability
    
    def get_EWOMP(self, system_output, kW_gen_data, hourly_EWOMP):
        successful_hours = np.where(system_output >= kW_gen_data)[0]
        return sum(hourly_EWOMP[hour] for hour in successful_hours)



        # # First determine how single-technologies setups would fare
        # for tech in Technology:
        #     number_of_systems = ceil(max(kW_gen_data) / self.POWER_OUTPUTS[tech])
        #     if tech is Technology.SOLAR_STORAGE and number_of_systems*self.SOLAR_STORAGE_POWER_OUTPUT < total_kW_gen:
        #         # If peak solar generation is enough but overall energy generation is not enough
        #         number_of_systems = max(number_of_systems, ceil(total_kW_gen / self.SOLAR_STORAGE_ENERGY_OUTPUT))

        #     tech_data = self.gather_tech_performance(tech, number_of_systems, total_kW_gen)

        #     self.tech_criteria_data.loc[f'{number_of_systems} {TECH_LABELS[tech]}' + ('s' if number_of_systems > 1 else '')] = tech_data
                

        # # Next, determine how two-technology setups would fare. One main technology, one for additional generation needed
        # for tech in Technology:
        #     tech1, tech2 = [option for option in Technology if option is not tech]

        #     # Tech1 as main generating option
        #     tech1_number_of_systems = max(kW_gen_data) // self.POWER_OUTPUTS[tech1]

        #     if tech1_number_of_systems == 0:
        #         continue

        #     tech1_kW_gen_data = np.copy(kW_gen_data)
        #     if tech1 is Technology.SOLAR_STORAGE:
        #         # Power output always stays under possible generation (depending on solar production in that hour)
        #         tech1_kW_gen_data = np.minimum(tech1_kW_gen_data, tech1_number_of_systems*self.SOLAR_OUTPUT)
        #         if tech1_number_of_systems*self.SOLAR_STORAGE_ENERGY_OUTPUT < sum(tech1_kW_gen_data):
        #             # If peak solar generation is enough but overall energy generation is not enough
        #             tech1_number_of_systems = max(tech1_number_of_systems, ceil(sum(tech1_kW_gen_data) / self.SOLAR_STORAGE_ENERGY_OUTPUT))
        #     else:
        #         # Power output always stays under possible generation (not time-dependent)
        #         tech1_kW_gen_data[tech1_kW_gen_data > tech1_number_of_systems*self.POWER_OUTPUTS[tech1]] = tech1_number_of_systems*self.POWER_OUTPUTS[tech1]

        #     tech2_kW_gen_data = kW_gen_data - tech1_kW_gen_data
        #     tech2_number_of_systems = ceil(max(tech2_kW_gen_data) / self.POWER_OUTPUTS[tech2])

        #     if tech2_number_of_systems == 0:
        #         continue

        #     tech1_data = self.gather_tech_performance(tech1, tech1_number_of_systems, sum(tech1_kW_gen_data))
        #     tech2_data = self.gather_tech_performance(tech2, tech2_number_of_systems, sum(tech2_kW_gen_data))
        #     combined_data = np.add(tech1_data, tech2_data)

        #     self.tech_criteria_data.loc[f'{tech1_number_of_systems} {TECH_LABELS[tech1]}' + ('s' if tech1_number_of_systems > 1 else '') + ' & ' +
        #         f'{tech2_number_of_systems} {TECH_LABELS[tech2]}' + ('s' if tech2_number_of_systems > 1 else '')] = combined_data
    
    def find_non_dominated_options(self):
        self.non_dominated_options = pareto.eps_sort([list(self.tech_criteria_data.itertuples())], list(self.tech_criteria_data.columns.map(self.tech_criteria_data.columns.get_loc).values + 1))
        column_list = ["Name", *self.tech_criteria_data.columns.values]
        # convert multi-dimension array to DataFrame
        self.non_dominated_options = DataFrame.from_records(self.non_dominated_options, columns=column_list, index="Name")
    
    def save(self, filepath):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        all_option_filepath = Path(filepath + "_all.csv")
        self.tech_criteria_data.to_csv(all_option_filepath)
        nd_option_filepath = Path(filepath + "_nd.csv")
        self.non_dominated_options.to_csv(nd_option_filepath)
        generated_option_filepath = Path(filepath + "_generated.csv")
        generated_data = concat([self.tech_criteria_data, self.CNSP_failing_tech_criteria_data, self.oversized_tech_criteria_data])
        generated_data.to_csv(generated_option_filepath)

        