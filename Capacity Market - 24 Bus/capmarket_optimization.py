# Python standard modules
import numpy as np
import pandas as pd
from collections import defaultdict
# Own modules
import optimization as results

def DayAheadMarket():
    df_price, df_genprod, df_lineflow, df_loadshed, df_windsolarload, df_revenueprod, network, times, generators, startup_number_df, df_zonalconsumption, df_windprod, df_solarprod = results.optimization()

    gen_dataframe = df_revenueprod
    gen_dataframe['TotalRevenue'] = gen_dataframe['Total Revenue'].map('{:.2f}'.format)
    gen_dataframe['TotalProduction'] = gen_dataframe['Total Production'].map('{:.2f}'.format)
    gen_dataframe['NumberofS/U'] = startup_number_df['Total Start-Ups']
    gen_dataframe['Capacity'] = generators.capacity
    gen_dataframe['MarginalCost'] = generators.lincost
    gen_dataframe['S/Ucost'] = generators.cyclecost
    gen_dataframe['FixedO&MCost'] = generators.fixedomcost
    gen_dataframe['VarO&MCost'] = generators.varomcost
    gen_dataframe['LevelizedCapitalCost'] = generators.levcapcost
    gen_dataframe['PrimaryFuel'] = generators.primaryfuel
    gen_dataframe.to_csv('revenue_cost_gen.csv')
    
    return df_lineflow, df_price, df_windprod, df_solarprod, df_windsolarload

def missingmoney(timeperiod, bidtype):
    df_cost = pd.read_csv('revenue_cost_gen_CM.csv').set_index('Generator')
    df_generators = pd.read_csv('generators.csv').set_index('ID')
    generators = df_generators.index
    
    if timeperiod == 'Weak':
        period = 52
    elif timeperiod == 'Year':
        period = 1

    # The remaining missing money stemming from variable, fixed and capital cost is calculated seperately
    totalrevenue = {}
    for g in generators:
        totalrevenue[g] = df_cost['TotalRevenue'][g] + df_cost['RevenueCapMarket'][g]
    
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
    
    df_cost = pd.merge(df_cost, missingmoney_df, right_index = True, left_index = True)
        
    return df_cost
    
def plantdeactivation(zones, gens_for_zones, df_cost, df_capacityreq):
    df_generators = pd.read_csv('generators.csv').set_index('ID')
    
    # Finding the missing-money threshold in each zone (2 plants in each zone can be mothballed)
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

    # Note: Generators recieving capacity payments will not have missing money  
  
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

def plantinvestment(df_price_DA, df_price, zones, gens_for_zones, timeperiod, df_capacityreq):
    df_generators = pd.read_csv('generators.csv').set_index('ID') 
    times = df_price_DA.index 
    # Used to name generators
    df_nodes = pd.read_csv('nodes.csv')
    extragen = len(df_generators) - 12
    nnodes = len(df_nodes) 
    
    if timeperiod == 'Weak':
        period = 52
    elif timeperiod == 'Year':
        period = 1
    
    # Dictionary containing zonal market prices
    MarketPriceDict = {}
    for t in times:
        for z in np.arange(len(zones)):
            MarketPriceDict[df_price_DA.columns[z], t] = df_price_DA.ix[df_price_DA.index[t], df_price_DA.columns[z]]
       
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

    # Revenue from capacity market, generator assumed dispatched 
    capacityrevenue = {}
    for z in zones:
        for g in df_generators.index:
            capacityrevenue[g,z] = df_price['Price'][z] * df_generators['capacityold'][g]
    
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

    df_generators.to_csv('generators.csv')        
    
    return df_generators
