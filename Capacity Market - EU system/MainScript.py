# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 14:13:34 2016

@author: Søren
"""
# Own modules
import OptimizationResults as results
# Python standard modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gurobipy as gb
import networkx as nx
from collections import defaultdict
import math
import seaborn as sns

import CM_function as CapMarket

df_price, df_gencapacity, df_cost, df_capacityreq, df_generators, df_price_DA, totalwindcost, df_windprod, df_solarprod, df_zonalconsumption, zones, gens_for_zones, timeperiod = CapMarket.capacitymarketoptimization()

df_capacityreq.to_csv('1capacityrequirement.csv')
df_price.to_csv('1capmarketprices.csv')
df_price_DA.to_csv('1dayaheadmarketprices.csv')
df_solarprod.to_csv('1solarproduction.csv')
df_windprod.to_csv('1windproduction.csv')
df_zonalconsumption.to_csv('1consumptionprofile.csv')
