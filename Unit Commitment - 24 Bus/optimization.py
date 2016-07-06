# Python standard modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns
from itertools import cycle, islice
# Own modules
from dayahead_optclass import DayAhead


def optimization():
    market = DayAhead()
    market.optimize()
    
    times = market.data.times
    zones = market.data.zones
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
  
    # Assigning different types of generators
    hydro_gens = [g for g in generators.index if generators.primaryfuel[g] == 'Hydro']
    coal_gens = [g for g in generators.index if generators.primaryfuel[g] == 'Coal']
    gas_gens = [g for g in generators.index if generators.primaryfuel[g] == 'Gas']
    nuclear_gens = [g for g in generators.index if generators.primaryfuel[g] == 'Nuclear']
    oil_gens = [g for g in generators.index if generators.primaryfuel[g] == 'Oil']

    # Calculating total hourly production for all technologies
    hydroP = {}
    for g in hydro_gens:
        hydroP[g] = df_genprod[g]
        
    totalhydroP = {}    
    for t in times:
        totalhydroP[t] = sum(hydroP[g][t] for g in hydro_gens)
  
    coalP = {}
    for g in coal_gens:
        coalP[g] = df_genprod[g]
        
    totalcoalP = {}    
    for t in times:
        totalcoalP[t] = sum(coalP[g][t] for g in coal_gens)
    
    gasP = {}
    for g in gas_gens:
        gasP[g] = df_genprod[g]
    
    totalgasP = {}    
    for t in times:
        totalgasP[t] = sum(gasP[g][t] for g in gas_gens)
    
    nuclearP = {}
    for g in nuclear_gens:
        nuclearP[g] = df_genprod[g]
    
    totalnuclearP = {}    
    for t in times:
        totalnuclearP[t] = sum(nuclearP[g][t] for g in nuclear_gens)

    oilP = {}
    for g in oil_gens:
        oilP[g] = df_genprod[g]
    
    totaloilP = {}    
    for t in times:
        totaloilP[t] = sum(oilP[g][t] for g in oil_gens)

    # Returning respective production into a dataframe and merges
    Oil_df = pd.DataFrame([[key,value] for key,value in totaloilP.items()],columns=["Times", "Oil Production"])#.set_index('Times')
    Nuclear_df = pd.DataFrame([[key,value] for key,value in totalnuclearP.items()],columns=["Times", "Nuclear Production"])#.set_index('Times')
    Gas_df = pd.DataFrame([[key,value] for key,value in totalgasP.items()],columns=["Times", "Gas Production"])#.set_index('Times')
    Coal_df = pd.DataFrame([[key,value] for key,value in totalcoalP.items()],columns=["Times", "Coal Production"])#.set_index('Times')
    Hydro_df = pd.DataFrame([[key,value] for key,value in totalhydroP.items()],columns=["Times", "Hydro Production"])#.set_index('Times')
    Wind_df = pd.DataFrame(df_windsolarload['WindProduction[MW]'])
    Wind_df.rename(columns={'WindProduction[MW]': 'Wind Production'}, inplace=True)
    Wind_df['Times'] = times
    Solar_df = pd.DataFrame(df_windsolarload['SolarProduction[MW]'])
    Solar_df.rename(columns={'SolarProduction[MW]': 'Solar Production'}, inplace=True)
    Solar_df['Times'] = times

    df_prodtype = pd.DataFrame(Wind_df.merge(Solar_df,on='Times').merge(Hydro_df,on='Times')\
    .merge(Nuclear_df,on='Times').merge(Coal_df,on='Times').merge(Gas_df,on='Times').merge(Oil_df,on='Times').set_index('Times'))

    # Plots the production as an area diagram
    plt.figure(1)
    my_colors = list(islice(cycle([sns.xkcd_rgb["windows blue"], sns.xkcd_rgb["yellow"], sns.xkcd_rgb["pale red"]\
    , sns.xkcd_rgb["medium green"], sns.xkcd_rgb["amber"], sns.xkcd_rgb["deep purple"],'grey']), None, len(df_prodtype)))
    ax = df_prodtype.plot(kind='area', color=my_colors)

    ax.set_ylabel('$MW$')
    ax.set_xlabel('$Hours$')
    ax.set_axis_bgcolor('whitesmoke')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=3, fancybox=True, shadow=True)
          
    # plt.savefig('productionareaplot.pdf')
          
    plt.show()

    return df_price, df_genprod, df_lineflow, df_loadshed, df_windsolarload, df_revenueprod, df_prodtype, network, times, generators, startup_number_df, df_zonalconsumption, df_windprod, df_solarprod

def marketoptimization():
    
    df_price, df_genprod, df_lineflow, df_loadshed, df_windsolarload, df_revenueprod, df_prodtype, network, times, generators, startup_number_df, df_zonalconsumption, df_windprod, df_solarprod = optimization()
    
    wind_penetration = df_windsolarload['WindPenetration[%]'].mean(axis=0)
    solar_penetration = df_windsolarload['SolarPenetration[%]'].mean(axis=0)
    
    dict_windcost = {}
    for z in df_price.columns:
        for t in df_price.index:
            dict_windcost[z,t] = df_windprod[z][t] * df_price[z][t]

    totalwindcost = sum(dict_windcost.values())
    
    dict_solarcost = {}
    for z in df_price.columns:
        for t in df_price.index:
            dict_solarcost[z,t] = df_solarprod[z][t] * df_price[z][t]

    totalsolarcost = sum(dict_solarcost.values())

    # A dataframe is returned to Excel as a csv file for further work
    gen_dataframe = df_revenueprod
    gen_dataframe['Total Revenue'] = gen_dataframe['Total Revenue'].map('{:.2f}'.format)
    gen_dataframe['Total Production'] =  gen_dataframe['Total Production'].map('{:.2f}'.format)
    gen_dataframe['Number of S/U´s'] = startup_number_df['Total Start-Ups']
    gen_dataframe['Capacity'] = generators.capacity
    gen_dataframe['Marginal Cost'] = generators.lincost
    gen_dataframe['S/U cost'] = generators.cyclecost
    gen_dataframe['Fixed O&M Cost'] = generators.fixedomcost
    gen_dataframe['Var O&M Cost'] = generators.varomcost
    gen_dataframe['Levelized Capital Cost'] = generators.levcapcost
    gen_dataframe['Primary Fuel'] = generators.primaryfuel
    gen_dataframe.to_csv('revenue_cost_gen.csv')
    
    return gen_dataframe, wind_penetration, solar_penetration, totalwindcost, totalsolarcost
    