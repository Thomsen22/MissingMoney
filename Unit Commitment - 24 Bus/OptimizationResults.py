# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:54:04 2016

@author: Søren
"""

# Python standard modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gurobipy as gb
import networkx as nx
from collections import defaultdict
import math
import seaborn as sns
# Own modules
import Data_24Bus as data
from DA_optclass import DayAhead

#%% Function to run optimization and return dataframes to main

def optimization():
    market = DayAhead()
    market.optimize()
    
    times = market.data.times
    zones = market.data.zones
    generators = market.data.generators
    lines = market.data.lines
    windproduction = market.data.windproduction[0:(len(times))]
    consumption = market.data.consumption
    network = market.data.network
 
    # Zonal prices. The prices are calculated in a long string, seperated into zone with the following code: 
    Price = market.data.MarketPrice
    MarketPrice = pd.DataFrame([[key,value] for key,value in Price.items()],columns=["Times","MarketPrice"]).set_index('Times')

    ZonalPrices = pd.DataFrame(np.arange(len(times)),columns=['Times'])
    nzones = list(range(len(zones)))
    for nz in nzones:
        ZonalPrices['{z}'.format(z=nz)] = pd.DataFrame(MarketPrice.iloc[(len(times))*nz:((len(times))*(nz+1))]).set_index(np.arange(len(times)))
        ZonalPrices = ZonalPrices.rename(columns={'{z}'.format(z=nz): 'Z{z}'.format(z=nz+1)})
    
    ZonalPrices = ZonalPrices.set_index('Times')

    # Generator production, 
    GeneratorProduction = pd.DataFrame(index = times, data = {g: [market.variables.gprod[g,t].x for t in times] for g in generators.index})

    # Line flow, from node -> to node
    LineFlow = pd.DataFrame(index = times, data = {l: [market.variables.linelimit[l,t].x for t in times] for l in lines})

    # Loadshedding in the system
    LoadShed = pd.DataFrame(index = times, data = {z: [market.variables.loadshed[z,t].x for t in times] for z in zones})

    # Wind penetration (including wind curtailment)
    WindProd = pd.DataFrame(index = times, data = {z: [market.variables.windprod[z,t].x for t in times] for z in zones})

    WindProd = WindProd.sum(axis=1)

    # Total consumption. Resetting the index, summing consumption for all nodes
    Consumption = consumption.set_index(np.arange(0,len(consumption)))
    Consumption = (Consumption.sum(axis=1)) - (LoadShed.sum(axis=1))
    
    # Calculating the wind penetration level
    WindPenetration = (WindProd / Consumption) * 100
    
    WindLoad_df = pd.DataFrame({'Time':WindPenetration.index, 'WindProduction[MW]':WindProd.values, 'TotalConsumption[MW]': Consumption.values, 'WindPenetration[%]':WindPenetration.values}).set_index('Time')
 
    # Assigning each zone to a generator
    zone_generator = generators[['name','country']].values.tolist()
    zone_for_gens = defaultdict(list)
    for generator, zone in zone_generator:
        zone_for_gens[generator].append(zone)
  
    # Creating a dictionary to contain the market prices
    MarketPriceDict = {}
    for t in times:
        for z in np.arange(len(zones)):
            MarketPriceDict[ZonalPrices.columns[z], t] = ZonalPrices.loc[ZonalPrices.index[t], ZonalPrices.columns[z]]
    
    # Creating a dictionary to contain the generator production
    GeneratorProductionDict = {}
    for t in times:
        for g in np.arange(len(generators.index)):
            GeneratorProductionDict[GeneratorProduction.columns[g], t] = GeneratorProduction.loc[GeneratorProduction.index[t], GeneratorProduction.columns[g]]

    # Calculating the revenue for each generator
    Revenue = {}
    for t in times:
        for g in generators.index:
            for z in zone_for_gens[g]:
                Revenue[g, t] = MarketPriceDict[z, t] * GeneratorProductionDict[g, t]
    
    # Summing the revenues for all hours 
    Revenue_total = {}
    for g in generators.index:
        Revenue_total[g] = sum(Revenue[g, t] for t in times) #/ GeneratorProduction[g].sum(axis=0)

    Revenue_df = pd.DataFrame([[key,value] for key,value in Revenue_total.items()],columns=["Generator","Total Revenue"]).set_index('Generator')
    
    # Cost calculation, simple (marg. price * production)
    Cost = {}
    for t in times:
        for g in generators.index:
            Cost[g,t] = generators.lincost[g] * GeneratorProductionDict[g,t]

    # Summing the costs for all hours
    Cost_total = {}
    for g in generators.index:
        Cost_total[g] = sum(Cost[g,t] for t in times)

    # Catching the start-up costs not covered in the market optimization
    startup_cost = {}
    for t in times[1:]:
        for g in generators.index:
            startup_cost[g, t] = 0 # Making a zero-filled dictionary 
            if(GeneratorProductionDict[g, t] > 0 and GeneratorProductionDict[g, t-1] == 0):
                startup_cost[g, t] = generators.cyclecost[g]
                
    # Calculating total start-up costs for all generators
    startup_cost_total = {}
    for g in generators.index:
        startup_cost_total[g] = sum(startup_cost[g,t] for t in times[1:])
    
        # Catching the start-up costs not covered in the market optimization
    startup_number = {}
    for t in times[1:]:
        for g in generators.index:
            startup_number[g, t] = 0 # Making a zero-filled dictionary 
            if(GeneratorProductionDict[g, t] > 0 and GeneratorProductionDict[g, t-1] == 0):
                startup_number[g, t] = 1
                
    # Calculating total start-up costs for all generators
    startup_number_total = {}
    for g in generators.index:
        startup_number_total[g] = sum(startup_number[g,t] for t in times[1:])
    
    startup_number_df = pd.DataFrame([[key,value] for key,value in startup_number_total.items()],columns=["Generator","Total Start-Ups"]).set_index('Generator')
    
    
    # Calculating fixed O&M for all generators    
    fixed_om_total = {}
    for g in generators.index:
        fixed_om_total[g] = (generators.fixedomcost[g] * generators.capacity[g]) / 365 * (len(times)/24)
    
    # Calculating fixed levelized cost for all gnerators
    fixed_lc_total = {}
    for g in generators.index:
        fixed_lc_total[g] = (generators.levcapcost[g] * 1000000 * generators.capacity[g]) / 365 * (len(times)/24)
    
    # Calculating total cost for each generator    
    total_costs = {}
    for g in generators.index:
        total_costs[g] = Cost_total[g] + fixed_om_total[g] + fixed_lc_total[g] + startup_cost_total[g]
        
    
    Cost_df = pd.DataFrame([[key,value] for key,value in total_costs.items()],columns=["Generator","Total Costs"]).set_index('Generator')

    # Merging the cost and revenue df´s together, calculate "profit" = difference
    Rev_Cost_df = pd.merge(Cost_df, Revenue_df, right_index = True, left_index = True)
    Rev_Cost_df['Total Production'] = GeneratorProduction.sum(axis=0)

    return ZonalPrices, GeneratorProduction, LineFlow, LoadShed, WindLoad_df, Rev_Cost_df, network, times, generators, startup_number_df