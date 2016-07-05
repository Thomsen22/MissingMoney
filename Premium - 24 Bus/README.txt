This code will undertake the premium optimization on the 24-bus IEEE test system

The IEEE 24-bus system can be found on:

https://www.researchgate.net/
file.PostFileLoader.html?id=5654318d6307d974148b45a9&assetKey=AS%
3A299250492690433%401448358285630.

Python files included:

- "main.py" executes the optimization
- "data_24bus" loads data from csv files
- "dayahead_optclass" contains the day ahead optimization code
- "optimization.py" runs the day ahead optimization class and extracts results 
- "premium_optimization" runs the premium optimization and determines the premium

csv files included:
- "generators.csv" contains information on generators
- "lines.csv" contains information on all lines
- "load.csv" contains information on the load
- "load_rel.csv" distributes the load to respective nodes
- "solar_cells.csv" contains sizes of solar cells
- "solar_prod.csv" contains solar production profiles
- "wind_turbines.csv" contains sizes of wind turbines
- "wind_prod.csv" contains wind turbine production profiles
- "rev_cost_gen" contains starting point for the simulation

Undertaking simulations:

- Download the files into the same directory
- The script "main.py" is run to excecute the optimization
- The returned csv file "revenue_cost_gen.csv" holds the results of the optimization for each generator
- The csv file "generators.csv" and "revenue_cost_gen" placed in the map "generators_start" must be copied into the directory
  (this is done before each optimization run)
- The optimization is run until there is just as many generators in the dataframe df_generators as in gen_dataframe
  (This indicates that the steady state is reached without further investment or shut down of power plants)

How to adjust parameters in the simulations:

- Wind production: The size of the wind turbines can be adjusted in wind_turbines.csv at node n1, n3, n5, n16, n21 and n23
- Solar production: The size of the solar cells can be adjusted in solar_cells.csv at node n1, n3, n5, n16, n21 and n23
- Winter and summer profiles of solar production, wind production and load profiles can be found in the respective maps.

(The data is from 01-05-2015 to 01-11-2015 and 07-06-215 to 07-12-2015 for the western part of Denmark.
 Data can be found on http://energinet.dk/DA/El/Engrosmarked/Udtraek-af-markedsdata/Sider/default.aspx)

- Hydro capacity factor can be adjusted in "dayahead_optclass" under self.data.hydrocoeff
- The price-cap in the day-ahead market can be adjusted in "dayahead_optclass" under self.data.VoLL 
- The reserve margin can be adjusted in "main"
- The selected generator type can be changed in "premium_function" under chosengenerator and typegenerator

Results displayed:
- Solar penetration and cost of solar energy
- Wind penetration and cost of wind energy
- df_generators dataframe showing information on generators
- gen_dataframe sowing information on generators after the code is executed




