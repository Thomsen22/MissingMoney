# Python standard modules
import numpy as np
import gurobipy as gb
import networkx as nx
from collections import defaultdict
import pandas as pd
import math
# Own modules
import loaddataEU as data

class expando(object):
    '''
        # A class for Day Ahead market clearing
    '''
    pass

class DayAhead:
    def __init__(self):       
        self.data = expando()
        self.variables = expando()
        self.constraints = expando()
        self._load_data()
        self._build_model()
            
    def optimize(self):
        self.model.optimize()
        
        m = self.model        
        generators = self.data.generators
        times = self.data.times
        gprod = self.variables.gprod        
        
        GeneratorProduction = pd.DataFrame(index = times, data = {g: [self.variables.gprod[g,t].x for t in times] for g in generators.index})

        GeneratorProductionDict = {}
        for t in times:
            for g in np.arange(len(generators.index)):
                GeneratorProductionDict[GeneratorProduction.columns[g], t] = GeneratorProduction.ix[GeneratorProduction.index[t], GeneratorProduction.columns[g]]

        hydroconstr = {}
        for t in times:
            for g in generators.index:
                if generators.primaryfuel[g] == 'Hydro':
                    hydroconstr[g, t] = GeneratorProductionDict[g, t] 
                 
        self.constraints.hydroconstr = {}
        for t in times:
            for g in generators.index:
                if generators.primaryfuel[g] == "Hydro":
                    self.constraints.hydroconstr[g, t] = m.addConstr(gprod[g, t], gb.GRB.EQUAL, hydroconstr[g, t])
                
        self.model.update()

        self.model.reset()

        self.model.optimize()

    def _load_data(self):
        self.data.consumption, self.data.windproduction, self.data.solarproduction = data.load_temporary()
        self.data.generators = data.load_generators()
        self.data.network = data.load_network()
        self.data.df_lines = data.load_lines()
        self.data.nodes = self.data.network.nodes()
        self.data.times = np.arange(len(self.data.consumption.index)) 
        self.data.country = self.data.generators['country'].unique().tolist()
        self.data.hydrocoeff = 0.70 
        self.data.windscale = 0.15 # Between 0 and 1
        self.data.solarscale = 0.15 # Between 0 and 1
        
        # Assigning each node to a country (price-area, zone)
        country = nx.get_node_attributes(self.data.network, 'country')
        country = pd.Series(country, name='Zone')
        country = country.reset_index()
        country = country.rename(columns={'index': 'Node'})
        self.data.countries = country
        # Using defaultdict
        zones_nodes = country[['Zone','Node']].values.tolist()
        self.data.nodes_for_zones = defaultdict(list)
        for Node,Zone in zones_nodes:
            self.data.nodes_for_zones[Node].append(Zone)
              
        times = self.data.times
        nodes = self.data.nodes
        consumption = self.data.consumption
        windproduction = self.data.windproduction
        solarproduction = self.data.solarproduction
        self.data.zones = self.data.country
        zones = self.data.zones        
        
        # Assigning load to each node and time (and zonal consumption)
        self.data.nodalconsumption = {}
        for t in times:
            for n in np.arange(len(nodes)):
                self.data.nodalconsumption[consumption.columns[n], t] = consumption.ix[consumption.index[t], consumption.columns[n]]
        
        self.data.zonalconsumption = {}
        for t in times:
            for z in zones: 
                self.data.zonalconsumption[z,t] = sum(self.data.nodalconsumption[n,t] for n in self.data.nodes_for_zones[z])        

        self.data.df_zonalconsumption = pd.DataFrame(index = times, data = {z: [self.data.zonalconsumption[z,t] for t in times] for z in zones})

        # Assigning wind production to each node (assigned to zones later) 
        self.data.windprod = {}
        for t in times:
            for n in np.arange(len(nodes)):
                self.data.windprod[windproduction.columns[n], t] = windproduction.ix[windproduction.index[t], windproduction.columns[n]] 
        
        # Assigning wind production to each node (assigned to zones later) 
        self.data.solarprod = {}
        for t in times:
            for n in np.arange(len(nodes)):
                self.data.solarprod[solarproduction.columns[n], t] = solarproduction.ix[solarproduction.index[t], solarproduction.columns[n]]         
        
        # Generator marginal cost
        self.data.generatorcost = {}
        for g in self.data.generators.index:
            self.data.generatorcost[g] = self.data.generators.lincost[g]
                
        # Assigning generators to specific zone
        country_generator = self.data.generators[['country','name']].values.tolist()
        self.data.gens_for_country = defaultdict(list) 
        for country, generator in country_generator:
            self.data.gens_for_country[country].append(generator)         
        
        # Lines and lineinfo
        self.data.lines = list(self.data.df_lines.index)

        # VOLL assigned to each time
        self.data.VoLL = {}
        for t in times:
            self.data.VoLL[t] = 3000 # Price cap is 3000 € in Nordpool Spot 
        
        
    def _build_model(self):
        self.model = gb.Model()
        self._build_variables()
        self._build_objective()
        self._build_constraints()
        
    def _build_variables(self):
        m = self.model
        
        times = self.data.times
        lines = self.data.lines
        lineinfo = self.data.df_lines
        generators = self.data.generators
        windproduction = self.data.windprod
        solarproduction = self.data.solarprod
        nodes_for_zones = self.data.nodes_for_zones
        zones = self.data.zones
        nodalconsumption = self.data.nodalconsumption
 
        # Capacity on generators 
        self.variables.gprod = {}
        for t in times:
            for g in generators.index:
                self.variables.gprod[g, t] = m.addVar(lb = 0, ub = generators.capacity[g])
               
        # Loadshed assigned to each zone in the system at each time
        self.variables.loadshed = {}
        for t in times:
            for z in zones:
                self.variables.loadshed[z, t] = m.addVar(lb = 0, ub = sum(nodalconsumption[n,t] for n in nodes_for_zones[z]))
                       
        # Wind production assigned to each node in the system at each time
        self.variables.windprod = {}
        for t in times:
            for z in zones:
                self.variables.windprod[z, t] = m.addVar(lb = 0, ub = sum(windproduction[n,t] for n in nodes_for_zones[z]) * self.data.windscale)

        # Solar production assigned to each node in the system at each time
        self.variables.solarprod = {}
        for t in times:
            for z in zones:
                self.variables.solarprod[z, t] = m.addVar(lb = 0, ub = sum(solarproduction[n,t] for n in nodes_for_zones[z]) * self.data.solarscale)

        # Export variable from each node at each time, (-infinity < export < infinity)
        self.variables.export = {}
        for t in times:
            for z in zones:
                self.variables.export[z, t] = m.addVar(lb = -math.inf, ub = math.inf)

        # The linelimits between zones are inserted        
        self.variables.linelimit = {}
        for t in times:
            for l in lines: 
                self.variables.linelimit[l, t] = m.addVar(lb=-lineinfo['capacity'][l], ub=lineinfo['capacity'][l])
        
        m.update()        
        
    def _build_objective(self):

        times = self.data.times
        zones = self.data.zones
        generators = self.data.generators
        loadshed = self.variables.loadshed
        gprod = self.variables.gprod
        generatorcost = self.data.generatorcost
        VoLL = self.data.VoLL
        
        self.model.setObjective(

            gb.quicksum(generatorcost[g] * gprod[g, t] for g in generators.index for t in times)            

            + gb.quicksum(VoLL[t] * loadshed[z, t] for z in zones for t in times)
            
            ,gb.GRB.MINIMIZE)

       
    def _build_constraints(self):
        m = self.model
        
        times = self.data.times
        zones = self.data.zones
        lines = self.data.lines
        linelimit = self.variables.linelimit
        Load = self.data.zonalconsumption
        loadshed = self.variables.loadshed
        gprod = self.variables.gprod
        gens_for_country = self.data.gens_for_country
        export = self.variables.export
        windprod = self.variables.windprod
        solarprod = self.variables.solarprod
        generators = self.data.generators
        gprod = self.variables.gprod
        hydrocoeff = self.data.hydrocoeff

        # Power Balance constraint in each zone at each time
        self.constraints.powerbalance = {}
        for z in zones:
            for t in times:
                self.constraints.powerbalance[z, t] = m.addConstr(
                    
                    gb.quicksum(gprod[g, t] for g in gens_for_country[z])
                    
                    + windprod[z, t] + solarprod[z, t]
                    
                    ,gb.GRB.EQUAL,
                    
                    (Load[z, t] - loadshed[z, t]) + export[z, t])
      
          
        # Export constraint at each node at each time
        self.constraints.exporting = {}
        for t in times:
            for z in zones:
                self.constraints.exporting[z, t] = m.addConstr(
                   
                   export[z, t], gb.GRB.EQUAL,

                   gb.quicksum(linelimit[l, t] for l in lines if l[0] == z) - gb.quicksum(linelimit[l, t] for l in lines if l[1] == z))

        
        # Hydro constraint                  
        self.constraints.hydro = {}
        for g in generators.index:
            if generators.primaryfuel[g] == "Hydro":
                if not (generators.country[g] == "MKD" or generators.country[g] == "MNE" or generators.country[g] == "HRV"):
                    self.constraints.hydro[g] = m.addConstr(
                
                        gb.quicksum(gprod[g, t] for t in times), gb.GRB.LESS_EQUAL,

                        hydrocoeff * generators.capacity[g] * len(times))
                    
    
