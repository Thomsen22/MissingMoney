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

import Premium_Function as PF

timeperiod = 'Weak'
bidtype = 'Fixed'
newpremium = 'yes'
reservemargin = 1.15

df_cost, df_price0, df_price1, df_zonalconsumption, df_generators, totalwindcost, totalsolarcost, windpenlevel, solarpenlevel, windproduction = PF.premiumfunction(timeperiod, bidtype, newpremium, reservemargin)
