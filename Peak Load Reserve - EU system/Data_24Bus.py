# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 09:00:51 2016

@author: Søren
"""
import pandas as pd
import numpy as np
import networkx as nx
from collections import defaultdict

#%% Load the data frame and returns the consumption

def load():
    relloaddf = pd.read_csv('load_rel.csv').set_index('node')
    
    loadtimedf = pd.read_csv('load_time.csv').set_index('time') # Reads the data, sets index
    
    fulloaddf = pd.DataFrame(data=np.outer((loadtimedf['tot']*0.001), relloaddf['relativeload']), index = loadtimedf.index, columns = relloaddf.index)
    
    #fulloaddf.to_csv('load.csv', float_format = '%.3f')
    
    return fulloaddf
    
#consumption = load()
#times = consumption.index # index = times
#nodes = consumption.columns # columns = nodes

#%% Assemble the windproduction matrix, create random production

def wind(windproduction): # Windprofile determined from beta function
    turbinedf = pd.read_csv('wind_turbines.csv').set_index('node') # Determine turbine sizes
    
    onesdf = pd.read_csv('ones.csv').set_index('time') # Matrix with ones

    capacitydf = pd.DataFrame(data=np.outer(onesdf['ones'], turbinedf['turbines']), index = onesdf.index, columns = turbinedf.index)

# Capacity on the wind turbines is assigned to each node, 24x24 matrix
# https://en.wikipedia.org/wiki/Beta_distribution
# Beta distribution: Gives higher values with a higher alpha
# The wind production is given as a value between 0 and 1 randomly chosen by the beta function

    if windproduction == 'Low':
        winddf = pd.read_excel('Wind_Production.xlsx', 'Low_Wind').set_index('Time')

    elif windproduction == 'Medium':
        winddf = pd.read_excel('Wind_Production.xlsx', 'Medium_Wind').set_index('Time')

    elif windproduction == 'High':
        winddf = pd.read_excel('Wind_Production.xlsx', 'High_Wind').set_index('Time')
    
    production = capacitydf * winddf
        
    return production
    
def windprod(): # Windprofile determined by scaled DK-East wind production
    
    windprodwest = pd.read_csv('windprodwest2015.csv').set_index('time')
    
    windprodwest['weightedprod'] = windprodwest['windproduction']/max(windprodwest['windproduction'])
    
    turbinedf = pd.read_csv('wind_turbines.csv').set_index('node') 
    
    windprodwestdf = pd.DataFrame(data=np.outer(windprodwest['weightedprod'], turbinedf['turbines']), index = windprodwest.index, columns = turbinedf.index)
    
    return windprodwestdf
    
#%% Load the generators 
 
def load_generators(generatorfile='generators.csv'):
    
    generators = pd.read_csv(generatorfile).set_index('ID') 
    
    return generators 

#%% Load the network

def load_network(nodefile='nodes.csv', linefile='lines.csv'):
    
    nodes = pd.read_csv(nodefile) 
    lines = pd.read_csv(linefile) 

    G = nx.Graph() 
    G.add_nodes_from(nodes.ID.values) 
    G.add_edges_from(lines.set_index(['fromNode', 'toNode']).index) 

    nodes['pos'] = [(lon, lat) for lon, lat in zip(nodes.longitude, nodes.latitude)] 

    for cn, s in nodes.set_index('ID').iteritems(): 
        nx.set_node_attributes(G, cn, s.to_dict())

    for cn, s in lines.set_index(['fromNode', 'toNode']).iteritems():
        nx.set_edge_attributes(G, cn, s.to_dict())
    
    return G


#%% The following is just notes and can be deleted

network = load_network()

country = nx.get_node_attributes(network, 'country')
country = pd.Series(country, name='Zone')
country = country.reset_index()
country = country.rename(columns={'index': 'Node'})
countries = country
        # Using defaultdict
zones_nodes = country[['Zone','Node']].values.tolist()
nodes_for_zones = defaultdict(list)
for Node,Zone in zones_nodes:
    nodes_for_zones[Node].append(Zone)

lines = network.edges()

df_nodes = pd.read_csv('nodes.csv') 
df_lines = pd.read_csv('lines.csv') 

df_lines['fromzone'] = pd.Series(np.random.randn(len(df_lines['fromNode'])), index=df_lines.index)
df_lines['tozone'] = pd.Series(np.random.randn(len(df_lines['fromNode'])), index=df_lines.index)

for a in df_lines.index:
    for b in df_nodes.index:
        if df_lines['fromNode'][a] == df_nodes['name'][b]:
            df_lines['fromzone'][a] = df_nodes['country'][b]
        if df_lines['toNode'][a] == df_nodes['name'][b]:
            df_lines['tozone'][a] = df_nodes['country'][b]

df_lines_new = df_lines[df_lines['fromzone'] != df_lines['tozone']]





'''
        self.data.zonecons = {}
        for z in self.data.zones:
            for l in self.data.lines:
                if l[0] == z:
                    self.data.zonecons.setdefault(z,[]).append(l[1])
                elif l[1] == z:
                    self.data.zonecons.setdefault(z,[]).append(l[0])
        
'''













