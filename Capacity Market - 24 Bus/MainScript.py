# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 14:13:34 2016

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

# Capacity Market Optimization
import CM_function as CapMarket

df_price, df_gencapacity, df_cost, df_capacityreq, df_generators, df_price_DA, totalwindcost, totalsolarcost, windpenlevel, solarpenlevel = CapMarket.capacitymarketoptimization()


