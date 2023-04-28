from pathlib import Path
from random import choices, random
from pandas import DataFrame, merge, read_csv
from numpy.random import rand

class CsvReader():
    def __init__(self, casename, data_folder: Path, start, end, svifilepath: Path):
        self.casename = casename
        self.data_folder = data_folder
        self.start = start
        self.end = end
        self.svifilepath = svifilepath
        self.hourly_gen = dict()
        self.hourly_loads = DataFrame()
        self.hourly_EWOMP = list()
        self.violated_equipment_ratings = dict()
        self.prioritiesfilepath = self.data_folder.parent.joinpath(f"R1-12.47-2_priorities.csv")            
    
    def compile_EWOMP_data(self, alpha, beta):
        SVI_filepath = self.data_folder.joinpath(f"{self.casename}_SVI.csv")
        if not SVI_filepath.is_file():
            if self.svifilepath is not None and self.svifilepath.is_file():
                SVI_data = read_csv(self.svifilepath)
                SVI_data.set_index("bus", inplace=True)
                SVI_data.to_csv(SVI_filepath)
            else:
                self.generate_SVI_data()
        SVI_data = read_csv(SVI_filepath)
        SVI_data.set_index("bus", inplace=True)
        # self.network_data = SVI_data
        priorities_filepath = self.data_folder.joinpath(f"{self.casename}_priorities.csv")
        if not priorities_filepath.is_file():
            if self.prioritiesfilepath is not None and self.prioritiesfilepath.is_file():
                priorities_data = read_csv(self.prioritiesfilepath)
                priorities_data.set_index("bus", inplace=True)
                priorities_data.to_csv(priorities_filepath)
            else:
                self.generate_priorities_data()
        priorities_data = read_csv(priorities_filepath)
        priorities_data.set_index("bus", inplace=True)
        self.network_data = merge(SVI_data, priorities_data, how='inner', on='bus', suffixes=("", ""))
        # self.network_data["priorities"] = priorities_data["priorities"]
        self.network_data["EWOMP_factor"] = alpha * self.network_data["SVI"] + beta * self.network_data["priorities"]
        self.EWOMP_factors = self.network_data[["EWOMP_factor"]]

    def generate_SVI_data(self):
        hour_one_filepath = self.data_folder.joinpath(f"{self.casename}_{self.start}_power.csv")
        network_data = read_csv(hour_one_filepath)
        network_data["SVI"] = random()
        SVI_data = network_data[["bus", "SVI"]]
        SVI_filepath = self.data_folder.joinpath(f"{self.casename}_SVI.csv")
        SVI_data.to_csv(SVI_filepath)

    def generate_priorities_data(self):
        hour_one_filepath = self.data_folder.joinpath(f"{self.casename}_{self.start}_power.csv")
        network_data = read_csv(hour_one_filepath)
        network_data["priorities"] = rand(len(network_data),)
        priorities_data = network_data[["bus", "priorities"]]
        priorities_data.set_index("bus", inplace=True)
        priorities_filepath = self.data_folder.joinpath(f"{self.casename}_priorities.csv")
        priorities_data.to_csv(priorities_filepath)

    def compile_power_timeseries(self):
        for hour_idx in range(self.end-self.start):
            hour = hour_idx + self.start
            filepath = self.data_folder.joinpath(f"{self.casename}_{hour}_power.csv")

            loads = self.get_loads_data(filepath, hour)
            # load_EWOMP = sum(abs(loads["complex_load"]).multiply(self.EWOMP_data["EWOMP"], fill_value=0))
            # self.hourly_EWOMP.append(load_EWOMP)
            # total_load = sum(loads['complex_load'])
            self.hourly_loads[hour_idx] = loads["complex_load"]

        self.gen_data_list = [abs(generation) for generation in self.hourly_gen.values()]
    
    def get_loads_data(self, filepath, hour, save_data = True):
        self.violated_equipment_ratings[hour] = False
        with open(filepath, "r") as f:
            file_text = f.readlines()
            # Check for power flow failure
            if file_text[0] == "FAILURE":
                return None

            # Check for equipment constraint violation
            if "VIOLATED EQUIPMENT RATINGS" in file_text:
                self.violated_equipment_ratings[hour] = True

        # If no violations occur
        try:
            power_data = read_csv(filepath, skipfooter=(1 if self.violated_equipment_ratings[hour] else 0))
        except Exception as e:
            print(e)
            return None
        gen_bus, gen_type, gen_P, gen_Q  = power_data[power_data['P(MW)'] == power_data.min()['P(MW)']].iloc[0]
        slack_bus, slack_type, slack_P, slack_Q  = power_data[power_data['name'] == 'Slack'].iloc[0]
        if gen_bus == slack_bus:
            total_gen = complex(gen_P, gen_Q)
        else:
            total_gen = complex(gen_P, gen_Q) + complex(slack_P, slack_Q)
        if save_data:
            self.hourly_gen[hour] = total_gen
        loads = DataFrame(power_data[(power_data['P(MW)'] >= 0) & (power_data['Q(MVar)'] >= 0)])
        loads.loc[:,'complex_load'] = loads.apply(lambda load: complex(load['P(MW)'], load['Q(MVar)']), axis=1)
        loads.set_index("bus", inplace=True)
        return loads
    
    def save(self, suffix):
        power_df = DataFrame(data=self.gen_data_list, index=range(self.start, self.end))
        power_df.to_csv(self.data_folder.joinpath(f"{self.casename}_{suffix}_power_timeseries.csv"))
        

