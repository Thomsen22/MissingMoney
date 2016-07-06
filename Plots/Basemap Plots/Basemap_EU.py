import matplotlib.pyplot as plt
import networkx as nx
from mpl_toolkits.basemap import Basemap as Basemap
import pandas as pd

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

# Basemap of cpacity market clearing prices across Europe
m = Basemap(
        projection='cyl',
        llcrnrlon=-15,
        llcrnrlat=32,
        urcrnrlon=35,
        urcrnrlat=64,
        lat_ts=0,
        resolution='i',
        suppress_ticks=True)

m.drawcountries()
m.drawlsmask(land_color='white',ocean_color='lightblue',lakes=True)

network = load_network()
lines = network.edges()
pos = nx.get_node_attributes(network, 'pos') 

capprices = pd.read_csv('capmarketprices.csv')
df_nodes = pd.read_csv('nodes.csv').set_index('ID')

capmarketprice = {}
for n in df_nodes.index:
    for i in capprices.index:
        if df_nodes['country'][n] == capprices['country'][i]:
            capmarketprice[n] = capprices['Price'][i]

df_capmarketprice = pd.DataFrame([[key,value] for key,value in capmarketprice.items()],columns=["node","capmarketprice"]).set_index('node')
    
df_nodes = pd.merge(df_nodes, df_capmarketprice, right_index = True, left_index = True)

nodes = network.nodes()

colors = [df_nodes['capmarketprice'][n] for n in nodes]

ec = nx.draw_networkx_edges(network, pos, alpha=0.2)
nc = nx.draw_networkx_nodes(network, pos, nodelist=nodes, node_color=colors, 
                            with_labels=False, node_size=3, cmap=plt.cm.viridis, vmin=0, vmax=510)

txt = '$Capacity\ Market\ Clearing\ Price\ [$€$/MW-day]$'
                           
plt.text(45,64,txt,rotation=270)
plt.colorbar(nc)
plt.axis('off')

plt.savefig('EUsystemCapMarket.pdf') 
plt.show() 


# Basemap of the European test system
m = Basemap(
        projection='cyl',
        llcrnrlon=-15,
        llcrnrlat=32,
        urcrnrlon=35,
        urcrnrlat=64,
        lat_ts=0,
        resolution='i',
        suppress_ticks=True)

network = load_network()
lines = network.edges()
pos = nx.get_node_attributes(network, 'pos')

nx.draw_networkx(network,with_labels=False,pos=pos,node_color='blue',node_size=2)
nx.draw_networkx_edges(network,pos=pos,edges=lines,edge_color='lightblue', width=0.05)

m.drawcountries()
m.drawmapboundary(fill_color='black')
m.shadedrelief()
plt.title('European Test Model Network') 
plt.savefig('EUsystem.pdf') 
plt.show()  
 
