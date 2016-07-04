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
from itertools import cycle, islice

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
    df_zonalconsumption = market.data.df_zonalconsumption
    
    #%% Pandas containing results from optimization
    
    # Zonal prices, found by taking the dual of the powerbalance constraint    
    
    ZonalPrices = pd.DataFrame(index = times, data = {z: [market.constraints.powerbalance[z,t].pi for t in times] for z in zones})

    # Generator production, 
    GeneratorProduction = pd.DataFrame(index = times, data = {g: [market.variables.gprod[g,t].x for t in times] for g in generators.index})

    # Line flow, from node -> to node
    LineFlow = pd.DataFrame(index = times, data = {l: [market.variables.linelimit[l,t].x for t in times] for l in lines})

    # Loadshedding in the system
    LoadShed = pd.DataFrame(index = times, data = {z: [market.variables.loadshed[z,t].x for t in times] for z in zones})

    # Wind penetration (including wind curtailment)
    WindProd = pd.DataFrame(index = times, data = {z: [market.variables.windprod[z,t].x for t in times] for z in zones})

    # Total possible wind production can be used to find needed wind-curtailment 
    # WindProduction = windproduction.set_index(np.arange(0,len(windproduction)))
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
    
    # Catching the start-up number not covered in the market optimization
    startup_number = {}
    for t in times[1:]:
        for g in generators.index:
            startup_number[g, t] = 0 # Making a zero-filled dictionary 
            if(GeneratorProductionDict[g, t] > 0 and GeneratorProductionDict[g, t-1] == 0):
                startup_number[g, t] = 1
                
    # Calculating total number of start-ups for all generators
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

    Rev_Cost_df = pd.merge(Cost_df, Revenue_df, right_index = True, left_index = True)
    Rev_Cost_df['Total Production'] = GeneratorProduction.sum(axis=0)

    # Production from respective technologies for the given period
    
    # list comprehension, assigning different types of generators
    hydro_gens = [g for g in generators.index if generators.primaryfuel[g] == 'Hydro']
    coal_gens = [g for g in generators.index if generators.primaryfuel[g] == 'Coal']
    gas_gens = [g for g in generators.index if generators.primaryfuel[g] == 'Gas']
    nuclear_gens = [g for g in generators.index if generators.primaryfuel[g] == 'Nuclear']
    oil_gens = [g for g in generators.index if generators.primaryfuel[g] == 'Oil']

    # Calculating total hourly production for all technologies
    hydroP = {}
    for g in hydro_gens:
        hydroP[g] = GeneratorProduction[g]
        
    totalhydroP = {}    
    for t in times:
        totalhydroP[t] = sum(hydroP[g][t] for g in hydro_gens)
  
    coalP = {}
    for g in coal_gens:
        coalP[g] = GeneratorProduction[g]
        
    totalcoalP = {}    
    for t in times:
        totalcoalP[t] = sum(coalP[g][t] for g in coal_gens)
    
    gasP = {}
    for g in gas_gens:
        gasP[g] = GeneratorProduction[g]
    
    totalgasP = {}    
    for t in times:
        totalgasP[t] = sum(gasP[g][t] for g in gas_gens)
    
    nuclearP = {}
    for g in nuclear_gens:
        nuclearP[g] = GeneratorProduction[g]
    
    totalnuclearP = {}    
    for t in times:
        totalnuclearP[t] = sum(nuclearP[g][t] for g in nuclear_gens)

    oilP = {}
    for g in oil_gens:
        oilP[g] = GeneratorProduction[g]
    
    totaloilP = {}    
    for t in times:
        totaloilP[t] = sum(oilP[g][t] for g in oil_gens)

    # Returning respective production into dataframe and merges
    Oil_df = pd.DataFrame([[key,value] for key,value in totaloilP.items()],columns=["Times", "Oil Production"])#.set_index('Times')
    Nuclear_df = pd.DataFrame([[key,value] for key,value in totalnuclearP.items()],columns=["Times", "Nuclear Production"])#.set_index('Times')
    Gas_df = pd.DataFrame([[key,value] for key,value in totalgasP.items()],columns=["Times", "Gas Production"])#.set_index('Times')
    Coal_df = pd.DataFrame([[key,value] for key,value in totalcoalP.items()],columns=["Times", "Coal Production"])#.set_index('Times')
    Hydro_df = pd.DataFrame([[key,value] for key,value in totalhydroP.items()],columns=["Times", "Hydro Production"])#.set_index('Times')
    Wind_df = pd.DataFrame(WindLoad_df['WindProduction[MW]'])
    Wind_df.rename(columns={'WindProduction[MW]': 'Wind Production'}, inplace=True)
    Wind_df['Times'] = times

    Production_df = pd.DataFrame(Wind_df.merge(Hydro_df,on='Times').merge(Nuclear_df,on='Times').merge(Coal_df,on='Times').merge(Gas_df,on='Times').merge(Oil_df,on='Times').set_index('Times'))

    # Plots the production as an area diagram
    plt.figure(2)
    my_colors = list(islice(cycle([sns.xkcd_rgb["windows blue"], sns.xkcd_rgb["pale red"], sns.xkcd_rgb["medium green"], sns.xkcd_rgb["amber"], sns.xkcd_rgb["deep purple"],'grey']), None, len(Production_df)))
    ax = Production_df.plot(kind='area', color=my_colors)

    ax.set_ylabel('$MW$')
    ax.set_xlabel('$Hours$')
    ax.set_axis_bgcolor('whitesmoke')
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=3, fancybox=True, shadow=True)
          
    plt.savefig('productionareaplot.pdf')
    plt.show()

    return ZonalPrices, GeneratorProduction, LineFlow, LoadShed, WindLoad_df, Rev_Cost_df, Production_df, network, times, generators, startup_number_df, df_zonalconsumption
    
def marketoptimization():
    
    df_price, df_genprod, df_flow, df_loadshed, df_windprodload, df_revenuecost, df_prodtype, network, times, generators, df_startups, df_zonalconsumption = optimization()
    
    # Average wind penetration is displayed
    Wind_Penetration = df_windprodload['WindPenetration[%]'].mean(axis=0)

    # A dataframe is returned to Excel for further work
    Gen_dataframe = df_revenuecost
    del Gen_dataframe['Total Costs']
    Gen_dataframe['Total Revenue'] = Gen_dataframe['Total Revenue'].map('{:.2f}'.format)
    Gen_dataframe['Total Production'] = Gen_dataframe['Total Production'].map('{:.2f}'.format)
    Gen_dataframe['Number of S/U´s'] = df_startups['Total Start-Ups']
    Gen_dataframe['Capacity'] = generators.capacity
    Gen_dataframe['Marginal Cost'] = generators.lincost
    Gen_dataframe['S/U cost'] = generators.cyclecost
    Gen_dataframe['Fixed O&M Cost'] = generators.fixedomcost
    Gen_dataframe['Var O&M Cost'] = generators.varomcost
    Gen_dataframe['Levelized Capital Cost'] = generators.levcapcost
    Gen_dataframe['Primary Fuel'] = generators.primaryfuel
    Gen_dataframe.to_csv('revenue_cost_gen.csv')
    
    return Gen_dataframe, Wind_Penetration