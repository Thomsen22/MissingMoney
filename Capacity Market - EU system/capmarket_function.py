# Python standard modules
import pandas as pd
# Own modules
from capmarket_optclass import CapacityMarket
import capmarket_opt as capmarket

def CapacityMarketFunction():
    
    market = CapacityMarket()
    market.optimize()
    zones = market.data.zones
    lines = market.data.lines
    bidtype = market.data.BidType
    timeperiod = market.data.timeperiod
    generators = market.data.generators
    gens_for_zones = market.data.gens_for_country
    zone_for_gens = market.data.zone_for_gens
    windreserve = market.data.zonalwindreserve
    df_price_DA = market.data.df_price_DA
    
    df_zonaldemand = pd.DataFrame({'Demand': {z: market.data.zonaldemand[z] for z in zones}})        
    df_price = pd.DataFrame({'Price': {z: market.constraints.powerbalance[z].pi for z in zones}})
    df_gencapacity = pd.DataFrame({'ClearedCapacity': {g: market.variables.gcap[g].x for g in generators.index}}) 
    df_windreserve = pd.DataFrame([[key,value] for key,value in market.data.zonalwindreserve.items()],columns=["Zone","Windreserve"]).set_index('Zone')
    df_cost = market.data.df_cost
    df_export = pd.DataFrame({'Export': {l: market.variables.linelimit[l].x for l in lines}})
    df_generators = market.data.generators
    df_zonalconsumption = market.data.df_zonalconsumption
    df_windprod = market.data.df_windprod
    df_solarprod = market.data.df_solarprod
    
    # Setting cleared capacity to max    
    for g in df_generators.index:
        if df_gencapacity['ClearedCapacity'][g] > 0:
            df_gencapacity['ClearedCapacity'][g] = df_generators['capacityold'][g]
    
    df_cost = pd.merge(df_cost, df_gencapacity, right_index = True, left_index = True) 
    
    capacityprice = {}
    for z in zones:
        capacityprice[z] = df_price['Price'][z]
       
    # Revenue dependent on marketprice in zone of generator location
    revenue = {}
    for g in df_generators.index:
        for z in zone_for_gens[g]:
            revenue[g] = capacityprice[z] * df_gencapacity['ClearedCapacity'][g]

    df_revenue = pd.DataFrame([[key,value] for key,value in revenue.items()],columns=["Generator","RevenueCapMarket"]).set_index('Generator')
    df_cost = pd.merge(df_cost, df_revenue, right_index = True, left_index = True)
    
    # Calculating the required amount of capacity in each zone
    export = {}
    for z in zones:
        export[z] = sum(df_export['Export'][l] for l in lines if l[0] == z) - sum(df_export['Export'][l] for l in lines if l[1] == z)

    capacityreq = {}
    for z in zones:
        capacityreq[z] = df_zonaldemand['Demand'][z] + export[z] - windreserve[z]

    df_capacityreq = pd.DataFrame([[key,value] for key,value in capacityreq.items()],columns=["Zones","CapacityReq"]).set_index('Zones')

    df_cost['MMVarCost'].fillna(0, inplace=True)
    df_cost['MMFixedCost'].fillna(0, inplace=True)
    df_cost['MMCapCost'].fillna(0, inplace=True)

    df_cost['MMVarCost'] = df_cost['MMVarCost'].map('{:.2f}'.format)
    df_cost['MMFixedCost'] = df_cost['MMFixedCost'].map('{:.2f}'.format)
    df_cost['MMCapCost'] = df_cost['MMCapCost'].map('{:.2f}'.format)
    df_cost['BidMM'] = df_cost['BidMM'].map('{:.2f}'.format)
    df_cost['RevenueCapMarket'] = df_cost['RevenueCapMarket'].map('{:.2f}'.format)

    df_cost = df_cost.reset_index()
    df_cost.rename(columns={'index': 'Generator'}, inplace=True)
    df_cost = df_cost.set_index('Generator')

    df_cost.to_csv('1revenue_cost_gen_CM.csv')    
    
    return df_zonaldemand, df_gencapacity, df_windreserve, df_cost, df_export, df_price, df_capacityreq, bidtype, timeperiod, zones, gens_for_zones, df_generators, df_price_DA, df_zonalconsumption, df_windprod, df_solarprod
    
def capacitymarketoptimization():
    df_zonaldemand, df_gencapacity, df_windreserve, df_cost, df_export, df_price, df_capacityreq, bidtype, timeperiod, zones, gens_for_zones, df_generators, df_price_DA, df_zonalconsumption, df_windprod, df_solarprod = CapacityMarketFunction()

    df_cost = capmarket.missingmoney(timeperiod, bidtype)
    
    # Cost of wind
    windcost = {}
    for z in df_price_DA.columns:
        for t in df_price_DA.index:
            windcost[z,t] = df_windprod[z][t] * df_price_DA[z][t]

    totalwindcost = sum(windcost.values())
    
    # Cost of solar
    solarcost = {}
    for z in df_price_DA.columns:
        for t in df_price_DA.index:
            solarcost[z,t] = df_solarprod[z][t] * df_price_DA[z][t]

    totalsolarcost = sum(solarcost.values())
    
    # Calculating the wind penetration level
    wind_penetration = (df_windprod.sum(axis=1) / df_zonalconsumption.sum(axis=1)) * 100
    
    # Calculating the solar penetration level
    solar_penetration = (df_solarprod.sum(axis=1) / df_zonalconsumption.sum(axis=1)) * 100
    
    # Check the reserve margin
    for z in zones:
        if sum(df_generators['capacity'][g] for g in gens_for_zones[z]) > df_capacityreq['CapacityReq'][z]:
            df_generators = capmarket.plantdeactivation(zones, gens_for_zones, df_cost, df_capacityreq)
        elif sum(df_generators['capacity'][g] for g in gens_for_zones[z]) < df_capacityreq['CapacityReq'][z]:
            df_generators = capmarket.plantactivation(zones, gens_for_zones, df_capacityreq)

    # Investment in new plants (Exogenous)

    # Turned on    
    df_generators = capmarket.plantinvestment(df_price_DA, df_price, zones, gens_for_zones, timeperiod, df_capacityreq)
    
    # Data can be send to csv.files:    
    
    #df_capacityreq.to_csv('1capacityrequirement.csv')
    #df_price.to_csv('1capmarketprices.csv')
    #df_price_DA.to_csv('1dayaheadmarketprices.csv')
    #df_solarprod.to_csv('1solarproduction.csv')
    #df_windprod.to_csv('1windproduction.csv')
    #df_zonalconsumption.to_csv('1consumptionprofile.csv')

    return df_cost, totalwindcost, totalsolarcost, wind_penetration, solar_penetration
