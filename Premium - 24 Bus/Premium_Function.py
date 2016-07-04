# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 08:57:01 2016

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
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, HPacker, VPacker
import OptimizationResults as results


def premiumfunction(timeperiod, bidtype, newpremium, reservemargin):

    df_price0, zones, gens_for_zones, df_zonalconsumption, df_zonalwindproduction, df_zonalsolarproduction, df_windprodload = DayAheadOptimization()    
    df_cost = missingmoney(timeperiod, bidtype)
    
    # Find highest amount of missing money and determine premium
    if newpremium == 'yes':
        df_cost, typegenerator, premiumfind = premiumdetermination(df_cost)
    elif newpremium == 'no':
        df_cost = df_cost
        chosengenerator = df_cost['Premium'].argmax() 
        typegenerator = df_cost['PrimaryFuel'][df_cost['Premium'].argmax()]
        premiumfind = df_cost['Premium'][chosengenerator]

    # Run DA optimization once again   
    df_price1, zones, gens_for_zones, df_zonalconsumption, df_zonalwindproduction, df_zonalsolarproduction, df_windprodload = DayAheadOptimization()
    df_cost = missingmoney(timeperiod, bidtype)
    df_cost.to_csv('revenue_cost_gen.csv')
    
    capacityreq = {}
    for z in zones:
        capacityreq[z] = df_zonalconsumption[z].max() * reservemargin
    
    df_capacityreq = pd.DataFrame([[key,value] for key,value in capacityreq.items()],columns=["Zones","CapacityReq"]).set_index('Zones')
     
    df_generators = pd.read_csv('generators.csv').set_index('ID')
    
    # Check the reserve margin
    for z in zones:
        if sum(df_generators['capacity'][g] for g in gens_for_zones[z]) > df_capacityreq['CapacityReq'][z]:
            df_generators = plantdeactivation(zones, gens_for_zones, df_cost, df_capacityreq)
        elif sum(df_generators['capacity'][g] for g in gens_for_zones[z]) < df_capacityreq['CapacityReq'][z]:
            df_generators = plantactivation(zones, gens_for_zones, df_capacityreq)

    # Investment in new plants (Exogenous)
    df_generators, df_cost = plantinvestment(df_price1, zones, gens_for_zones, timeperiod, df_capacityreq, typegenerator, premiumfind)
    df_cost.to_csv('revenue_cost_gen.csv')  
    
    windcost = {}
    for z in df_price1.columns:
        for t in df_price1.index:
            windcost[z,t] = df_zonalwindproduction[z][t] * df_price1[z][t]

    totalwindcost = sum(windcost.values())
    
    solarcost = {}
    for z in df_price1.columns:
        for t in df_price1.index:
            windcost[z,t] = df_zonalsolarproduction[z][t] * df_price1[z][t]

    totalsolarcost = sum(solarcost.values())
    
    windpenlevel = df_windprodload['WindPenetration[%]'].mean()
    solarpenlevel = df_windprodload['SolarPenetration[%]'].mean() 
    
    windproduction = df_windprodload['WindProduction[MW]'].sum()
    
    return df_cost, df_price0, df_price1, df_zonalconsumption, df_generators, totalwindcost, totalsolarcost, windpenlevel, solarpenlevel, windproduction
    
    
