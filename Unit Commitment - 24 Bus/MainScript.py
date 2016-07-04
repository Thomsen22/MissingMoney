# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 14:13:34 2016

@author: Søren
"""
# Own modules
import OptimizationResults as results
import drawnetwork as draw
# Python standard modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gurobipy as gb
import networkx as nx
from collections import defaultdict
import math
import seaborn as sns

#%% Optimization

# Runs the optimization
df_price, df_genprod, df_flow, df_loadshed, df_windprodload, df_revenuecost, network, times, generators, df_startups = results.optimization()

# Average wind penetration is displayed
Wind_Penetration = df_windprodload['WindPenetration[%]'].mean(axis=0)
print('Average Wind Penetration')
print(Wind_Penetration)

# A dataframe is returned to Excel for further work
Gen_dataframe = df_revenuecost
del Gen_dataframe['Total Costs']
Gen_dataframe['Total Revenue'] = Gen_dataframe['Total Revenue'].map('{:.2f}'.format)
Gen_dataframe['Total Production'] = Gen_dataframe['Total Production'].map('{:.2f}'.format)
Gen_dataframe['Number of S/U´s'] = df_startups['Total Start-Ups']
Gen_dataframe['Capacity'] = generators.capacity
Gen_dataframe['Marginal Cost'] = generators.lincost
Gen_dataframe['S/U cost'] = generators.cyclecost
Gen_dataframe['Fixed O&M Cost'] = generators.fixedomcost
Gen_dataframe['Var O&M Cost'] = generators.varomcost
Gen_dataframe['Levelized Capital Cost'] = generators.levcapcost
Gen_dataframe['Primary Fuel'] = generators.primaryfuel
Gen_dataframe.to_csv('revenue_cost_gen.csv')

