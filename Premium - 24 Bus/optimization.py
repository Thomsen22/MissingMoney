# Python standard modules
import numpy as np
import pandas as pd
from collections import defaultdict
# Own modules
from dayahead_optclass import DayAhead

def optimization():
    market = DayAhead()
    market.optimize()
    
    times = market.data.times
    zones = market.data.zones
    gens_for_zones = market.data.gens_for_country
    generators = market.data.generators
    lines = market.data.lines
    consumption = market.data.consumption
    network = market.data.network
    df_zonalconsumption = market.data.df_zonalconsumption

    # Zonal prices, found by taking the dual of the powerbalance constraint        
    df_price = pd.DataFrame(index = times, data = {z: [market.constraints.powerbalance[z,t].pi for t in times] for z in zones})

    # Generator production, 
    df_genprod = pd.DataFrame(index = times, data = {g: [market.variables.gprod[g,t].x for t in times] for g in generators.index})

    # Line flow, from node -> to node
    df_lineflow = pd.DataFrame(index = times, data = {l: [market.variables.linelimit[l,t].x for t in times] for l in lines})

    # Loadshedding in the system
    df_loadshed = pd.DataFrame(index = times, data = {z: [market.variables.loadshed[z,t].x for t in times] for z in zones})

    # Wind production
    df_windprod = pd.DataFrame(index = times, data = {z: [market.variables.windprod[z,t].x for t in times] for z in zones})
    windproduction = df_windprod.sum(axis=1)
    
    # Solar production
    df_solarprod = pd.DataFrame(index = times, data = {z: [market.variables.solarprod[z,t].x for t in times] for z in zones})
    solarproduction = df_solarprod.sum(axis=1)

    # Total consumption 
    total_consumption = consumption.set_index(np.arange(0,len(consumption)))
    total_consumption = (total_consumption.sum(axis=1)) - (df_loadshed.sum(axis=1))
    
    # Calculating the wind penetration level
    wind_penetration = (windproduction / total_consumption) * 100
    solar_penetration = (solarproduction / total_consumption) * 100
    df_windsolarload = pd.DataFrame({'Time': df_windprod.index, 'WindProduction[MW]': windproduction.values, 'SolarProduction[MW]': solarproduction.values,\
    'TotalConsumption[MW]': total_consumption.values, 'WindPenetration[%]': wind_penetration.values, 'SolarPenetration[%]': solar_penetration.values}).set_index('Time')

    # Assigning each zone to a generator
    zone_generator = generators[['name','country']].values.tolist()
    zone_for_gens = defaultdict(list)
    for generator, zone in zone_generator:
        zone_for_gens[generator].append(zone)
  
    # Creating a dictionary to contain the market prices
    dict_price = {}
    for t in times:
        for z in np.arange(len(zones)):
            dict_price[df_price.columns[z], t] = df_price.ix[df_price.index[t], df_price.columns[z]]
    
    # Creating a dictionary to contain the generator production
    dict_genprod = {}
    for t in times:
        for g in np.arange(len(generators.index)):
            dict_genprod[df_genprod.columns[g], t] = df_genprod.ix[df_genprod.index[t], df_genprod.columns[g]]

    # Calculating the revenue for each generator
    dict_revenue = {}
    for t in times:
        for g in generators.index:
            for z in zone_for_gens[g]:
                dict_revenue[g, t] = dict_price[z, t] * dict_genprod[g, t]
    
    # Summing the revenue for all hours 
    dict_revenue_total = {}
    for g in generators.index:
        dict_revenue_total[g] = sum(dict_revenue[g, t] for t in times)

    df_revenueprod = pd.DataFrame([[key,value] for key,value in dict_revenue_total.items()],columns=["Generator","Total Revenue"]).set_index('Generator')
    df_revenueprod['Total Production'] = df_genprod.sum(axis=0)    
    
    # Catching the start-up number
    dict_startup_number = {}
    for t in times[1:]:
        for g in generators.index:
            dict_startup_number[g, t] = 0 
            if(dict_genprod[g, t] > 0 and dict_genprod[g, t-1] == 0):
                dict_startup_number[g, t] = 1
                
    # Calculating total number of start-ups for all generators
    dict_startup_number_total = {}
    for g in generators.index:
        dict_startup_number_total[g] = sum(dict_startup_number[g,t] for t in times[1:])
    
    startup_number_df = pd.DataFrame([[key,value] for key,value in dict_startup_number_total.items()],columns=["Generator","Total Start-Ups"]).set_index('Generator')
  
    return df_price, df_genprod, df_lineflow, df_loadshed, df_windsolarload, df_revenueprod, network, times, generators, startup_number_df, df_zonalconsumption, df_windprod, df_solarprod, zones, gens_for_zones
  