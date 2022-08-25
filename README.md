# resilience_hub_MCDA
Perform a Multi-Criteria Decision Analysis for the performance of Resilience Hubs as providers of electricity during power outages

Run the `run_mcda.py` file to do the following:
- Read in CSV files with power values for the slack bus, system loads, and resilience hub generator (modeled as a negative load) of a distribution network
- Determine the equipment options that can supply the loads
- Calculate the economics and environmental impact of the power output for each equipment option
- Determine which options are non-dominated
- Plot the multi-criteria performances of the non-dominated options

`run_mcda.py` takes in the following arguments:
- case = The name of the case, assumed to be part of the data file naming convention
- start = The first hour of the year to consider (0-8759)
- end = The last hour of the year to consider (0-8759)
- datafolder = The folder containing the data files
- plotfilepath = The location to save the plot HTML
  - optional
  - the plot goes to a `temp-plot.html` in the working directory if plotfilepath is not provided. this file is overridden with subsequent runs
