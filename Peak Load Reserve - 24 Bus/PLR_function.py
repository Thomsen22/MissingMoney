# Python standard modules
import pandas as pd
# Own modules
from PLR_optclass import PLRclass
import optimization as results
import PLR_optimization as plrmodel

def PLRmarket():
    market = PLRclass()
    market.optimize()

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
    
    ActivationPrice = df_generators['lincostold'].max() + 1 
    # ActivationPrice = 1000 
    
    for g in df_generators.index:
        if model == 'Swedish':
            if df_gencapacity['capacity'][g] > 0:
                df_generators['lincost'][g] = ActivationPrice + (df_generators['lincostold'][g]*0.05)
            elif df_gencapacity['capacity'][g] <= 0:
                df_generators['lincost'][g] = df_generators['lincostold'][g]

    df_generators.to_csv('generators.csv')
  
    df_price, df_genprod, df_lineflow, df_loadshed, df_windsolarload, df_revenueprod, network, times, generators, startup_number_df, df_zonalconsumption, df_windprod, df_solarprod = results.optimization()
    
    # Cost of wind
    windcost = {}
    for z in df_price.columns:
        for t in df_price.index:
            windcost[z,t] = df_windprod[z][t] * df_price[z][t]

    totalwindcost = sum(windcost.values())
    
    # Cost of solar
    solarcost = {}
    for z in df_price.columns:
        for t in df_price.index:
            solarcost[z,t] = df_solarprod[z][t] * df_price[z][t]

    totalsolarcost = sum(solarcost.values())
    
    windpenlevel = df_windsolarload['WindPenetration[%]'].mean()
    solarpenlevel = df_windsolarload['SolarPenetration[%]'].mean()    
  
    # A dataframe is returned to Excel for further work
    Gen_dataframe = df_revenueprod
    Gen_dataframe['TotalRevenue'] = Gen_dataframe['Total Revenue'].map('{:.2f}'.format)
    Gen_dataframe['TotalProduction'] = Gen_dataframe['Total Production'].map('{:.2f}'.format)
    Gen_dataframe['NumberofS/U'] = startup_number_df['Total Start-Ups']
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
    
    return df_gencapacity, df_zonaldemand, df_price, zones, df_generators, df_zonalconsumption, Gen_dataframe, gens_for_zones, reservemargin, timeperiod, df_cost, windpenlevel, totalwindcost, solarpenlevel, totalsolarcost

def plroptimization():
    df_gencapacity, df_zonaldemand, df_price, zones, df_generators, df_zonalconsumption, Gen_dataframe, gens_for_zones, reservemargin, timeperiod, df_cost, windpenlevel, totalwindcost, solarpenlevel, totalsolarcost = PLRmarket()
    
    df_zonalconsumption['AllZones'] = df_zonalconsumption.sum(axis=1)
    systemreserve = df_zonalconsumption['AllZones'].max() * reservemargin
    del df_zonalconsumption['AllZones']

    # Choose to activate or deactivate depending on systemreserve margin
    if df_generators['capacity'].sum(axis=0) > systemreserve:
        df_generators = plrmodel.plantdeactivation(zones, gens_for_zones, df_zonalconsumption, reservemargin, Gen_dataframe)
    elif df_generators['capacity'].sum(axis=0) < systemreserve:
        df_generators = plrmodel.plantactivation(zones, gens_for_zones, df_zonalconsumption, reservemargin)
      
    # Investment analysis can be enabled here:
      
    # df_generators = plrmodel.plantinvestment(df_price, timeperiod, zones, systemreserve)

    
    
    return Gen_dataframe, df_generators, windpenlevel, totalwindcost, solarpenlevel, totalsolarcost

