import argparse
from pathlib import Path

from csv_reader import CsvReader
from rh_option_plotter import RHOptionPlotter
from technology_evaluator import TechnologyEvaluator
parser = argparse.ArgumentParser()

parser.add_argument("case")
parser.add_argument("start")
parser.add_argument("end")
parser.add_argument("datafolder")
parser.add_argument("--plotfilepath", required=False)
args = parser.parse_args()

case = args.case
start = int(args.start)
end = int(args.end)
datafolder = Path(args.datafolder)
plotfilepath = Path(args.plotfilepath) if args.plotfilepath is not None else None

print("========================")
print("BEGINNING MULTI-CRITERIA DECISION ANALYSIS")
print()

print("Reading input files...")
csv_reader = CsvReader()
csv_reader.compile_power_timeseries(case, start, end, datafolder)

print()
print("Enumerating and evaluating technologies...")
tech_evaluator = TechnologyEvaluator()
tech_evaluator.compile_solar_output(start, end)
tech_evaluator.enumerate_and_evaluate_technologies(csv_reader.gen_data_list)

print()
print("Finding non-dominated options among technology options...")
tech_evaluator.find_non_dominated_options()

print()
print("Plotting non-dominated options...")
plotter = RHOptionPlotter()
plotter.plot(tech_evaluator.non_dominated_options)
if plotfilepath is not None:
    plotter.save(plotfilepath)

print()
print("COMPLETE")
print("========================")