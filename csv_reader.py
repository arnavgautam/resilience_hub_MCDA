from pathlib import Path
from pandas import read_csv

class CsvReader():
    def __init__(self):
        self.hourly_gen = dict()
        self.hourly_load = dict()

    def compile_power_timeseries(self, casename, start, end, data_folder: Path):
        for hour in range(start,end):
            filepath = data_folder.joinpath(f"{casename}_{hour}_power.csv")
            power_data = read_csv(filepath)
            gen_bus, gen_type, gen_P, gen_Q  = power_data[power_data['P(MW)'] == power_data.min()['P(MW)']].iloc[0]
            slack_bus, slack_type, slack_P, slack_Q  = power_data[power_data['name'] == 'Slack'].iloc[0]
            total_gen = complex(gen_P, gen_Q) + complex(slack_P, slack_Q)
            self.hourly_gen[hour] = total_gen
            loads = power_data[(power_data['bus']!= gen_bus) & (power_data['bus']!= slack_bus)]
            loads['complex_load'] = loads.apply(lambda load: complex(load['P(MW)'], load['Q(MVar)']), axis=1)
            total_load = sum(loads['complex_load'])
            self.hourly_load[hour] = total_load

        self.gen_data_list = [abs(generation) for generation in self.hourly_gen.values()]

