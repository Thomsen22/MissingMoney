# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 14:10:06 2016

@author: Søren
"""

# Python standard modules
import numpy as np
import gurobipy as gb
import networkx as nx
from collections import defaultdict
import pandas as pd
# Own modules
import Data_24Bus as data

# This class makes the DA market clearing using zonal prices.

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
        m = self.model
        m.params.Presolve = 1
        m.params.ZeroObjNodes = 1000
        
        self.model.optimize()
        mf = self.model.fixed()
        mf.optimize()
        
        times = self.data.times
        zones = self.data.zones
        
        timezones = list(range(0,len(times)*len(zones)))
        
        Constraintname = {}
        for z in timezones:
            Constraintname[z] = "R{s}".format(s=z)
           
        self.data.MarketPrice = {}
        for z in timezones: 
            self.data.MarketPrice[z] = mf.getConstrByName('{s}'.format(s=Constraintname[z])).pi
        
 
    def _load_data(self):
        self.data.consumption = data.load()
        windproduction = data.windprod()
        self.data.windproduction = windproduction
        self.data.generators = data.load_generators()
        self.data.network = data.load_network()
        self.data.nodes = self.data.network.nodes()
        self.data.times = np.arange(len(self.data.consumption.index))
        self.data.country = nx.get_node_attributes(self.data.network, 'country')
        self.data.hydrocoeff = 0.5
        # Assigning each node to a country (price-area)
        country = nx.get_node_attributes(self.data.network, 'country')
        country = pd.Series(self.data.country, name='Zone')
        country = country.reset_index()
        country = country.rename(columns={'index': 'Node'})
        self.data.countries = country
        # Using defaultdict
        zones_nodes = country[['Zone','Node']].values.tolist()
        self.data.nodes_for_zones = defaultdict(list)
        for Node,Zone in zones_nodes:
            self.data.nodes_for_zones[Node].append(Zone)
        
        # Assigning load to each node and time (and zonal consumption)
        times = self.data.times
        nodes = self.data.nodes
        consumption = self.data.consumption
        windproduction = self.data.windproduction
        self.data.zones = ['Z1', 'Z2', 'Z3']
        zones = self.data.zones        
        
        self.data.nodalconsumption = {}
        for t in times:
            for n in np.arange(len(nodes)):
                self.data.nodalconsumption[consumption.columns[n], t] = consumption.loc[consumption.index[t], consumption.columns[n]]
        
        self.data.zonalconsumption = {}
        for t in times:
            for z in zones: 
                self.data.zonalconsumption[z,t] = sum(self.data.nodalconsumption[n,t] for n in self.data.nodes_for_zones[z])        
        
        # Assigning wind production to each node (assigned to zones later) 
        self.data.windprod = {}
        for t in times:
            for n in np.arange(len(nodes)):
                self.data.windprod[windproduction.columns[n], t] = windproduction.loc[windproduction.index[t], windproduction.columns[n]] 
        
        # Generator marginal cost
        self.data.generatorcost = {}
        for g in self.data.generators.index:
            self.data.generatorcost[g] = self.data.generators.lincost[g]
        
        # Returns a list where each gen is assigned to the given zone
        country_generator = self.data.generators[['country','name']].values.tolist()
        self.data.gens_for_country = defaultdict(list) 
        for country, generator in country_generator:
            self.data.gens_for_country[country].append(generator) 
        
        # Lines and lineinfo
        self.data.lines = [('Z1', 'Z2'), ('Z2', 'Z3')]

        self.data.lineinfo = {}

        self.data.lineinfo[('Z1', 'Z2')] = {'linecapacity': 875, 'x': 1, 'otherinfo': []} #875
        self.data.lineinfo[('Z2', 'Z3')] = {'linecapacity': 1500, 'x': 1, 'otherinfo': []} #1500
       
        # VOLL assigned to each time
        self.data.VoLL = {}
        for t in times:
            self.data.VoLL[t] = 3000 # Price cap is 3000 € in Nordpool Spot (SE and NO) 
        
        
    def _build_model(self):
        self.model = gb.Model()
        self._build_variables()
        self._build_objective()
        self._build_constraints()
        
    def _build_variables(self):
        m = self.model
        
        times = self.data.times
        lines = self.data.lines
        lineinfo = self.data.lineinfo
        generators = self.data.generators
        windproduction = self.data.windprod
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
                self.variables.windprod[z, t] = m.addVar(lb = 0, ub = sum(windproduction[n,t] for n in nodes_for_zones[z]))

        # Export variable from each node at each time, (-infinity < export < infinity)
        self.variables.export = {}
        for t in times:
            for z in zones:
                self.variables.export[z, t] = m.addVar(lb = -gb.GRB.INFINITY, ub = gb.GRB.INFINITY)

        # The linelimits between zones are inserted        
        self.variables.linelimit = {}
        for t in times:
            for l in lines: # New lines, check from beginning!
                self.variables.linelimit[l, t] = m.addVar(lb=-lineinfo[l]['linecapacity'], ub=lineinfo[l]['linecapacity'])
                                                         
        # Binary variables used to find start-up and on/off status
        self.variables.startup = {}
        for t in times:
            for g in generators.index:
                self.variables.startup[g, t] = m.addVar(vtype = gb.GRB.BINARY) 

        self.variables.online = {}
        for t in times:
            for g in generators.index:
                self.variables.online[g, t] = m.addVar(vtype = gb.GRB.BINARY)                                               
        
        
        m.update()        
        
    def _build_objective(self):

        times = self.data.times
        zones = self.data.zones
        generators = self.data.generators
        loadshed = self.variables.loadshed
        gprod = self.variables.gprod
        generatorcost = self.data.generatorcost
        VoLL = self.data.VoLL
        startup = self.variables.startup
        
        self.model.setObjective(
            
            gb.quicksum(generatorcost[g] * gprod[g, t] for g in generators.index for t in times)
            
            + gb.quicksum(startup[g, t] * generators.cyclecost[g] for g in generators.index for t in times)
            
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
        generators = self.data.generators
        online = self.variables.online
        gprod = self.variables.gprod
        startup = self.variables.startup
        hydrocoeff = self.data.hydrocoeff

        # Power Balance constraint in each zone at each time
        self.constraints.powerbalance = {}
        for z in zones:
            for t in times:
                self.constraints.powerbalance[z, t] = m.addConstr(
                    
                    gb.quicksum(gprod[g, t] for g in gens_for_country[z])
                    
                    + windprod[z, t]
                    
                    ,gb.GRB.EQUAL,
                    
                    (Load[z, t] - loadshed[z, t]) + export[z, t])
      
          
        # Export constraint at each node at each time
        self.constraints.exporting = {}
        for t in times:
            for z in zones:
                self.constraints.exporting[z, t] = m.addConstr(
                   
                   export[z, t], gb.GRB.EQUAL,

                   gb.quicksum(linelimit[l, t] for l in lines if l[0] == z) - gb.quicksum(linelimit[l, t] for l in lines if l[1] == z))

        
        # On/Off status for each generator at each time
        self.constraints.on_off_min = {}
        for t in times:
            for g in generators.index:
                self.constraints.on_off_min[g, t] = m.addConstr(
                
                    generators.minonlinecapacity[g] * online[g, t], 

                    gb.GRB.LESS_EQUAL, gprod[g, t])

        self.constraints.on_off_max = {}
        for t in times:
            for g in generators.index:
               self.constraints.on_off_max[g, t] = m.addConstr(
                
                    gprod[g, t], gb.GRB.LESS_EQUAL,
                
                    generators.capacity[g] * online[g, t])

        
        # Start-up costs for a generator starting up, the units are initially online (indifferent)
        self.constraints.start_up = {}
        for t in times:
            for s in times[1:]:
                for r in list(range(times[0],2)):
                    for g in generators.index:
                        self.constraints.start_up[g, t] = m.addConstr(
                
                            (online[g, r] - 1) + (online[g, s] - online[g, s-1])
                            
                            ,gb.GRB.LESS_EQUAL, startup[g, t])
               
        # Minimum time online
        # The initial on/off status of the generators is left out and is not included.
        self.constraints.min_up = {} 
        for g in generators.index:
            for t in times:              
                if t >= max((max(times)-generators.minuptime[g]+2),2): # Ending period
                    endingtimeset = []
                    for tau in times:
                        if tau >= t:
                            endingtimeset.append(tau)
                    if endingtimeset != []:
                        self.constraints.min_up[g, t] = m.addConstr(
                        
                        gb.quicksum((online[g, tau] - (online[g, t] - online[g, t-1])) for tau in endingtimeset), 

                        gb.GRB.GREATER_EQUAL, 0)
                
                if t > 0 and t <= max((max(times)-generators.minuptime[g]+1),2): # Subsequent period
                    generatortimeset = []
                    for tau in times:
                        if tau >= t and tau < t + generators.minuptime[g]:
                            generatortimeset.append(tau)
                    if generatortimeset != []:
                        self.constraints.min_up[g, t] = m.addConstr(
                        
                        gb.quicksum(online[g, tau] for tau in generatortimeset), gb.GRB.GREATER_EQUAL,

                        generators.minuptime[g] * (online[g, t] - online[g, t-1]))
            
            
        # Minimum time offline, same reasoning as with up-time
        self.constraints.min_down = {} 
        for g in generators.index:
            for t in times:
                if t >= max((max(times)-generators.mindowntime[g]+2),2): # Ending period
                    endingtimeset = []
                    for tau in times:
                        if tau >= t:
                            endingtimeset.append(tau)
                    if endingtimeset != []:
                        self.constraints.min_down[g, t] = m.addConstr(
                        
                        gb.quicksum((1 - online[g, tau] - (online[g, t-1] - online[g, t])) for tau in endingtimeset), 

                        gb.GRB.GREATER_EQUAL, 0)
                
                if t > 0 and t <= max((max(times)-generators.mindowntime[g]+1),2): # Subsequent period
                    generatortimeset = []
                    for tau in times:
                        if tau >= t and tau < t + generators.mindowntime[g]:
                            generatortimeset.append(tau)
                    if generatortimeset != []:
                        self.constraints.min_down[g, t] = m.addConstr(
                        
                        gb.quicksum((1 - online[g, tau]) for tau in generatortimeset), gb.GRB.GREATER_EQUAL,

                        generators.mindowntime[g] * (online[g, t-1] - online[g, t]))
                        
                        
        self.constraints.rampup = {}
        for t in times[1:]:
            for g in generators.index:
                self.constraints.rampup = m.addConstr(
                
                    gprod[g, t], gb.GRB.LESS_EQUAL,

                    gprod[g, t-1] + generators.rampingup[g] * generators.capacity[g]) 
                    
                    
        self.constraints.rampdown = {}
        for t in times[1:]:
            for g in generators.index:
                self.constraints.rampdown = m.addConstr(
                
                    gprod[g, t-1] - generators.rampingdown[g] * generators.capacity[g], 

                    gb.GRB.LESS_EQUAL, gprod[g, t])
                    
                    
        self.constraints.hydro = {}
        for g in generators.index:
            if generators.primaryfuel[g] == "Hydro":
                self.constraints.hydro[g] = m.addConstr(
                
                    gb.quicksum(gprod[g, t] for t in times), gb.GRB.LESS_EQUAL,

                    hydrocoeff * generators.capacity[g] * len(times))

''' 
This is the code to implement the beginning period. However, it is not needed

                if t <= (online[g, 0] * generators.iniminuptime[g]): # Beginning period
                    begintimeset = []
                    for tau in times:
                        if tau <= t:
                            begintimeset.append[tau]
                    if begintimeset != []:
                        self.constraints.min_up[g, t] = m.addConstr(
                    
                            gb.quicksum(online[g, tau] for tau in begintimeset),

                            gb.GRB.EQUAL, generators.iniminuptime[g])



                if t <= online[g, 0] * generators.iniminuptime[g]:
                    self.constraints.min_up[g, t] = m.addConstr(
                    
                        online[g, t], gb.GRB.EQUAL, generators.minuptime[g])
                
                if t >= max((len(times)-generators.minuptime[g]+2),2):
                    self.constraints.min_up[g, t] = m.addConstr(
                        
                        online[g, t] - startup[g, t], gb.GRB.GREATER_EQUAL, 0)
 
        # Minimum time offline
        self.constraints.min_down = {}
        for t in times[1:]:
            for g in generators.index:
                self.constraints.min_down[g, t] = m.addConstr(
                    
                    online[g, t-1] - online[g, t],

                    gb.GRB.LESS_EQUAL, 1 - online[g, t+generators.mindowntime[g]-1])
     
        # Minimum time offline
        self.constraints.min_down = {}
        for t in times[1:]:
            for g in generators.index:
                for x in mindown:
                    self.constraints.min_down[g, t] = m.addConstr(
                    
                        online[g, t] - online[g, t-1], 

                        gb.GRB.LESS_EQUAL, online[g, x])
        
        
        # Minimum time online
        self.constraints.min_up = {}
        for t in times[1:]:
            for g in generators.index:
                for x in minup:
                    self.constraints.min_up[g, t] = m.addConstr(
                    
                        online[g, t-1] - online[g, t],

                        gb.GRB.LESS_EQUAL, 1 - online[g, x])

       
'''

