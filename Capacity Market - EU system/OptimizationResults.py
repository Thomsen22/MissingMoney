# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:54:04 2016

@author: Søren
"""

# Python standard modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gurobipy as gb
import networkx as nx
from collections import defaultdict
import math
import seaborn as sns
# Own modules
import LoadDataEU as data
from DA_optclass import DayAhead

def optimization():
    market = DayAhead()
    market.optimize()
    
    times = market.data.times    
    zones = market.data.zones
    generators = market.data.generators
    lines = market.data.lines
    consumption = market.data.consumption
    network = market.data.network

    # Zonal consumption
    df_zonalconsumption = market.data.df_zonalconsumption
    
    # Zonal prices, found by taking the dual of the powerbalance constraint    
    df_price = pd.DataFrame(index = times, data = {z: [market.constraints.powerbalance[z,t].pi for t in times] for z in zones})

    # Generator production, 
    df_genprod = pd.DataFrame(index = times, data = {g: [market.variables.gprod[g,t].x for t in times] for g in generators.index})

    # Line flow, from zone -> to zone
    df_lineflow = pd.DataFrame(index = times, data = {l: [market.variables.linelimit[l,t].x for t in times] for l in lines})

    # Loadshedding in the system
    df_loadshed = pd.DataFrame(index = times, data = {z: [market.variables.loadshed[z,t].x for t in times] for z in zones})

    # Wind penetration (including wind curtailment)
    df_windprod = pd.DataFrame(index = times, data = {z: [market.variables.windprod[z,t].x for t in times] for z in zones})

    # Wind penetration (including wind curtailment)
    df_solarprod = pd.DataFrame(index = times, data = {z: [market.variables.solarprod[z,t].x for t in times] for z in zones})

    return df_zonalconsumption, df_price, df_genprod, df_lineflow, df_loadshed, df_windprod, df_solarprod, generators
    
