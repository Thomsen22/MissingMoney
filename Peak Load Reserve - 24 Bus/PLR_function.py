# -*- coding: utf-8 -*-
"""
Created on Mon May  2 22:25:40 2016

@author: Søren
"""

# Python standard modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import gurobipy as gb
import networkx as nx
from collections import defaultdict
import math
import xlrd
from collections import OrderedDict
# Own modules
import Data_24Bus as data
from PLR_optclass import PLRclass
import OptimizationResults as results
import PLR_opt as plrmodel

def PLRmarket():
    # Optimize to find cheapest PLR plant configuration
    market = PLRclass()
    market.optimize()

    # Data output from PLR market
    df_generators = pd.read_csv('generators.csv').set_index('ID')
    df_cost = market.data.cost
    zones = market.data.zones
    times = market.data.times
    df_gencapacity = pd.DataFrame({'capacity': {g: market.variables.gcap[g].x for g in df_generators.index}})
    df_zonaldemand = pd.DataFrame({'demand': {z: market.variables.demand[z].x for z in zones}})
    df_zonalconsumption = pd.DataFrame(index = times, data = {z: [market.data.zonalconsumption[z,t] for t in times] for z in zones})
    gens_for_zones = market.data.gens_for_country
    reservemargin = market.data.reservemargin
    timeperiod = market.data.timeperiod
    model = market.data.model
    linelimit = market.data.linelimit
    
    # Model types are controlled from the PLR_optclass 
    # SEmodel = df_generators['lincostold'].max() + 1 
    SEmodel = 1000 # Price cap
    # SEmodel = 250
    for g in df_generators.index:
        if model == 'Swedish':
            if df_gencapacity['capacity'][g] > 0:
                df_generators['lincost'][g] = SEmodel + (df_generators['lincostold'][g]*0.05)
            elif df_gencapacity['capacity'][g] <= 0:
                df_generators['lincost'][g] = df_generators['lincostold'][g]

    df_generators.to_csv('generators.csv')

    # Run the DA optimization ones again and determine the missing money still in the system   
    df_price, df_genprod, df_flow, df_loadshed, df_windprodload, df_revenuecost, network, times, generators, df_startups, windcurtailment, TotalCost_df, windpenlevel, totalwindcost = results.optimization()

    # A dataframe is returned to Excel for further work
    Gen_dataframe = df_revenuecost
    del Gen_dataframe['TotalCosts']
    Gen_dataframe['TotalRevenue'] = Gen_dataframe['TotalRevenue'].map('{:.2f}'.format)
    Gen_dataframe['TotalProduction'] = Gen_dataframe['TotalProduction'].map('{:.2f}'.format)
    Gen_dataframe['NumberofS/U'] = df_startups['Total Start-Ups']
    Gen_dataframe['Capacity'] = generators.capacity
    Gen_dataframe['MarginalCost'] = generators.lincost
    Gen_dataframe['S/Ucost'] = generators.cyclecost
    Gen_dataframe['FixedO&MCost'] = generators.fixedomcost
    Gen_dataframe['VarO&MCost'] = generators.varomcost
    Gen_dataframe['LevelizedCapitalCost'] = generators.levcapcost
    Gen_dataframe['PrimaryFuel'] = generators.primaryfuel
    Gen_dataframe['PLRplants'] = df_gencapacity['capacity']

    PLRbid = {}
    for g in df_generators.index:
        if df_gencapacity['capacity'][g] > 0:
            PLRbid[g] = df_cost['PLRbid'][g]
        elif df_gencapacity['capacity'][g] == 0:
            PLRbid[g] = 0

    PLRbid_df = pd.DataFrame([[key,value] for key,value in PLRbid.items()],columns=["Generator","PLRbid"]).set_index('Generator')
    Gen_dataframe['PLRbid'] = PLRbid_df['PLRbid'].map('{:.2f}'.format)

    Gen_dataframe.to_csv('revenue_cost_gen_PLR.csv')
    
    Gen_dataframe = plrmodel.missingmoneyPLR(timeperiod)
    
    return df_gencapacity, df_zonaldemand, df_price, zones, df_generators, df_zonalconsumption, Gen_dataframe, gens_for_zones, reservemargin, timeperiod, linelimit, df_cost, windpenlevel, totalwindcost

def plroptimization():
    # Function for PLR "optimization"
    df_gencapacity, df_zonaldemand, df_price, zones, df_generators, df_zonalconsumption, Gen_dataframe, gens_for_zones, reservemargin, timeperiod, linelimit, df_cost, windpenlevel, totalwindcost = PLRmarket()

    # Finds the systemreserve margin in MW
    df_zonalconsumption['AllZones'] = df_zonalconsumption.sum(axis=1)
    systemreserve = df_zonalconsumption['AllZones'].max() * reservemargin
    del df_zonalconsumption['AllZones']

    # Choose to activate or deactivate depending on systemreserve margin
    if df_generators['capacity'].sum(axis=0) > systemreserve:
        df_generators = plrmodel.plantdeactivation(zones, gens_for_zones, df_zonalconsumption, reservemargin, Gen_dataframe)
    elif df_generators['capacity'].sum(axis=0) < systemreserve:
        df_generators = plrmodel.plantactivation(zones, gens_for_zones, df_zonalconsumption, reservemargin)

    df_generators = plrmodel.plantinvestment(df_price, timeperiod, zones, systemreserve)
    
    return Gen_dataframe, df_generators, windpenlevel, totalwindcost

