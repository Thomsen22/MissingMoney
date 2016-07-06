# Python standard modules
import pandas as pd
# Own modules
from PLR_optclass import PLRMarket
import PLR_optimization as plrmodel

def PeakLoadReserveFunction():
    market = PLRMarket()
    market.optimize()

    df_generators = market.data.generators
    gens_for_zones = market.data.gens_for_country
    peakload = market.data.peakload
    df_cost = market.data.cost    
    zones = market.data.zones
    times = market.data.times
    df_gencapacity = pd.DataFrame({'capacity': {g: market.variables.gcap[g].x for g in df_generators.index}})
    df_zonalconsumption = pd.DataFrame(index = times, data = {z: [market.data.zonalconsumption[z,t] for t in times] for z in zones})
    reservemargin = market.data.reservemargin
    timeperiod = market.data.timeperiod
    model = market.data.model
    bidtype = market.data.BidType

    # Model types are controlled from the PLR_optclass 
    # ActivationPrice = df_generators['lincostold'].max() + 1 # max + 1
    ActivationPrice = 280
    for g in df_generators.index:
        if model == 'Swedish':
            if df_gencapacity['capacity'][g] > 0:
                df_generators['lincost'][g] = ActivationPrice + (df_generators['lincostold'][g]*0.05)
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
    
    return Gen_dataframe, df_zonalconsumption, reservemargin, df_price_DA, df_windprod, df_solarprod, gens_for_zones, df_generators, zones, peakload, timeperiod
    
def peakloadreserveoptimization():

    Gen_dataframe, df_zonalconsumption, reservemargin, df_price_DA, df_windprod, df_solarprod, gens_for_zones, df_generators, zones, peakload, timeperiod = PeakLoadReserveFunction()
    
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
    
    # The activation, deactivation and investment loop can be run by removing the # in the following line of code:
    
    #for z in zones:
        #if sum(df_generators['capacity'][g] for g in gens_for_zones[z]) > (peakload[z] * reservemargin):
            #df_generators = plrmodel.plantdeactivation(zones, gens_for_zones, df_zonalconsumption, reservemargin, Gen_dataframe)
        #elif sum(df_generators['capacity'][g] for g in gens_for_zones[z]) < (peakload[z] * reservemargin):
            #df_generators = plrmodel.plantactivation(zones, gens_for_zones, df_zonalconsumption, reservemargin)
 
    #df_generators = plrmodel.plantinvestment(df_price_DA, zones, gens_for_zones, timeperiod, reservemargin, peakload)  


    # Data to csv files, remove the #
    #df_price_DA.to_csv('1dayaheadmarketprices.csv')
    #df_solarprod.to_csv('1solarproduction.csv')
    #df_windprod.to_csv('1windproduction.csv')

    return Gen_dataframe, df_generators, totalwindcost, totalsolarcost, wind_penetration, solar_penetration
