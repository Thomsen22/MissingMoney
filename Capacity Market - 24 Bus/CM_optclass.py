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
import Data_24Bus as data
import CM_opt as cmmodel

class expando(object):
    '''
        # A class for capacity market clearing
    '''
    pass

class CapacityMarket:
    def __init__(self):       
        self.data = expando()
        self.variables = expando()
        self.constraints = expando()
        self._load_data()
        self._build_model()
            
    def optimize(self):       
        self.model.optimize()

    def _load_data(self):
        self.data.flow, self.data.df_price_DA, self.data.df_windprodload, self.data.df_zonalsolarproduction, self.data.df_windsolarpen = cmmodel.DayAheadMarket() # Runs DA market clearing
        self.data.cost = pd.read_csv('revenue_cost_gen.csv').set_index('Generator')
        self.data.generators = pd.read_csv('generators.csv').set_index('ID')
        self.data.windturbines = pd.read_csv('wind_turbines.csv').set_index('node')
        self.data.consumption = data.load()
        self.data.network = data.load_network()
        self.data.nodes = self.data.network.nodes()
        self.data.country = nx.get_node_attributes(self.data.network, 'country')
        self.data.times = np.arange(len(self.data.consumption.index)) # Only run 1 time (if needed)
        self.data.timeperiod = 'Weak'
        self.data.BidType = 'Fixed'
        self.data.reservemargin = 1.15
        self.data.windreserve = 0.06
        self.data.zones = ['Z1', 'Z2', 'Z3']
        self.data.lines = [('Z1', 'Z2'), ('Z2', 'Z3')]
        self.data.lineinfo = {}
        self.data.lineinfo[('Z1', 'Z2')] = {'linecapacity': 875, 'x': 1, 'otherinfo': []} #875
        self.data.lineinfo[('Z2', 'Z3')] = {'linecapacity': 1500, 'x': 1, 'otherinfo': []} #1500

        times = self.data.times
        nodes = self.data.nodes
        consumption = self.data.consumption
        windturbines = self.data.windturbines
        zones = self.data.zones        
             
        if self.data.timeperiod == 'Weak':
            self.data.period = 52
        elif self.data.timeperiod == 'Year':
            self.data.period = 1
        
        df_cost = self.data.cost
        generators = self.data.generators.index
        
        # Missing money from variable costs
        self.data.varcost = {}
        for g in generators:
            self.data.varcost[g] = (df_cost['TotalProduction'][g]*df_cost['MarginalCost'][g]+df_cost['TotalProduction'][g]*df_cost['VarO&MCost'][g]+df_cost['S/Ucost'][g]*df_cost['NumberofS/U'][g])

        self.data.mmvarcost = {}
        for g in generators:
            if df_cost['TotalRevenue'][g] - self.data.varcost[g] >= 0:
                self.data.mmvarcost[g] = 0
            elif df_cost['TotalRevenue'][g] - self.data.varcost[g] < 0:
                self.data.mmvarcost[g] = df_cost['TotalRevenue'][g] - self.data.varcost[g]
            
        self.data.variablebid = {}
        for g in generators:
            self.data.variablebid[g] = -(self.data.mmvarcost[g] / df_cost['Capacity'][g])
    
        df_variable = pd.DataFrame([[key,value] for key,value in self.data.variablebid.items()],columns=["Generator","MMVarCost"]).set_index('Generator')
        df_cost = pd.merge(df_cost, df_variable, right_index = True, left_index = True)

        # Missing money including fixed costs
        self.data.fixedcost = {}
        for g in generators:
            self.data.fixedcost[g] = (df_cost['FixedO&MCost'][g]*df_cost['Capacity'][g])/self.data.period

        self.data.mmfixedcost = {}
        for g in generators:
            if df_cost['TotalRevenue'][g] - (self.data.varcost[g] + self.data.fixedcost[g]) >= 0:
                self.data.mmfixedcost[g] = 0
            elif df_cost['TotalRevenue'][g] - (self.data.varcost[g] + self.data.fixedcost[g]) < 0:
                self.data.mmfixedcost[g] = df_cost['TotalRevenue'][g] - (self.data.varcost[g] + self.data.fixedcost[g])

        self.data.fixedbid = {}
        for g in generators:
            self.data.fixedbid[g] = -(self.data.mmfixedcost[g] / df_cost['Capacity'][g])
    
        df_fixed = pd.DataFrame([[key,value] for key,value in self.data.fixedbid.items()],columns=["Generator","MMFixedCost"]).set_index('Generator')
        df_cost = pd.merge(df_cost, df_fixed, right_index = True, left_index = True)

        # Missing money including capital costs
        self.data.capcost = {}
        for g in generators:
            self.data.capcost[g] = (df_cost['LevelizedCapitalCost'][g]*1000000*df_cost['Capacity'][g])/self.data.period

        self.data.mmcapcost = {}
        for g in generators:
            if df_cost['TotalRevenue'][g] - (self.data.varcost[g] + self.data.fixedcost[g] + self.data.capcost[g]) >= 0:
                self.data.mmcapcost[g] = 0
            elif df_cost['TotalRevenue'][g] - (self.data.varcost[g] + self.data.fixedcost[g] + self.data.capcost[g]) < 0:
                self.data.mmcapcost[g] = df_cost['TotalRevenue'][g] - (self.data.varcost[g] + self.data.fixedcost[g] + self.data.capcost[g])
    
        self.data.capitalbid = {}
        for g in generators:
            self.data.capitalbid[g] = -(self.data.mmcapcost[g] / df_cost['Capacity'][g])
        
        df_capital = pd.DataFrame([[key,value] for key,value in self.data.capitalbid.items()],columns=["Generator","MMCapCost"]).set_index('Generator')
        df_cost = pd.merge(df_cost, df_capital, right_index = True, left_index = True)

        # Capacity market bid depending on BidType
        if self.data.BidType == 'Variable':
            bidcap = {}
            for g in generators:
                bidcap[g] = -(self.data.mmvarcost[g] / df_cost['Capacity'][g])
        
        if self.data.BidType == 'Fixed':
            bidcap = {}
            for g in generators:
                bidcap[g] = -(self.data.mmfixedcost[g] / df_cost['Capacity'][g])
        
        if self.data.BidType == 'Capital':
            bidcap = {}
            for g in generators:
                bidcap[g] = -(self.data.mmcapcost[g] / df_cost['Capacity'][g])

        df_capacitybids = pd.DataFrame([[key,value] for key,value in bidcap.items()],columns=["Generator","BidMM"]).set_index('Generator')
    
        df_cost = pd.merge(df_cost, df_capacitybids, right_index = True, left_index = True)
        df_cost['BidMM'].fillna(0, inplace=True)
        
        self.data.df_cost = df_cost

        # Assigning each node to a country (price-area, zone)
        country = nx.get_node_attributes(self.data.network, 'country')
        country = pd.Series(self.data.country, name='Zone')
        country = country.reset_index()
        country = country.rename(columns={'index': 'Node'})
        # Using defaultdict
        zones_nodes = country[['Zone','Node']].values.tolist()
        self.data.nodes_for_zones = defaultdict(list)
        for Node,Zone in zones_nodes:
            self.data.nodes_for_zones[Node].append(Zone)
        
        # Assigning load to each zone and finding peakload
        self.data.nodalconsumption = {}
        for t in times:
            for n in np.arange(len(nodes)):
                self.data.nodalconsumption[consumption.columns[n], t] = consumption.loc[consumption.index[t], consumption.columns[n]]
        
        self.data.zonalconsumption = {}
        for t in times:
            for z in zones: 
                self.data.zonalconsumption[z,t] = sum(self.data.nodalconsumption[n,t] for n in self.data.nodes_for_zones[z]) 
                
        self.data.df_zonalconsumption = pd.DataFrame(index = times, data = {z: [self.data.zonalconsumption[z,t] for t in times] for z in zones})

        self.data.peakload = {}
        for z in zones:
            self.data.peakload[z] = self.data.df_zonalconsumption[z].max()
        
        # Windturbine capacity in each zone
        self.data.turbinecapacity = {}
        for z in zones:
            self.data.turbinecapacity[z] = sum(windturbines['turbines'][n] for n in self.data.nodes_for_zones[z])
        
        # Assigning generators to specific zone
        country_generator = self.data.generators[['country','name']].values.tolist()
        self.data.gens_for_country = defaultdict(list) 
        for country, generator in country_generator:
            self.data.gens_for_country[country].append(generator)
        
        # Assigning each zone to a generator
        zone_generator = self.data.generators[['name','country']].values.tolist()
        self.data.zone_for_gens = defaultdict(list)
        for generator, zone in zone_generator:
            self.data.zone_for_gens[generator].append(zone)
        
        # Demand for capacity in each zone        
        self.data.zonaldemand = {}
        for z in zones:
            self.data.zonaldemand[z] = self.data.peakload[z] * self.data.reservemargin
         
        # Wind capacity in each zone
        self.data.zonalwindreserve = {}
        for z in zones:
            self.data.zonalwindreserve[z] = self.data.turbinecapacity[z] * self.data.windreserve
        
        # Price-cap in the capacity market
        if sum(self.data.generators['capacity']) < sum(self.data.zonaldemand.values()) - sum(self.data.zonalwindreserve.values()):        
            if max(self.data.df_cost['BidMM']) + 1 > 40000/self.data.period:
                self.data.pricecap = max(self.data.df_cost['BidMM']) + 1
            elif max(self.data.df_cost['BidMM']) + 1 < 40000/self.data.period:
                self.data.pricecap = 40000/self.data.period + 1
        elif sum(self.data.generators['capacity']) > sum(self.data.zonaldemand.values()) - sum(self.data.zonalwindreserve.values()):
            self.data.pricecap = max(self.data.df_cost['BidMM']) + 1

    def _build_model(self):
        self.model = gb.Model()
        self._build_variables()
        self._build_objective()
        self._build_constraints()
        
    def _build_variables(self):
        m = self.model
        
        lines = self.data.lines
        lineinfo = self.data.lineinfo
        generators = self.data.generators
        zones = self.data.zones

        # Capacity variable
        self.variables.gcap = {}
        for g in generators.index:
            self.variables.gcap[g] = m.addVar(lb = 0, ub = generators['capacity'][g])

        # The linelimits between zones are inserted        
        self.variables.linelimit = {}
        for l in lines: 
            self.variables.linelimit[l] = m.addVar(lb=-lineinfo[l]['linecapacity']*0.5, ub=lineinfo[l]['linecapacity']*0.5)
            
        # Export variable from each zone
        self.variables.export = {}
        for z in zones:
            self.variables.export[z] = m.addVar(lb = -gb.GRB.INFINITY, ub = gb.GRB.INFINITY)
         
        # Capacity shed assigned to each zone in the system
        self.variables.capshed = {}
        for z in zones:
            self.variables.capshed[z] = m.addVar(lb = 0, ub = self.data.zonaldemand[z])
            
        # Wind capacity
        self.variables.windcap = {}
        for z in zones:
            self.variables.windcap[z] = m.addVar(lb = 0, ub = self.data.zonalwindreserve[z])
  
        m.update() 
           
    def _build_objective(self):

        df_cost = self.data.df_cost
        gcap = self.variables.gcap
        pricecap = self.data.pricecap
        capshed = self.variables.capshed
        zones = self.data.zones
        
        self.model.setObjective(

            gb.quicksum(df_cost['BidMM'][g] * gcap[g] for g in df_cost.index)
            
            + gb.quicksum(pricecap * capshed[z] for z in zones) 
            
            ,gb.GRB.MINIMIZE)

    def _build_constraints(self):
        m = self.model
        
        zones = self.data.zones
        lines = self.data.lines
        linelimit = self.variables.linelimit
        gens_for_zones = self.data.gens_for_country
        windreserve = self.variables.windcap
        gcap = self.variables.gcap
        export = self.variables.export
        demand = self.data.zonaldemand
        capshed = self.variables.capshed

        # Power Balance constraint in each zone at each time
        self.constraints.powerbalance = {}
        for z in zones:
            self.constraints.powerbalance[z] = m.addConstr(
                    
                    gb.quicksum(gcap[g] for g in gens_for_zones[z])
                    
                    + windreserve[z]
                    
                    ,gb.GRB.EQUAL,
                    
                    (demand[z] - capshed[z]) + export[z])

        # Export constraint from each zone
        self.constraints.exporting = {}
        for z in zones:
            self.constraints.exporting[z] = m.addConstr(
            
                export[z], gb.GRB.EQUAL,

                gb.quicksum(linelimit[l] for l in lines if l[0] == z) - gb.quicksum(linelimit[l] for l in lines if l[1] == z))


        
   
                  
    
    