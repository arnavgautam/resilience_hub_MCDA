from run_mcda import main

seasons = ["winter", "spring", "summer", "fall"]

durations = ["short"]

RHs = {"RH0":2084}#", RH2":2112}

load_sets = ["large"]

def yield_constructed_args():
    for rh in RHs.keys():
        for load_set in load_sets:
            for season in seasons:
                for duration in durations:
                    constructed_args = [
                                        f"{rh}",
                                        f"{load_set}",
                                        f"{season}",
                                        f"{duration}",
                                        "510000",
                                        "../Data/TPF Output/R1-12.47-2-with-RHs/",
                                        "--svifilepath=../../Research/Data/richmond_ca_svi_values_r1_1247_2.csv",
                                        "--plotfolder=../../Part A/Images/Tradeoffs",
                                        "--csvfolder=../../Part A/Data/R1-12.47-2-with-RHs/R_and_R",
                                    ]
                    yield constructed_args

for constructed_args in yield_constructed_args():
    main(constructed_args)