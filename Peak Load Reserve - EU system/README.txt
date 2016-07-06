This code will undertake the peak load reserve (PLR) optimization on the European test system

The European system can be found on:

https://zenodo.org/record/35177

Python files included:

- "main.py" executes the optimization
- "data_24bus" loads data from csv files
- "dayahead_optclass" contains the day ahead optimization code
- "optimization.py" runs the day ahead optimization class and extracts results 
- "PLR_optimization" runs the PLR optimization and extract results
- "PLR_optclass" contains the PLR tendering process optimization code
- "PLR_function" runs PLR code and sends results to "main" 

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
- "rev_cost_gen" zero-filled matrix
- "rev_cost_gen_PLR" zero-filled matrix

Undertaking simulations:

- Download the files into the same directory
- The script "main.py" is run to excecute the optimization
- The returned csv file "revenue_cost_gen_PLR.csv" holds the results of the optimization for each generator
- The csv file "generators.csv", "revenue_cost_gen" and "revenue_cost_gen_PLR" placed in the map "generators_start" must be copied into the directory
  (this is done before each optimization run at a certain PLR size and activation price)
- The optimization is run until there is just as many generators in the dataframe df_generators as in Gen_dataframe
  (This indicates that the steady state is reached without further investment or shut down of power plants)

How to adjust parameters in the simulations:

- Wind production: Adjusted in dayahead_optclass under self.data.windscale
- Solar production: Adjusted in dayahead_optclass under self.data.solarscale
- Hydro capacity factor can be adjusted in "dayahead_optclass" under self.data.hydrocoeff
- The price-cap in the day-ahead market can be adjusted in "dayahead_optclass" under self.data.VoLL 
- The reserve margin can be adjusted in PLR_optclass under self.data.reservemargin
- The size of the PLR can be changed in PLR_optclass under self.data.plrdemand
- The activation price of the PLR can be changed in PLR_function under ActivationPrice
- The investment loop can be enabled by removing the # under the text "The activation, deactivation and investment analysis can be enabled here:"

Results displayed:
- Solar penetration and cost of solar energy
- Wind penetration and cost of wind energy
- df_generators dataframe showing information on generators
- Gen_dataframe sowing information on generators after the code is executed




