# Python standard modules
import numpy as np
import pandas as pd
from collections import defaultdict
# Own modules
import optimization as results
import loaddataEU as data

def DayAheadMarket():    
    consumption = data.load()
    windproduction = data.wind()
    solarproduction = data.solar()
    
    generators = pd.read_csv('generators.csv', sep=',', encoding='latin-1').set_index('ID')
    country = generators['country'].unique().tolist()
    transmissioncapacity = pd.read_csv('transmissioncapacity.csv', sep=',', encoding='latin-1').set_index('line')
    
    priceopt = pd.DataFrame(index = list(range(0,8760)), columns = country)
    priceopt.fillna(0, inplace = True)
    priceopt.index.rename('time', inplace=True) 

    windopt = pd.DataFrame(index = list(range(0,8760)), columns = country)
    windopt.fillna(0, inplace = True)
    windopt.index.rename('time', inplace=True) 

    solaropt = pd.DataFrame(index = list(range(0,8760)), columns = country)
    solaropt.fillna(0, inplace = True)
    solaropt.index.rename('time', inplace=True) 

    loadshedopt = pd.DataFrame(index = list(range(0,8760)), columns = country)
    loadshedopt.fillna(0, inplace = True)
    loadshedopt.index.rename('time', inplace=True) 

    zonalconsumptionopt = pd.DataFrame(index = list(range(0,8760)), columns = country)
    zonalconsumptionopt.fillna(0, inplace = True)
    zonalconsumptionopt.index.rename('time', inplace=True) 
    
    lineflowopt = pd.DataFrame(index = list(range(0,8760)), columns = transmissioncapacity.index)
    lineflowopt.fillna(0, inplace = True)
    lineflowopt.index.rename('time', inplace=True) 

    genprodopt = pd.DataFrame(index = list(range(0,8760)), columns = generators.index)
    genprodopt.fillna(0, inplace = True)
    genprodopt.index.rename('time', inplace=True)    
   
    optimizationtimes = list(range(1,366))

    for t in optimizationtimes:
        consumptionopt = consumption.loc[24*t-24+1:24*t]
        windprodopt = windproduction.loc[24*t-24+1:24*t]
        solarprodopt = solarproduction.loc[24*t-24+1:24*t]
        
        index = list(range(1,25))
        
        consumptionopt = consumptionopt.reset_index()
        windprodopt = windprodopt.reset_index()
        solarprodopt = solarprodopt.reset_index()
        
        consumptionopt['time'] = index
        windprodopt['time'] = index
        solarprodopt['time'] = index
        
        consumptionopt = consumptionopt.set_index('time')
        windprodopt = windprodopt.set_index('time')
        solarprodopt = solarprodopt.set_index('time')
        
        consumptionopt.to_csv('consumptionopt.csv')
        windprodopt.to_csv('windprodopt.csv')
        solarprodopt.to_csv('solarprodopt.csv')

        df_zonalconsumption, df_price, df_genprod, df_lineflow, df_loadshed, df_windprod, df_solarprod, generators  = results.optimization()

        for l in df_lineflow.index:
            lineflowopt.ix[24*t-24+l] = df_lineflow.ix[l]
            priceopt.ix[24*t-24+l] = df_price.ix[l]
            windopt.ix[24*t-24+l] = df_windprod.ix[l]
            solaropt.ix[24*t-24+l] = df_solarprod.ix[l]
            genprodopt.ix[24*t-24+l] = df_genprod.ix[l]
            loadshedopt.ix[24*t-24+l] = df_loadshed.ix[l]
            zonalconsumptionopt.ix[24*t-24+l] = df_zonalconsumption.ix[l]

    times = priceopt.index
    zones = priceopt.columns    
    
    # Total consumption in the system subtracted loadshedding
    Consumption = zonalconsumptionopt.set_index(np.arange(0,len(zonalconsumptionopt)))
    Consumption = (Consumption.sum(axis=1)) - (loadshedopt.sum(axis=1))

    # Calculating the wind penetration level
    WindPenetration = (windopt.sum(axis=1) / Consumption) * 100
    
    # Calculating the solar penetration level
    SolarPenetration = (solaropt.sum(axis=1) / Consumption) * 100
    
    WindLoad_df = pd.DataFrame({'Time':WindPenetration.index, 'WindProduction[MW]':windopt.sum(axis=1).values,\
    'SolarProduction[MW]':solaropt.sum(axis=1).values, 'TotalConsumption[MW]': Consumption.values, 'WindPenetration[%]':WindPenetration.values,\
    'SolarPenetration[%]':SolarPenetration.values}).set_index('Time')

    # Assigning each zone to a generator
    zone_generator = generators[['name','country']].values.tolist()
    zone_for_gens = defaultdict(list)
    for generator, zone in zone_generator:
        zone_for_gens[generator].append(zone)
    
    # Creating a dictionary to contain the market prices
    pricedict = {}
    for t in times:
        for z in np.arange(len(zones)):
            pricedict[priceopt.columns[z], t] = priceopt.ix[priceopt.index[t], priceopt.columns[z]]

    # Creating a dictionary to contain the generator production
    genproddict = {}
    for t in times:
        for g in np.arange(len(generators.index)):
            genproddict[genprodopt.columns[g], t] = genprodopt.ix[genprodopt.index[t], genprodopt.columns[g]]

    # Calculating the revenue for each generator
    revenue = {}
    for t in times:
        for g in generators.index:
            for z in zone_for_gens[g]:
                revenue[g, t] = pricedict[z, t] * genproddict[g, t]
    
    # Summing the revenues for all hours 
    revenue_total = {}
    for g in generators.index:
        revenue_total[g] = sum(revenue[g, t] for t in times)

    df_revenue = pd.DataFrame([[key,value] for key,value in revenue_total.items()],columns=["Generator","TotalRevenue"]).set_index('Generator')
     
     # Catching the start-up number of each generator
    startup_number = {}
    for t in times[1:]:
        for g in generators.index:
            startup_number[g, t] = 0 
            if(genproddict[g, t] > 0 and genproddict[g, t-1] == 0):
                startup_number[g, t] = 1
                
    # Summing total number of start-ups for all generators
    startup_number_total = {}
    for g in generators.index:
        startup_number_total[g] = sum(startup_number[g,t] for t in times[1:])
    
    startup_number_df = pd.DataFrame([[key,value] for key,value in startup_number_total.items()],columns=["Generator","TotalStart-Ups"]).set_index('Generator')
     
    # A dataframe is returned to Excel for further work
    Gen_dataframe = df_revenue
    Gen_dataframe['TotalRevenue'] = Gen_dataframe['TotalRevenue'].map('{:.2f}'.format)
    Gen_dataframe['TotalProduction'] = genprodopt.sum(axis=0)
    Gen_dataframe['TotalProduction'] = Gen_dataframe['TotalProduction'].map('{:.2f}'.format)
    Gen_dataframe['NumberofS/U'] = startup_number_df['TotalStart-Ups']
    Gen_dataframe['Capacity'] = generators.capacity
    Gen_dataframe['MarginalCost'] = generators.lincost
    Gen_dataframe['S/Ucost'] = generators.cyclecost
    Gen_dataframe['FixedO&MCost'] = generators.fixedomcost
    Gen_dataframe['VarO&MCost'] = generators.varomcost
    Gen_dataframe['LevelizedCapitalCost'] = generators.levcapcost
    Gen_dataframe['PrimaryFuel'] = generators.primaryfuel
    Gen_dataframe['Country'] = generators.country
    Gen_dataframe.to_csv('revenue_cost_gen.csv') 
        
    return lineflowopt, priceopt, windopt, solaropt 
    