def premiumdetermination(df_cost):
    df_generators = pd.read_csv('generators.csv').set_index('ID')
    
    df_cost_temp = df_cost

    for g in df_cost_temp.index:
        if df_cost_temp['Premium'][g] > 0:
            df_cost_temp['MissingMoney'][g] = 0
        elif df_cost_temp['Premium'][g] == 0:
            df_cost_temp['MissingMoney'][g] = df_cost_temp['MissingMoney'][g]   
    
    for g in df_cost_temp.index:
        if df_cost_temp['TotalProduction'][g] > 0:
            df_cost_temp['MissingMoney'][g] = df_cost_temp['MissingMoney'][g]
        elif df_cost_temp['TotalProduction'][g] == 0:
            df_cost_temp['MissingMoney'][g] = 0

    chosengenerator = 'g16'
    typegenerator = 'GasCCGT'
    premiumfind = df_cost_temp['MissingMoney'][chosengenerator] / df_cost_temp['TotalProduction'][chosengenerator]
        
    premium = {}
    for g in df_cost.index:
        if df_cost['Premium'][g] > 0:
            premium[g] = df_cost['Premium'][g]
        elif df_cost['Premium'][g] == 0:
            if df_cost['PrimaryFuel'][g] == typegenerator:
                premium[g] = premiumfind
            elif df_cost['PrimaryFuel'][g] != typegenerator:
                premium[g] = 0
    
    premium_df = pd.DataFrame([[key,value] for key,value in premium.items()],columns=["Generator","Premium"]).set_index('Generator')
        
    df_cost['Premium'] = premium_df['Premium'] 
    
    df_generators['lincost'] = df_generators['lincostold'] - df_cost['Premium']
    
    for g in df_generators.index:
        if df_generators['lincost'][g] < 0:
            df_generators['lincost'][g] = -0.1
        elif df_generators['lincost'][g] >= 0:
            df_generators['lincost'][g] = df_generators['lincost'][g]
    
    df_cost.to_csv('revenue_cost_gen.csv')
    df_generators.to_csv('generators.csv')
    
    return df_cost, typegenerator, premiumfind

def DayAheadOptimization():
    # Runs the optimization
    df_price, df_genprod, df_flow, df_loadshed, df_windprodload, df_revenuecost, network, times, generators, df_startups, windcurtailment, TotalCost_df, df_zonalwindproduction, df_zonalsolarproduction, zones, gens_for_zones, consumption = results.optimization()

    # A dataframe is returned to Excel for further work
    revenue_cost_gen = pd.read_csv('revenue_cost_gen.csv').set_index('Generator')
    Gen_dataframe = df_revenuecost
    del Gen_dataframe['TotalCosts']
    revenue_cost_gen['TotalRevenue'] = Gen_dataframe['TotalRevenue'].map('{:.2f}'.format)
    revenue_cost_gen['TotalProduction'] = Gen_dataframe['TotalProduction'].map('{:.2f}'.format)
    revenue_cost_gen['NumberofS/U'] = df_startups['Total Start-Ups']
    revenue_cost_gen['Capacity'] = generators.capacity
    revenue_cost_gen['MarginalCost'] = generators.lincost
    revenue_cost_gen['S/Ucost'] = generators.cyclecost
    revenue_cost_gen['FixedO&MCost'] = generators.fixedomcost
    revenue_cost_gen['VarO&MCost'] = generators.varomcost
    revenue_cost_gen['LevelizedCapitalCost'] = generators.levcapcost
    revenue_cost_gen['PrimaryFuel'] = generators.primaryfuel
    revenue_cost_gen.to_csv('revenue_cost_gen.csv')

    return df_price, zones, gens_for_zones, consumption, df_zonalwindproduction, df_zonalsolarproduction, df_windprodload

