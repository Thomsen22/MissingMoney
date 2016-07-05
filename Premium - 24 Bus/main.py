import premium_function as pf

timeperiod = 'Weak'
bidtype = 'Fixed'
newpremium = 'yes'
reservemargin = 1.15

gen_dataframe, df_generators, totalwindcost, totalsolarcost, wind_penetration, solar_penetration = pf.premiumfunction(timeperiod, bidtype, newpremium, reservemargin)