def PLR(timeperiod, approach):
    df_cost = pd.read_csv('revenue_cost_gen.csv', sep=',', encoding='latin-1').set_index('Generator')
    df_cost_PLR = pd.read_csv('revenue_cost_gen_PLR.csv', sep=',', encoding='latin-1').set_index('Generator')
    df_generators = pd.read_csv('generators.csv', sep=',', encoding='latin-1').set_index('ID')
    
    if timeperiod == 'Weak':
        period = 52
    elif timeperiod == 'Year':
        period = 1

    # Missing money from variable costs
    varcost = {}
    for g in df_generators.index:
        varcost[g] = (df_cost['TotalProduction'][g]*df_generators['lincostold'][g]\
        + df_cost['TotalProduction'][g]*df_cost['VarO&MCost'][g]+df_cost['S/Ucost'][g]*df_cost['NumberofS/U'][g])

    mmvarcost = {}
    for g in df_generators.index:
        if df_cost['TotalRevenue'][g] - varcost[g] >= 0:
            mmvarcost[g] = 0
        elif df_cost['TotalRevenue'][g] - varcost[g] < 0:
            mmvarcost[g] = df_cost['TotalRevenue'][g] - varcost[g]
            
    variablemissingmoney = {}
    for g in df_generators.index:
        variablemissingmoney[g] = -(mmvarcost[g] / df_cost['Capacity'][g])
    
    df_variable = pd.DataFrame([[key,value] for key,value in variablemissingmoney.items()],columns=["Generator","MMVarCost"]).set_index('Generator')
    df_cost = pd.merge(df_cost, df_variable, right_index = True, left_index = True)

    # Missing money including fixed costs
    fixedcost = {}
    for g in df_generators.index:
        fixedcost[g] = (df_cost['FixedO&MCost'][g]*df_cost['Capacity'][g])/period

    mmfixedcost = {}
    for g in df_generators.index:
        if df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g]) >= 0:
            mmfixedcost[g] = 0
        elif df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g]) < 0:
            mmfixedcost[g] = df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g])

    fixedmissingmoney = {}
    for g in df_generators.index:
        fixedmissingmoney[g] = -(mmfixedcost[g] / df_cost['Capacity'][g])
    
    df_fixed = pd.DataFrame([[key,value] for key,value in fixedmissingmoney.items()],columns=["Generator","MMFixedCost"]).set_index('Generator')
    df_cost = pd.merge(df_cost, df_fixed, right_index = True, left_index = True)

    # Missing money including capital costs
    capcost = {}
    for g in df_generators.index:
        capcost[g] = (df_cost['LevelizedCapitalCost'][g]*1000000*df_cost['Capacity'][g])/period

    mmcapcost = {}
    for g in df_generators.index:
        if df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g] + capcost[g]) >= 0:
            mmcapcost[g] = 0
        elif df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g] + capcost[g]) < 0:
            mmcapcost[g] = df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g] + capcost[g])
    
    capitalmissingmoney = {}
    for g in df_generators.index:
        capitalmissingmoney[g] = -(mmcapcost[g] / df_cost['Capacity'][g])
        
    df_capital = pd.DataFrame([[key,value] for key,value in capitalmissingmoney.items()],columns=["Generator","MMCapCost"]).set_index('Generator')
    df_cost = pd.merge(df_cost, df_capital, right_index = True, left_index = True)
    
    missingmoney = {}
    for g in df_generators.index:
        if df_generators['age'][g] == 'old':
            missingmoney[g] = df_cost['MMFixedCost'][g]
        elif df_generators['age'][g] == 'new':
            missingmoney[g] = df_cost['MMCapCost'][g] 

    missingmoney_df = pd.DataFrame([[key,value] for key,value in missingmoney.items()],columns=["Generator","MissingMoney"]).set_index('Generator')
    df_cost = pd.merge(df_cost, missingmoney_df, right_index = True, left_index = True)
    
    if len(df_cost) != len(df_cost_PLR):
        # Dictionary containing profitable generator types
        newgens = {}
        for g in df_generators.index:
            if df_generators['age'][g] == 'new':
                newgens.setdefault('newgen',[]).append(g)

        # Dataframe with new generators
        geninv = pd.DataFrame(columns=df_cost_PLR.columns)
        for n in newgens.keys():
            for g in newgens[n]:
                tempdf = df_cost.loc[[g]]
                tempdf['PLRplants'] = 0
                tempdf['PLRbid'] = 0
                geninv = geninv.append(tempdf)
        
        df_cost_PLR = pd.concat([df_cost_PLR, geninv]).reset_index()
        df_cost_PLR = df_cost_PLR.set_index('Generator') 
        
    elif len(df_cost) == len(df_cost_PLR):
        df_cost_PLR = df_cost_PLR
    
    df_cost['MissingMoney'].fillna(0, inplace=True)
    # The bids are returned in €. All plants make a bid to become a PLR.
    plrbid = {}
    for g in df_generators.index:
        if approach == 'Approach1':
            if df_cost_PLR['PLRplants'][g] <= 0:
                if df_cost['MissingMoney'][g] > 0:
                    if df_generators['age'][g] == 'old': 
                        plrbid[g] = ((df_cost['FixedO&MCost'][g]*df_generators['capacityold'][g])+\
                        (df_cost['S/Ucost'][g]+5*(df_generators['lincostold'][g]+df_cost['VarO&MCost'][g])*df_generators['capacityold'][g]))
                    elif df_generators['age'][g] == 'new': 
                        plrbid[g] = ((df_cost['LevelizedCapitalCost'][g]*1000000*df_generators['capacityold'][g])+\
                        (df_cost['S/Ucost'][g]+5*(df_generators['lincostold'][g]+df_cost['VarO&MCost'][g])*df_generators['capacityold'][g]))
                elif df_cost['MissingMoney'][g] <= 0:
                    if df_generators['age'][g] == 'old':
                        plrbid[g] = ((df_cost['FixedO&MCost'][g]*df_generators['capacityold'][g])+\
                        (df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g]))+\
                        (df_cost['S/Ucost'][g]+5*(df_generators['lincostold'][g]+df_cost['VarO&MCost'][g])*df_generators['capacityold'][g]))
                    elif df_generators['age'][g] == 'new':
                        plrbid[g] = ((df_cost['LevelizedCapitalCost'][g]*1000000*df_generators['capacityold'][g])+\
                        (df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g]))+\
                        (df_cost['S/Ucost'][g]+5*(df_generators['lincostold'][g]+df_cost['VarO&MCost'][g])*df_generators['capacityold'][g]))
            elif df_cost_PLR['PLRplants'][g] > 0:
                plrbid[g] = df_cost_PLR['PLRbid'][g]

    # Bid size depending on simulation time
    plrbidnew = {}
    for g in df_generators.index:
        if df_cost_PLR['PLRplants'][g] <= 0:
            plrbidnew[g] = plrbid[g]/period
        elif df_cost_PLR['PLRplants'][g] > 0:
            plrbidnew[g] = plrbid[g]

    plrbid_df = pd.DataFrame([[key,value] for key,value in plrbidnew.items()],columns=["Generator","PLRbid"]).set_index('Generator')
    df_cost = pd.merge(df_cost, plrbid_df, right_index = True, left_index = True)
  
    return df_cost

