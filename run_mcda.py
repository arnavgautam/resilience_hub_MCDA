import argparse
from pathlib import Path

from csv_reader import CsvReader
from rh_option_plotter import RHOptionPlotter
from technology_enumerator import TechnologyEnumerator
from technology_evaluator import TechnologyEvaluator

def main(raw_args=None):
    parser = argparse.ArgumentParser()

    parser.add_argument("RH")
    parser.add_argument("load_set")
    parser.add_argument("season")
    parser.add_argument("duration")
    parser.add_argument("upfrontcostceiling")
    parser.add_argument("datafolder")
    parser.add_argument("--svifilepath", required=False)
    parser.add_argument("--plotfolder", required=False)
    parser.add_argument("--csvfolder", required=False)
    parser.add_argument("--alpha", required=False)
    parser.add_argument("--beta", required=False)
    parser.add_argument("--gamma", required=False)
    args = parser.parse_args(raw_args)

    DATE_FINDER = {"winter": {"short": (8184,8220), "long": (8184,8256)}, "spring": {"short": (3264,3300), "long": (3264,3336)}, "summer": {"short": (4776,4812), "long": (4776,4848)}, "fall": {"short": (5760,5796), "long": (5760,5832)}}

    RH = args.RH
    load_set = args.load_set
    season = args.season
    duration = args.duration
    start, end = DATE_FINDER[season][duration]
    case = f"{RH}_{load_set}_{season}_max"
    upfrontcostceiling = int(args.upfrontcostceiling)
    datafolder = Path(args.datafolder)
    datafolder = datafolder.joinpath(case)
    svifilepath = Path(args.svifilepath) if args.svifilepath is not None else None
    plotfilepath = Path(args.plotfolder).joinpath(f"{case}_{duration}.html") if args.plotfolder is not None else None
    csvfilepath = f"{args.csvfolder}{case}_{duration}" if args.csvfolder is not None else None
    alpha = float(args.alpha) if args.alpha is not None else 0.5
    beta = float(args.beta) if args.beta is not None else 0.5
    gamma = float(args.gamma) if args.gamma is not None else 0.5

    # parser.add_argument("case")
    # parser.add_argument("start")
    # parser.add_argument("end")
    # parser.add_argument("upfrontcostceiling")
    # parser.add_argument("datafolder")
    # parser.add_argument("--svifilepath", required=False)
    # parser.add_argument("--plotfilepath", required=False)
    # parser.add_argument("--csvfilepath", required=False)
    # args = parser.parse_args()

    # case = args.case
    # start = int(args.start)
    # end = int(args.end)
    # upfrontcostceiling = int(args.upfrontcostceiling)
    # datafolder = Path(args.datafolder)
    # svifilepath = Path(args.svifilepath) if args.svifilepath is not None else None
    # plotfilepath = Path(args.plotfilepath) if args.plotfilepath is not None else None
    # csvfilepath = args.csvfilepath if args.csvfilepath is not None else None

    print("========================")
    print("BEGINNING MULTI-CRITERIA DECISION ANALYSIS")
    print()

    print("Enumerating technologies")
    tech_enumerator = TechnologyEnumerator()
    tech_enumerator.enumerate_tech_sets(upfrontcostceiling)

    print("Reading input files...")
    csv_reader = CsvReader(case, datafolder, start, end, svifilepath)
    csv_reader.compile_EWOMP_data(alpha, beta)
    csv_reader.compile_power_timeseries()
    # csv_reader.save(suffix=csvfilepath.split("_")[-1])

    print()
    print("Evaluating technologies...")
    tech_evaluator = TechnologyEvaluator(CNSP_THRESHOLD=0.1)
    tech_evaluator.compile_tech_outputs(start, end)
    failed_systems_CNSPs = tech_evaluator.evaluate_technologies(csv_reader.gen_data_list, csv_reader.hourly_loads, csv_reader.EWOMP_factors, tech_enumerator.tech_sets, gamma)
    print(f"Eliminated {len(failed_systems_CNSPs)} systems who have greater than acceptable Customer-Not-Supplied-Probability")

    print()
    print("Finding non-dominated options among technology options...")
    tech_evaluator.find_non_dominated_options(epsilons=None)#[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
    if csvfilepath is not None:
        tech_evaluator.save(csvfilepath)

    # print()
    # print("Plotting non-dominated options...")
    # plotter = RHOptionPlotter()
    # plotter.plot(tech_evaluator.non_dominated_options, no_sox_no2=True)
    # if plotfilepath is not None:
    #     plotter.save(plotfilepath)

    print()
    print("COMPLETE")
    print("========================")

if __name__ == "__main__":
    main()