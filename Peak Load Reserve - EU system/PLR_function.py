# -*- coding: utf-8 -*-
"""
Created on Fri May 20 10:17:13 2016

@author: Søren
"""
# Python standard modules
import numpy as np
import pandas as pd
# Own modules
from PLR_optclass import PLRMarket
import PLR_opt as plrmodel

def PeakLoadReserveFunction():
    
    market = PLRMarket()
    market.optimize()

    df_generators = market.data.generators
    df_cost = market.data.cost    
    zones = market.data.zones
    times = market.data.times
    df_gencapacity = pd.DataFrame({'capacity': {g: market.variables.gcap[g].x for g in df_generators.index}})
    df_zonaldemand = pd.DataFrame({'demand': {z: market.variables.demand[z].x for z in zones}})
    df_zonalconsumption = pd.DataFrame(index = times, data = {z: [market.data.zonalconsumption[z,t] for t in times] for z in zones})
    reservemargin = market.data.reservemargin
    timeperiod = market.data.timeperiod
    model = market.data.model
    bidtype = market.data.BidType

    # Model types are controlled from the PLR_optclass 
    # SEmodel = df_generators['lincostold'].max() + 1 # max + 1
    # SEmodel = 3000 # Price cap
    SEmodel = 280
    for g in df_generators.index:
        if model == 'Swedish':
            if df_gencapacity['capacity'][g] > 0:
                df_generators['lincost'][g] = SEmodel + (df_generators['lincostold'][g]*0.05)
            elif df_gencapacity['capacity'][g] <= 0:
                df_generators['lincost'][g] = df_generators['lincostold'][g]

    df_generators.to_csv('generators.csv')
    
    # Run the DA optimization ones again and determine the missing money still in the system  
    df_flow, df_price_DA, df_windprod, df_solarprod = plrmodel.DayAheadMarket()
    
    # A dataframe is returned to Excel for further work
    Gen_dataframe = pd.read_csv('revenue_cost_gen.csv', sep=',', encoding='latin-1').set_index('Generator')
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
    
    Gen_dataframe = plrmodel.missingmoneyPLR(timeperiod, bidtype)
    
    return Gen_dataframe, df_zonalconsumption, reservemargin, df_price_DA, df_windprod, df_solarprod
    
def peakloadreserveoptimization():

    Gen_dataframe, df_zonalconsumption, reservemargin, df_price_DA, df_windprod, df_solarprod = PeakLoadReserveFunction()

    return Gen_dataframe, df_price_DA, df_windprod, df_solarprod