def missingmoneyPLR(timeperiod, bidtype):
    df_generators = pd.read_csv('generators.csv', sep=',', encoding='latin-1').set_index('ID')  
    df_cost = pd.read_csv('revenue_cost_gen_PLR.csv', sep=',', encoding='latin-1').set_index('Generator')
    generators = df_cost.index    
    
    if timeperiod == 'Weak':
        period = 52
    elif timeperiod == 'Year':
        period = 1
    
    # Missing money from variable costs
    varcost = {}
    for g in generators:
        varcost[g] =  (df_cost['TotalProduction'][g]*df_cost['MarginalCost'][g]+df_cost['TotalProduction'][g]*df_cost['VarO&MCost'][g]+df_cost['S/Ucost'][g]*df_cost['NumberofS/U'][g])

    mmvarcost = {}
    for g in generators:
        if df_cost['TotalRevenue'][g] - varcost[g] >= 0:
            mmvarcost[g] = 0
        elif df_cost['TotalRevenue'][g] - varcost[g] < 0:
            mmvarcost[g] = df_cost['TotalRevenue'][g] - varcost[g]
    
    df_variable = pd.DataFrame([[key,value] for key,value in mmvarcost.items()],columns=["Generator","MMVarCost"]).set_index('Generator')
    df_cost = pd.merge(df_cost, df_variable, right_index = True, left_index = True)

    # Missing money including fixed costs
    fixedcost = {}
    for g in generators:
        fixedcost[g] = (df_cost['FixedO&MCost'][g]*df_cost['Capacity'][g])/period

    mmfixedcost = {}
    for g in generators:
        if df_cost['PLRplants'][g] == 0:
            if df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g]) >= 0:
                mmfixedcost[g] = 0
            elif df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g]) < 0:
                mmfixedcost[g] = df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g])
        elif df_cost['PLRplants'][g] > 0:
            mmfixedcost[g] = 0            
    
    df_fixed = pd.DataFrame([[key,value] for key,value in mmfixedcost.items()],columns=["Generator","MMFixedCost"]).set_index('Generator')
    df_cost = pd.merge(df_cost, df_fixed, right_index = True, left_index = True)

    # Missing money including capital costs
    capcost = {}
    for g in generators:
        capcost[g] = (df_cost['LevelizedCapitalCost'][g]*1000000*df_cost['Capacity'][g])/period

    mmcapcost = {}
    for g in generators:
        if df_cost['PLRplants'][g] == 0:
            if df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g] + capcost[g]) >= 0:
                mmcapcost[g] = 0
            elif df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g] + capcost[g]) < 0:
                mmcapcost[g] = df_cost['TotalRevenue'][g] - (varcost[g] + fixedcost[g] + capcost[g])
        elif df_cost['PLRplants'][g] > 0:
            mmcapcost[g] = 0

    df_capital = pd.DataFrame([[key,value] for key,value in mmcapcost.items()],columns=["Generator","MMCapCost"]).set_index('Generator')
    df_cost = pd.merge(df_cost, df_capital, right_index = True, left_index = True)
    
    missingmoney = {}
    for g in df_generators.index:
        if df_generators['age'][g] == 'old':
            missingmoney[g] = -df_cost['MMFixedCost'][g]
        elif df_generators['age'][g] == 'new':
            missingmoney[g] = -df_cost['MMCapCost'][g]
     
    df_missingmoney = pd.DataFrame([[key,value] for key,value in missingmoney.items()],columns=["Generator","MissingMoney"]).set_index('Generator')
    df_cost = pd.merge(df_cost, df_missingmoney, right_index = True, left_index = True)
         
    Gen_dataframe_PLR = df_cost
     
    return Gen_dataframe_PLR
    
