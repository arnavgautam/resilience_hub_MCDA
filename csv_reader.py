from pathlib import Path
from random import choices, random
from pandas import read_csv

class CsvReader():
    def __init__(self, casename, data_folder: Path, start, end):
        self.casename = casename
        self.data_folder = data_folder
        self.start = start
        self.end = end
        self.hourly_gen = dict()
        self.hourly_load = dict()
        self.hourly_EWOMP = dict()

    def compile_EWOMP_data(self):
        SVI_filepath = self.data_folder.joinpath(f"{self.casename}_SVI.csv")
        if not SVI_filepath.is_file():
            self.generate_SVI_data()
        SVI_data = read_csv(SVI_filepath)
        self.network_data = SVI_data[["bus", "SVI"]]
        priorities_filepath = self.data_folder.joinpath(f"{self.casename}_priorities.csv")
        if not priorities_filepath.is_file():
            self.generate_priorities_data()
        priorities_data = read_csv(priorities_filepath)
        self.network_data["priorities"] = priorities_data["priorities"]
        self.network_data["EWOMP"] = self.network_data["SVI"] / self.network_data["priorities"]
        self.EWOMP_data = self.network_data[["bus", "EWOMP"]]
        self.EWOMP_data.set_index("bus", inplace=True)

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
        network_data["priorities"] = choices(population=range(1, 10), k=len(network_data))
        priorities_data = network_data[["bus", "priorities"]]
        priorities_filepath = self.data_folder.joinpath(f"{self.casename}_priorities.csv")
        priorities_data.to_csv(priorities_filepath)

    def compile_power_timeseries(self):
        for hour in range(self.start, self.end):
            filepath = self.data_folder.joinpath(f"{self.casename}_{hour}_power.csv")
            power_data = read_csv(filepath)
            gen_bus, gen_type, gen_P, gen_Q  = power_data[power_data['P(MW)'] == power_data.min()['P(MW)']].iloc[0]
            slack_bus, slack_type, slack_P, slack_Q  = power_data[power_data['name'] == 'Slack'].iloc[0]
            total_gen = complex(gen_P, gen_Q) + complex(slack_P, slack_Q)
            self.hourly_gen[hour] = total_gen
            loads = power_data[(power_data['bus']!= gen_bus) & (power_data['bus']!= slack_bus)]
            loads['complex_load'] = loads.apply(lambda load: complex(load['P(MW)'], load['Q(MVar)']), axis=1)
            loads.set_index("bus", inplace=True)
            self.hourly_EWOMP[hour] = sum(abs(loads['complex_load'] * self.EWOMP_data["EWOMP"]).dropna())
            total_load = sum(loads['complex_load'])
            self.hourly_load[hour] = total_load

        self.gen_data_list = [abs(generation) for generation in self.hourly_gen.values()]
        

