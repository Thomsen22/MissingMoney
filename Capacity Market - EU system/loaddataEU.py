import pandas as pd
import numpy as np
import networkx as nx
from collections import defaultdict

def load_generators():
    
    df_generators = pd.read_csv('generators.csv', sep=',', encoding='latin-1').set_index('ID')
     
    return df_generators

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

def load(loadfile='load.csv'):
    
    fulloaddf = pd.read_csv(loadfile).set_index('time')
        
    return fulloaddf

def wind(): 
    turbinedf = pd.read_csv('wind_turbines.csv').set_index('node') # Determine turbine sizes
    
    onesdf = pd.read_csv('ones.csv').set_index('time') # Matrix with ones

    capacitydf = pd.DataFrame(data=np.outer(onesdf['ones'], turbinedf['turbines']), index = onesdf.index, columns = turbinedf.index)

    winddf = pd.read_csv('wind.csv').set_index('time')
    
    production = pd.DataFrame(capacitydf.values*winddf.values, columns=winddf.columns, index=winddf.index)
        
    return production
    
def solar(): 
    solar_celldf = pd.read_csv('solar_cells.csv').set_index('node') # Determine turbine sizes
    
    onesdf = pd.read_csv('ones.csv').set_index('time') # Matrix with ones

    capacitydf = pd.DataFrame(data=np.outer(onesdf['ones'], solar_celldf['cells']), index = onesdf.index, columns = solar_celldf.index)

    solardf = pd.read_csv('solar.csv').set_index('time')
    
    production = pd.DataFrame(capacitydf.values*solardf.values, columns=solardf.columns, index=solardf.index)
        
    return production

def transcapacity(): # Finds the transmission capacities between zones
    df_nodes = pd.read_csv('nodes.csv') 
    df_lines = pd.read_csv('lines.csv')
    
    df_lines['fromzone'] = pd.Series(np.random.randn(len(df_lines['fromNode'])), index=df_lines.index)
    df_lines['tozone'] = pd.Series(np.random.randn(len(df_lines['fromNode'])), index=df_lines.index)

    for node in df_lines.index:
        for line in df_nodes.index:
            if df_lines['fromNode'][node] == df_nodes['ID'][line]:
                df_lines['fromzone'][node] = df_nodes['country'][line]
            if df_lines['toNode'][node] == df_nodes['ID'][line]:
                df_lines['tozone'][node] = df_nodes['country'][line]

    tozone = df_lines['tozone'].unique().tolist()
    fromzone = df_lines['fromzone'].unique().tolist()
    totalzone = list(set(fromzone+tozone))

    # At this point, total number of zones is found

    zonecons = {}
    for count in df_lines.index:
        for z in totalzone:
            if df_lines['fromzone'][count] == z:
                zonecons.setdefault(z,[]).append(df_lines['tozone'][count])
            elif df_lines['tozone'][count] == z:
                zonecons.setdefault(z,[]).append(df_lines['fromzone'][count])

    # At this point, all connections from and within each zone is found

    zoneforzones = {}
    for k,v in zonecons.items():
        d = defaultdict(int)
        for i in v:
            if i != k:
                d[i] = d[i]
        zoneforzones[k] = list(d.keys())

    # At this point, the connections from each zone is found

    zonenumber = {}
    for count in df_lines.index:
        for z in totalzone:
            for zone in zoneforzones[z]:
                if df_lines['fromzone'][count] == z and df_lines['tozone'][count] == zone:
                    zonenumber.setdefault((z,zone),[]).append(count)
                elif df_lines['tozone'][count] == z and df_lines['fromzone'][count] == zone:
                    zonenumber.setdefault((z,zone),[]).append(count)                

    # At this point, the connection number (place in df_lines) is found
    # The error is right here. Find a way to separate zone connections

    transcap = {}
    for z in list(zonenumber.keys()):
        transcap[z] = sum(df_lines['limit'][n] for n in zonenumber[z])

    linecapacity = pd.DataFrame({'Line' : list(transcap.keys()), 'Capacity' : list(transcap.values())})
    linecapacity = linecapacity.set_index('Line')

    linecapacity.to_csv('transmissioncapacity.csv')
    
    # Check the output file for more than 2 duplicates on capacity.
    # Then execute following code in the Python Console
    
    # Transcap = pd.read_csv('transmissioncapacity.csv', sep=',', encoding='latin-1').set_index('Line')
    # Transcap = Transcap.drop_duplicates(subset=['Capacity'], keep="first") 
    # Transcap.to_csv('transmissioncapacity.csv')

    return

def load_lines(loadfile='transmissioncapacity.csv'):
    
    df_lines = pd.read_csv(loadfile).set_index('line')
        
    return df_lines

def load_temporary():
    
    df_load = pd.read_csv('consumptionopt.csv', sep=',', encoding='latin-1').set_index('time')
    df_wind = pd.read_csv('windprodopt.csv', sep=',', encoding='latin-1').set_index('time')
    df_solar = pd.read_csv('solarprodopt.csv', sep=',', encoding='latin-1').set_index('time')     
          
    return df_load, df_wind, df_solar