#%% Deactivate plants 
def plantdeactivation(zones, gens_for_zones, df_zonalconsumption, reservemargin, df_cost):
    df_generators = pd.read_csv('generators.csv').set_index('ID')

    zonalreserve = {}
    for z in zones:
        zonalreserve[z] = df_zonalconsumption[z].max() * reservemargin
        
    df_zonalconsumption['AllZones'] = df_zonalconsumption.sum(axis=1)
    systemreserve = df_zonalconsumption['AllZones'].max() * reservemargin

    # Setting missing money for PLR plants to zero
    for g in df_cost.index:
        if df_cost['PLRplants'][g] > 0:
            df_cost['MissingMoney'][g] = 0

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

    # Mothballing plants 
    if df_generators['capacity'].sum(axis=0) > systemreserve:
        for z in zones:
            for g in gens_for_zones[z]:
                if sum(df_generators['capacity'][i] for i in gens_for_zones[z]) > zonalreserve[z]:
                    if df_cost['MissingMoney'][g] >= treshold[z] and df_cost['MissingMoney'][g] > 0:
                        df_generators['capacity'][g] = 0
                    if df_generators['capacity'].sum(axis=0) - df_generators['capacity'][g] < systemreserve:
                        df_generators['capacity'][g] = df_generators['capacityold'][g] 

    df_generators.to_csv('generators.csv') 

    return df_generators