def missingmoney(timeperiod, bidtype):
    df_cost = pd.read_csv('revenue_cost_gen.csv').set_index('Generator')
    df_generators = pd.read_csv('generators.csv').set_index('ID')
    generators = df_generators.index
    
    if timeperiod == 'Weak':
        period = 52
    elif timeperiod == 'Year':
        period = 1

    # The remaining missing money stemming from variable, fixed and capital cost is calculated seperately
    totalrevenue = {}
    for g in generators:
        totalrevenue[g] = df_cost['TotalRevenue'][g] + (df_cost['TotalProduction'][g] * df_cost['Premium'][g])
    
    # Missing money from variable cost
    varcost = {}
    for g in generators:
        varcost[g] =  (df_cost['TotalProduction'][g]*df_cost['MarginalCost'][g]+df_cost['TotalProduction'][g]*df_cost['VarO&MCost'][g]+df_cost['S/Ucost'][g]*df_cost['NumberofS/U'][g])

    mmvarcost = {}
    for g in generators:
        if totalrevenue[g] - varcost[g] >= 0:
            mmvarcost[g] = 0
        elif totalrevenue[g] - varcost[g] < 0:
            mmvarcost[g] = totalrevenue[g] - varcost[g]

    # Missing money including fixed costs
    fixedcost = {}
    for g in generators:
        fixedcost[g] = (df_cost['FixedO&MCost'][g]*df_cost['Capacity'][g])/period

    mmfixedcost = {}
    for g in generators:
        if totalrevenue[g] - (varcost[g] + fixedcost[g]) >= 0:
            mmfixedcost[g] = 0
        elif totalrevenue[g] - (varcost[g] + fixedcost[g]) < 0:
            mmfixedcost[g] = totalrevenue[g] - (varcost[g] + fixedcost[g])

    # Missing money including capital costs
    capcost = {}
    for g in generators:
        capcost[g] = (df_cost['LevelizedCapitalCost'][g]*1000000*df_cost['Capacity'][g])/period

    mmcapcost = {}
    for g in generators:
        if totalrevenue[g] - (varcost[g] + fixedcost[g] + capcost[g]) >= 0:
            mmcapcost[g] = 0
        elif totalrevenue[g] - (varcost[g] + fixedcost[g] + capcost[g]) < 0:
            mmcapcost[g] = totalrevenue[g] - (varcost[g] + fixedcost[g] + capcost[g])

    # Remaining amount of missing money
    if bidtype == 'Variable':
        missingmoney = {}
        for g in generators:
            missingmoney[g] = - mmvarcost[g]
    if bidtype == 'Fixed':
        missingmoney = {}
        for g in generators:
            missingmoney[g] = - mmfixedcost[g]
    if bidtype == 'Capital':
        missingmoney = {}
        for g in generators:
            missingmoney[g] = - mmcapcost[g]

    missingmoney_df = pd.DataFrame([[key,value] for key,value in missingmoney.items()],columns=["Generator","MissingMoney"]).set_index('Generator')
        
    df_cost['MissingMoney'] = missingmoney_df['MissingMoney']

    return df_cost


def plantdeactivation(zones, gens_for_zones, df_cost, df_capacityreq):
    df_generators = pd.read_csv('generators.csv').set_index('ID')
    
    # Finding the missing-money treshold in each zone (2 plants in each zone can be mothballed)
    missingmoney= {}
    treshold = {}
    for z in zones:
        for g in gens_for_zones[z]:
            if df_cost['MissingMoney'][g] > 0:
                missingmoney[g] = df_cost['MissingMoney'][g]
                mmlist = list(missingmoney.values())
            elif df_cost['MissingMoney'][g] == 0:
                missingmoney[g] = 0
                mmlist = list(missingmoney.values())
        if max(mmlist) == 0:
            treshold[z] = max(mmlist)
        elif max(mmlist) != 0:
            treshold[z] = max(n for n in mmlist if n!=max(mmlist)) 
        missingmoney.clear()

    # Mothballing the two generators with highest missing money
    for z in zones:
        for g in gens_for_zones[z]:
            if df_cost['MissingMoney'][g] >= treshold[z] and df_cost['MissingMoney'][g] > 0:
                df_generators['capacity'][g] = 0
            if df_generators['capacity'].sum(axis=0) - df_generators['capacity'][g] < sum(df_capacityreq['CapacityReq']):
                df_generators['capacity'][g] = df_generators['capacityold'][g] 

  
    df_generators.to_csv('generators.csv') 
    
    return df_generators


