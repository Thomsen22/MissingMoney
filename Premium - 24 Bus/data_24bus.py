import pandas as pd
import numpy as np
import networkx as nx

def load():
    relloaddf = pd.read_csv('load_rel.csv').set_index('node')
    
    loadtimedf = pd.read_csv('load.csv').set_index('time')
    
    fulloaddf = pd.DataFrame(data=np.outer((loadtimedf['total']), relloaddf['relativeload']), index = loadtimedf.index, columns = relloaddf.index)
    
    return fulloaddf
    
def windprod():
    
    windprodwest = pd.read_csv('wind_prod.csv').set_index('time')
    
    windprodwest['weightedprod'] = windprodwest['windproduction']/max(windprodwest['windproduction'])
    
    turbinedf = pd.read_csv('wind_turbines.csv').set_index('node') 
    
    windprodwestdf = pd.DataFrame(data=np.outer(windprodwest['weightedprod'], turbinedf['turbines']), index = windprodwest.index, columns = turbinedf.index)
    
    return windprodwestdf
    
def solarprod():
    
    solarprodwest = pd.read_csv('solar_prod.csv').set_index('time')
    
    solarprodwest['weightedprod'] = solarprodwest['solarproduction']/max(solarprodwest['solarproduction'])
    
    turbinedf = pd.read_csv('solar_cells.csv').set_index('node') 
    
    solarprodwestdf = pd.DataFrame(data=np.outer(solarprodwest['weightedprod'], turbinedf['cells']), index = solarprodwest.index, columns = turbinedf.index)
    
    return solarprodwestdf

def load_generators(generatorfile='generators.csv'):
    
    generators = pd.read_csv(generatorfile).set_index('ID') 
    
    return generators 

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