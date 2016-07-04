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

# Runs the optimization
Gen_dataframe, Wind_Penetration = results.marketoptimization()