def plantactivation(zones, gens_for_zones, df_capacityreq):
    df_generators = pd.read_csv('generators.csv').set_index('ID')

    zonalcapacity = {}
    capacityfind = {}
    for z in zones:
        for g in gens_for_zones[z]:
            if df_generators['capacity'][g] == 0:
                zonalcapacity[g] = df_generators['capacityold'][g]
                zonalcap = list(zonalcapacity.values())
            elif df_generators['capacity'][g] != 0:
                zonalcapacity[g] = 0
                zonalcap = list(zonalcapacity.values())
        capacityfind[z] = min(zonalcap, key=lambda x:abs(x-df_capacityreq['CapacityReq'][z]))
        zonalcapacity.clear()

    summation = df_generators['capacity'].sum(axis=0) 

    # Only one generator can be activated in each zone
    for z in zones:
        for g in gens_for_zones[z]:
            if df_generators['capacity'][g] == 0 and df_generators['capacityold'][g] == capacityfind[z]:
                df_generators['capacity'][g] = df_generators['capacityold'][g]
            if df_generators['capacity'].sum(axis=0) - df_generators['capacity'][g] > summation:
                df_generators['capacity'][g] = 0 

    df_generators.to_csv('generators.csv')  
       
    return df_generators

    
def plantinvestment(df_price_DA, zones, gens_for_zones, timeperiod, df_capacityreq, typegenerator, premiumfind):
    df_generators = pd.read_csv('generators.csv').set_index('ID') # This must include new generators or be a seperate dataframe?
    df_cost = pd.read_csv('revenue_cost_gen.csv').set_index('Generator')    
    times = df_price_DA.index 
    # Used to name generators
    df_nodes = pd.read_csv('nodes.csv')
    extragen = len(df_generators) - 12 # Started with 12 generators
    nnodes = len(df_nodes) 
    
    if timeperiod == 'Weak':
        period = 52
    elif timeperiod == 'Year':
        period = 1
    
    # Dictionary containing zonal market prices
    MarketPriceDict = {}
    for t in times:
        for z in np.arange(len(zones)):
            MarketPriceDict[df_price_DA.columns[z], t] = df_price_DA.loc[df_price_DA.index[t], df_price_DA.columns[z]]
       
    # Revenue from Day-Ahead market for each generator in each zone
    # Each generator will produce when the market price is above marg. cost.
    energyrevenues = {}
    energyrevenue = {}
    productions = {}
    production = {}
    for g in df_generators.index:
        for z in zones:
            for t in times:
                if df_generators['lincostold'][g] < (MarketPriceDict[z,t]):
                    energyrevenues[g,z,t] = (MarketPriceDict[z,t] * df_generators['capacityold'][g]) -\
                    ((MarketPriceDict[z,t]-(MarketPriceDict[z,t]-df_generators['lincostold'][g])) * df_generators['capacityold'][g])
                    productions[g,z,t] = df_generators['capacityold'][g]
                elif df_generators['lincostold'][g] >= (MarketPriceDict[z,t]):
                    energyrevenues[g,z,t] = 0
                    productions[g,z,t] = 0
            energyrevenue[g,z] = sum(energyrevenues[g,z,t] for t in times)
            production[g,z] = sum(productions[g,z,t] for t in times)

    # Revenue from premium, generator assumed dispatched 
    capacityrevenue = {}
    for z in zones:
        for g in df_generators.index:
            capacityrevenue[g,z] = df_cost['Premium'][g] * df_cost['TotalProduction'][g]
    
    # Total revenue from capacity market and energy market
    revenue = {}        
    for z in zones:
        for g in df_generators.index:
            revenue[g,z] = energyrevenue[g,z] + capacityrevenue[g,z]  

    # Variable cost
    varcost = {}
    for z in zones:
        for g in df_generators.index:
            varcost[g,z] =  production[g,z] * df_generators['varomcost'][g]
    
    # Fixed costs
    fixedcost = {}
    for z in zones:
        for g in df_generators.index:
            fixedcost[g,z] = (df_generators['fixedomcost'][g] * df_generators['capacityold'][g])/period

    # Capital costs
    capcost = {}
    for z in zones:
        for g in df_generators.index:
            capcost[g,z] = (df_generators['levcapcost'][g]*1000000*df_generators['capacityold'][g])/period

    sumcost = {}
    for z in zones:
        for g in df_generators.index:
            sumcost[g,z] = varcost[g,z] + fixedcost[g,z] + capcost[g,z]

    # Calculating possible profit for generators
    profit = {}
    for z in zones:
        for g in df_generators.index:
            if revenue[g,z] > sumcost[g,z]:
                profit[g,z] = revenue[g,z] - sumcost[g,z]
            elif revenue[g,z] < sumcost[g,z]: 
                profit[g,z] = 0

    # Dictionary containing profitable generator types
    zone_generator = df_generators[['country','name']].values.tolist()
    gens_for_zone = defaultdict(list) 
    for country, generator in zone_generator:
        gens_for_zone[country].append(generator) 

    newgens = {}
    for z in zones:
        for g in df_generators.index:
            if sum(df_generators['capacity']) < sum(df_capacityreq['CapacityReq']):
                if sum(df_generators['capacity'][i] for i in gens_for_zone[z]) < df_capacityreq['CapacityReq'][z]:
                    if profit[g,z] > 0:
                        newgens.setdefault(z,[]).append(g)
            elif sum(df_generators['capacity']) > sum(df_capacityreq['CapacityReq']):
                if sum(df_generators['capacity'][i] for i in gens_for_zone[z]) >= df_capacityreq['CapacityReq'][z]:
                    if profit[g,z] > 0 and production[g,z] > 0:
                        newgens.setdefault(z,[]).append(g)

    # Dataframe with new generators
    geninv = pd.DataFrame(columns=df_generators.columns)
    for z in newgens.keys():
        for g in newgens[z]:
            tempdf = df_generators.loc[[g]]
            tempdf.name = "{arg1}{arg2}".format(arg1=g, arg2=z)
            tempdf.country = z
            tempdf.age = 'new'
            geninv = geninv.append(tempdf)  
            geninv.index = geninv.name
                        
    # Excluding hydro investments and two types of same generator in each zone
    geninv = geninv[geninv.primaryfuel != 'Hydro']
    geninv = geninv.drop_duplicates(subset=['country', 'lincostold'], keep='first')
    
    geninv['cum_sum'] = geninv['latitude'].cumsum()
    for g in geninv.index:
        geninv.name[g] = 'g%d' % (nnodes+extragen+geninv['cum_sum'][g])
        geninv['lincost'][g] = geninv['lincostold'][g] 

    geninv.index = geninv.name
    del geninv['cum_sum']
    
    df_generators = pd.concat([geninv, df_generators]).reset_index()
    df_generators.rename(columns={'index': 'ID'}, inplace=True)
    df_generators = df_generators.set_index('ID')
    
    newgens = geninv.index
    
    for g in newgens:
        df_cost.loc[g] = [0,0,0,0,0,0,0,0,0,0,0,0]
        df_cost['Capacity'] = df_generators.capacity
        df_cost['MarginalCost'] = df_generators.lincost
        df_cost['S/Ucost'] = df_generators.cyclecost
        df_cost['FixedO&MCost'] = df_generators.fixedomcost
        df_cost['VarO&MCost'] = df_generators.varomcost
        df_cost['LevelizedCapitalCost'] = df_generators.levcapcost
        df_cost['PrimaryFuel'] = df_generators.primaryfuel

        if df_cost['PrimaryFuel'][g] == typegenerator:
            df_cost['Premium'][g] = premiumfind 
        elif df_cost['PrimaryFuel'][g] != typegenerator:
            df_cost['Premium'][g] = 0

        if df_cost['PrimaryFuel'][g] == typegenerator:
            df_cost['MarginalCost'][g] = df_generators.lincost[g] - df_cost['Premium'][g]
        elif df_cost['PrimaryFuel'][g] != typegenerator:
            df_cost['MarginalCost'][g] = df_generators.lincost[g]

        df_generators['lincost'][g] = df_cost['MarginalCost'][g]

        if df_generators['lincost'][g] < 0:
            df_generators['lincost'][g] = -0.1
            df_cost['MarginalCost'][g] = -0.1
        elif df_generators['lincost'][g] >= 0:
            df_generators['lincost'][g] = df_generators['lincost'][g]
            df_cost['MarginalCost'][g] = df_cost['MarginalCost'][g]
    
    df_generators.to_csv('generators.csv')        
    
    return df_generators, df_cost





  

    
    
    
    
    
    
    
    