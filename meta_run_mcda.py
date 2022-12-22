from run_mcda import main

seasons = ["winter", "spring", "summer", "fall"]

durations = ["short"]

# DATE_FINDER = {"winter": {"short": (8184,8220), "long": (8184,8256)}, "spring": {"short": (3264,3300), "long": (3264,3336)}, "summer": {"short": (4776,4812), "long": (4776,4848)}, "fall": {"short": (5760,5796), "long": (5760,5832)}}

RHs = {"RH0":2084, "RH2":2112}

load_sets = ["only", "small", "large"]

for rh in RHs.keys():
    for load_set in load_sets:
        for season in seasons:
            for duration in durations:
                constructed_args = [
                                    f"{rh}",
                                    f"{load_set}",
                                    f"{season}",
                                    f"{duration}",
                                    "500000",
                                    "../Data/TPF Output/R1-12.47-2-with-RHs/",
                                    "--svifilepath=../../Research/Data/richmond_ca_svi_values_r1_1247_2.csv",
                                    "--plotfolder=../../Part A/Images/Tradeoffs",
                                    "--csvfolder=../../Part A/Data/R1-12.47-2-with-RHs/",
                                ]
                
                main(constructed_args)