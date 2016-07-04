# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 14:13:34 2016

@author: Søren
"""

# Main script: 

# Should be run in order to undertake the optimization

# Own modules
import OptimizationResults as results
import PLR_opt as plrmodel
import PLR_function as plrfunction
# Python standard modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gurobipy as gb
import networkx as nx
from collections import defaultdict
import math
import seaborn as sns

Gen_dataframe, df_generators, windpenlevel, totalwindcost = plrfunction.plroptimization()



