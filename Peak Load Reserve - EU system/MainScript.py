# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 14:13:34 2016

@author: Søren
"""

# Main script: 

# Should be run in order to undertake the optimization

# Python standard modules

#%% Peak Load Reserve Optimization

import PLR_function as PLRfunc

Gen_dataframe, df_price_DA, df_windprod, df_solarprod = PLRfunc.peakloadreserveoptimization()

#df_capacityreq.to_csv('1capacityrequirement.csv')
#df_price.to_csv('1capmarketprices.csv')
df_price_DA.to_csv('1dayaheadmarketprices.csv')
df_solarprod.to_csv('1solarproduction.csv')
df_windprod.to_csv('1windproduction.csv')
#df_zonalconsumption.to_csv('1consumptionprofile.csv')



