This code will undertake the capacity market optimization on the 24-bus European test system

The European system can be found on:

https://zenodo.org/record/35177

Python files included:

- "main.py" executes the optimization
- "loaddata_EU" loads data from csv files
- "dayahead_optclass" contains the day ahead optimization code
- "optimization.py" runs the day ahead optimization class and extracts results 
- "capmarket_opt" runs the capacity market optimization and extract results
- "capmarket_optclass" contains the capacity market optimization code
- "capmarket_function" runs capacity market code and sends results to "main" 

csv files included:
- "generators.csv" contains information on generators
- "lines.csv" contains information on all lines
- "nodes.csv" contains information on all nodes
- "load.csv" contains information on the load
- "ones.csv" 1-filled matrix
- "solar_cells.csv" contains sizes of solar cells
- "solar.csv" contains solar production profiles
- "wind_turbines.csv" contains sizes of wind turbines
- "wind.csv" contains wind turbine production profiles
- "generatorsinvestment.csv" contains information on generators used to undertake investment loop
- "transmissioncapacity.csv" contains information on transmission capacity between countries

Undertaking simulations:

- Download the files into the same directory
- The script "main.py" is run to excecute the optimization
- The returned csv file "revenue_cost_gen_CM.csv" holds the results of the optimization for each generator
- The csv file "generators.csv" placed in the map "generators_start" must be copied into the directory
- The optimization is run until their is just as many generators in dataframe df_generators as in gen_dataframe
  (This indicates that the steady state is reached without further investment or shut down of power plants)

How to adjust parameters in the simulations:

- Wind production: Adjusted in dayahead_optclass under self.data.windscale
- Solar production: Adjusted in dayahead_optclass under self.data.solarscale
- Hydro capacity factor can be adjusted in "dayahead_optclass" under self.data.hydrocoeff
- The price-cap in the day-ahead market can be adjusted in "dayahead_optclass" under self.data.VoLL 
- The reserve margin can be adjusted in capmarket_optclass under self.data.reservemargin

Cost estimates on generators:

- The cost estimates can be found in the report. However, gas generators have following costs: Below 30 MW a cost estimate on GCT is used, between 30 MW and 100 MW a SCGT cost estimate is used, and above 100 MW a CCGT cost estimate.



