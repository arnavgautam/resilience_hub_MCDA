import argparse
from pathlib import Path

from csv_reader import CsvReader
from rh_option_plotter import RHOptionPlotter
from technology_enumerator import TechnologyEnumerator
from technology_evaluator import TechnologyEvaluator
parser = argparse.ArgumentParser()

parser.add_argument("case")
parser.add_argument("start")
parser.add_argument("end")
parser.add_argument("upfrontcostceiling")
parser.add_argument("datafolder")
parser.add_argument("--plotfilepath", required=False)
args = parser.parse_args()

case = args.case
start = int(args.start)
end = int(args.end)
upfrontcostceiling = int(args.upfrontcostceiling)
datafolder = Path(args.datafolder)
plotfilepath = Path(args.plotfilepath) if args.plotfilepath is not None else None

print("========================")
print("BEGINNING MULTI-CRITERIA DECISION ANALYSIS")
print()

print("Enumerating technologies")
tech_enumerator = TechnologyEnumerator()
tech_enumerator.enumerate_tech_sets(upfrontcostceiling)

print("Reading input files...")
csv_reader = CsvReader(case, datafolder, start, end)
csv_reader.compile_EWOMP_data()
csv_reader.compile_power_timeseries()

print()
print("Evaluating technologies...")
tech_evaluator = TechnologyEvaluator()
tech_evaluator.compile_tech_outputs(start, end)
failed_systems_CNSPs = tech_evaluator.evaluate_technologies(csv_reader.gen_data_list, csv_reader.hourly_EWOMP, tech_enumerator.tech_sets)
print(f"Eliminated {len(failed_systems_CNSPs)} systems who have greater than acceptable Customer-Not-Supplied-Probability")

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