def plantactivation(zones, gens_for_zones, zonaldemand_df, reservemargin):
    df_generators = pd.read_csv('generators.csv').set_index('ID')

    df_zonalconsumption = zonaldemand_df
    zonalreserve = {}
    for z in zones:
        zonalreserve[z] = df_zonalconsumption[z].max() * reservemargin

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
        capacityfind[z] = min(zonalcap, key=lambda x:abs(x-zonalreserve[z]))
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

def plantinvestment(df_price_DA, zones, gens_for_zones, timeperiod, reservemargin, peakload):
    df_generators = pd.read_csv('generators.csv', sep=',', encoding='latin-1').set_index('ID') # This must include new generators or be a seperate dataframe?
    df_generatorinvestment = pd.read_csv('generatorsinvestment.csv', sep=',', encoding='latin-1').set_index('ID')    
    times = df_price_DA.index 
    # Used to name generators
    df_nodes = pd.read_csv('nodes.csv')
    extragen = len(df_generators) # Started with 12 generators
    nnodes = len(df_nodes) 
    systemreserve = sum(peakload.values()) * reservemargin    
    
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
    for g in df_generatorinvestment.index:
        for z in zones:
            for t in times:
                if df_generatorinvestment['lincostold'][g] < (MarketPriceDict[z,t]):
                    energyrevenues[g,z,t] = (MarketPriceDict[z,t] * df_generatorinvestment['capacityold'][g]) -\
                    ((MarketPriceDict[z,t]-(MarketPriceDict[z,t]-df_generatorinvestment['lincostold'][g])) * df_generatorinvestment['capacityold'][g])
                    productions[g,z,t] = df_generatorinvestment['capacityold'][g]
                elif df_generatorinvestment['lincostold'][g] >= (MarketPriceDict[z,t]):
                    energyrevenues[g,z,t] = 0
                    productions[g,z,t] = 0
            energyrevenue[g,z] = sum(energyrevenues[g,z,t] for t in times)
            production[g,z] = sum(productions[g,z,t] for t in times)

    # Total revenue from capacity market and energy market
    revenue = {}        
    for z in zones:
        for g in df_generatorinvestment.index:
            revenue[g,z] = energyrevenue[g,z] 

    # Variable cost
    varcost = {}
    for z in zones:
        for g in df_generatorinvestment.index:
            varcost[g,z] =  production[g,z] * df_generatorinvestment['varomcost'][g]
    
    # Fixed costs
    fixedcost = {}
    for z in zones:
        for g in df_generatorinvestment.index:
            fixedcost[g,z] = (df_generatorinvestment['fixedomcost'][g] * df_generatorinvestment['capacityold'][g])/period

    # Capital costs
    capcost = {}
    for z in zones:
        for g in df_generatorinvestment.index:
            capcost[g,z] = (df_generatorinvestment['levcapcost'][g]*1000000*df_generatorinvestment['capacityold'][g])/period

    sumcost = {}
    for z in zones:
        for g in df_generatorinvestment.index:
            sumcost[g,z] = varcost[g,z] + fixedcost[g,z] + capcost[g,z]

    # Calculating possible profit for generators
    profit = {}
    for z in zones:
        for g in df_generatorinvestment.index:
            if revenue[g,z] > sumcost[g,z]:
                profit[g,z] = revenue[g,z] - sumcost[g,z]
            elif revenue[g,z] < sumcost[g,z]: 
                profit[g,z] = 0

    # Dictionary containing profitable generator types
    zone_generator = df_generators[['country','name']].values.tolist()
    gens_for_zone = defaultdict(list) 
    for country, generator in zone_generator:
        gens_for_zone[country].append(generator) 

    # Dictionary containing profitable generator types
    newgens = {}
    for z in zones:
        for g in df_generators.index:
            if sum(df_generators['capacity']) < systemreserve:
                if profit[g,z] > 0:
                    newgens.setdefault(z,[]).append(g)
            elif sum(df_generators['capacity']) > systemreserve:
                if profit[g,z] > 0 and production[g,z] > 0:
                    newgens.setdefault(z,[]).append(g)

    # Dataframe with new generators
    geninv = pd.DataFrame(columns=df_generatorinvestment.columns)
    for z in newgens.keys():
        for g in newgens[z]:
            tempdf = df_generatorinvestment.loc[[g]]
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
