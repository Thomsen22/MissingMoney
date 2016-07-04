# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 16:46:18 2016

@author: Søren
"""

# Python standard modules
import numpy as np
import gurobipy as gb
import networkx as nx
from collections import defaultdict
import pandas as pd
# Own modules
import LoadDataEU as data
import PLR_opt as plrmodel

class expando(object):
    '''
        # A class for capacity market clearing
    '''
    pass

class PLRMarket:
    def __init__(self):       
        self.data = expando()
        self.variables = expando()
        self.constraints = expando()
        self._load_data()
        self._build_model()
            
    def optimize(self):       
        self.model.optimize()

    def _load_data(self):
        self.data.generators = pd.read_csv('generators.csv', sep=',', encoding='latin-1').set_index('ID')
        self.data.consumption = data.load()
        self.data.network = data.load_network()
        self.data.nodes = self.data.network.nodes()
        self.data.df_lines = data.load_lines()
        self.data.approach = 'Approach1' # Energinet = Approach1
        self.data.model = 'Swedish' # 'Swedish'
        self.data.plrdemand = 0.25
        self.data.times = np.arange(len(self.data.consumption.index)) 
        self.data.country = self.data.generators['country'].unique().tolist()
        self.data.zones = self.data.country
        self.data.timeperiod = 'Year' #'Weak'
        self.data.BidType = 'Fixed'
        self.data.reservemargin = 1.15
        self.data.windreserve = 0.06
        self.data.lines = list(self.data.df_lines.index)
        self.data.flow, self.data.df_price_DA, self.data.df_windprod, self.data.df_solarprod = plrmodel.DayAheadMarket() # Runs DA market clearing
        self.data.cost = plrmodel.PLR(self.data.timeperiod, self.data.approach) # Finds the PLR bids
   
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
            
        # Connection between zones (tells which zones are connected to each other, like defaultdict)
        self.data.zonecons = {}
        for z in self.data.zones:
            for l in self.data.lines:
                if l[0] == z:
                    self.data.zonecons.setdefault(z,[]).append(l[1])
                elif l[1] == z:
                    self.data.zonecons.setdefault(z,[]).append(l[0])

        # Assigning load to each node and time (and zonal consumption)
        times = self.data.times
        nodes = self.data.nodes
        consumption = self.data.consumption
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

        self.data.peakload = {}
        for z in zones:
            self.data.peakload[z] = self.data.df_zonalconsumption[z].max()
        
        # Assigning generators to specific zone
        country_generator = self.data.generators[['country','name']].values.tolist()
        self.data.gens_for_country = defaultdict(list) 
        for country, generator in country_generator:
            self.data.gens_for_country[country].append(generator)

        # Demand for PLR using the Swedish data
        self.data.zonaldemand = {}
        for z in zones:
            if self.data.model == 'Swedish':
                self.data.zonaldemand[z] = (self.data.peakload[z] * self.data.plrdemand)
        

    def _build_model(self):
        self.model = gb.Model()
        self._build_variables()
        self._build_objective()
        self._build_constraints()
        
    def _build_variables(self):
        m = self.model
        
        generators = self.data.generators
        zones = self.data.zones
        lines = self.data.lines
        lineinfo = self.data.df_lines

        # Capacity variable (mothballed generators also participates)
        self.variables.gcap = {}
        for g in generators.index:
            self.variables.gcap[g] = m.addVar(lb = 0, ub = generators['capacity'][g])
    
        # PLR demand
        self.variables.demand = {}
        for z in zones:
            self.variables.demand[z] = m.addVar(lb = self.data.zonaldemand[z], ub = gb.GRB.INFINITY)

        # Dispatched status of generators
        self.variables.dispatch = {}
        for g in generators.index:
            self.variables.dispatch[g] = m.addVar(vtype = gb.GRB.BINARY)  

        # The linelimits between zones are inserted        
        self.variables.linelimit = {}
        for l in lines: 
            self.variables.linelimit[l] = m.addVar(lb=-lineinfo['capacity'][l]*0.5, ub=lineinfo['capacity'][l]*0.5)
            
        # Export variable from each zone
        self.variables.export = {}
        for z in zones:
            self.variables.export[z] = m.addVar(lb = -gb.GRB.INFINITY, ub = gb.GRB.INFINITY)
                                                    
        m.update()  

           
    def _build_objective(self):

        dispatch = self.variables.dispatch
        df_cost = self.data.cost
        
        self.model.setObjective(

            gb.quicksum(df_cost['PLRbid'][g] * dispatch[g] for g in df_cost.index)            
            
            ,gb.GRB.MINIMIZE)

    def _build_constraints(self):
        m = self.model
        
        zones = self.data.zones
        gens_for_zones = self.data.gens_for_country
        gcap = self.variables.gcap
        demand = self.variables.demand 
        generators = self.data.generators
        dispatch = self.variables.dispatch
        export = self.variables.export
        lines = self.data.lines
        linelimit = self.variables.linelimit
        
        # Power Balance constraint in each zone
        self.constraints.powerbalance = {}
        for z in zones:
            self.constraints.powerbalance[z] = m.addConstr(
                    
                gb.quicksum(gcap[g] for g in gens_for_zones[z])
                    
                ,gb.GRB.EQUAL,
                    
                demand[z] + export[z])
                    
        # Dispatched status for each generator
        self.constraints.dispatch = {}
        for g in generators.index:
            self.constraints.dispatch[g] = m.addConstr(
                
                generators.capacity[g] * dispatch[g], 

                gb.GRB.EQUAL, gcap[g])

        
        # Export constraint from each zone
        self.constraints.exporting = {}
        for z in zones:
            self.constraints.exporting[z] = m.addConstr(
            
                export[z], gb.GRB.EQUAL,

                gb.quicksum(linelimit[l] for l in lines if l[0] == z) - gb.quicksum(linelimit[l] for l in lines if l[1] == z))

  
        # Hydro constraint (cannot be a PLR)
        self.constraints.hydro = {}
        for g in generators.index:
            if generators['primaryfuel'][g] == 'Hydro':
                self.constraints.hydro[g] = m.addConstr(
                
                    generators.capacity[g] * dispatch[g], 

                    gb.GRB.EQUAL, 0)   
    
