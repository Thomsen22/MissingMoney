# Python standard modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import statsmodels.api as sm
import matplotlib.colors as mcolors
import matplotlib as mpl
from matplotlib.pylab import *
from mpl_toolkits.axes_grid1 import host_subplot

resultsdf_plot1 = pd.read_excel('PLR_plots.xlsx', 'plot1') 

# Results
WindLevel = resultsdf_plot1['wind_pen'].tolist()
Energycost = resultsdf_plot1['cost_energy'].tolist()
EnergycostWind = resultsdf_plot1['cost_wind'].tolist()
PLRcost = resultsdf_plot1['cost_plr'].tolist()
Fixedcost = resultsdf_plot1['mm_fixedcost'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(1)

width = 0.35

ind = np.arange(len(WindLevel))
p3 = plt.bar(ind, Energycost, width, color=sns.xkcd_rgb["windows blue"], label='$Cost\ of\ Energy$')
p2 = plt.bar(ind, EnergycostWind, width, color=sns.xkcd_rgb["medium green"],bottom=Energycost, label='$Cost\ of\ Wind$')
new = [x + y for x, y in zip(Energycost, EnergycostWind)]
p1 = plt.bar(ind, Fixedcost, width, color=sns.xkcd_rgb["amber"],bottom=new, label='$Variable\ and\ Fixed\ Cost\ Not\ Covered$')
new = [x + y for x, y in zip(new, Fixedcost)]
p4 = plt.bar(ind, PLRcost, width, color=sns.xkcd_rgb["pale red"],bottom=new, label='$Cost\ of\ PLR$')

plt.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
plt.axis([-1, 10, 0, 2.5])
plt.ylabel('$Cost\ (M$€$/day)$')
plt.xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')
plt.xticks(ind + width/2., ('0', '9.5', '19', '28', '38', '47', '56', '66','70','77'))
plt.yticks(np.arange(0, 3, 0.5))

plt.legend(loc='upper center', bbox_to_anchor=(.5, 1.15), ncol=2, fancybox=True, shadow=True)
axes = plt.gca()
axes.set_axis_bgcolor('whitesmoke')

# plt.savefig('SEpeakloadreserve.pdf')

plt.show()

resultsdf_plot6 = pd.read_excel('PLR_plots.xlsx', 'plot6') 

# Results
WindLevel = resultsdf_plot6['wind_pen'].tolist()
PLR20 = resultsdf_plot6['PLR20'].tolist()
PLR15 = resultsdf_plot6['PLR15'].tolist()
PLR10 = resultsdf_plot6['PLR10'].tolist()
PLR5 = resultsdf_plot6['PLR5'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(1)

plt.plot(WindLevel, PLR5, c=sns.xkcd_rgb["windows blue"],alpha=1, label = r"$5\;$%$\;PLR$")
plt.plot(WindLevel, PLR10, c=sns.xkcd_rgb["medium green"],alpha=1, label = r"$10\;$%$\;PLR$")
plt.plot(WindLevel, PLR15, c=sns.xkcd_rgb["amber"],alpha=1, label = r"$15\;$%$\;PLR$")
plt.plot(WindLevel, PLR20, c=sns.xkcd_rgb["pale red"],alpha=1, label = r"$20\;$%$\;PLR$")

plt.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
plt.axis([0.0, 77, 0, 35])
plt.ylabel('$Number\ of\ Activations$')
plt.xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')

plt.legend(loc='upper center', bbox_to_anchor=(.5, 1.10), ncol=4, fancybox=True, shadow=True)
axes = plt.gca()
axes.set_axis_bgcolor('whitesmoke')

# plt.savefig('peakloadreserveNOA.pdf')

plt.show()

resultsdf_plot2 = pd.read_excel('PLR_plots.xlsx', 'plot2') 
resultsdf_plot3 = pd.read_excel('PLR_plots.xlsx', 'plot3') 

WindLevel = resultsdf_plot2['wind_pen'].tolist()
Energycost5 = resultsdf_plot2['CostOfEnergy005'].tolist()
Energycost10 = resultsdf_plot2['CostOfEnergy010'].tolist()
Energycost15 = resultsdf_plot2['CostOfEnergy015'].tolist()
Energycost20 = resultsdf_plot2['CostOfEnergy020'].tolist()
MM5 = resultsdf_plot3['mm005'].tolist()
MM10 = resultsdf_plot3['mm010'].tolist()
MM15 = resultsdf_plot3['mm015'].tolist()
MM20 = resultsdf_plot3['mm020'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

f0 = figure(num = 0, figsize = (8, 12))#, dpi = 300)
f0.suptitle("$Peak\ Load\ Reserve\ Demand\ Increase$", fontsize=14)
ax01 = subplot2grid((2, 2), (0, 0))
ax02 = subplot2grid((2, 2), (0, 1))

ax01.set_ylim(0,4)
ax02.set_ylim(0,0.4)

ax01.set_xlim(0,77)
ax02.set_xlim(0,77)

ax01.grid(True)
ax02.grid(True)

ax01.set_xlabel("$Average\ Wind\ Penetration\ Level\ ($%$)$")
ax01.set_ylabel("$Total\ Cost\ (M$€$/day)$")
ax02.set_xlabel("$Average\ Wind\ Penetration\ Level\ ($%$)$")
ax02.set_ylabel("$Missing\ Money\ from\ Var.\ and\ Fixed\ Cost\ (M$€$/day)$")
ax02.yaxis.tick_right()

p011, = ax01.plot(WindLevel, Energycost5, c=sns.xkcd_rgb["windows blue"],alpha=1, label = "$5$%$\ PLR$")
p012, = ax01.plot(WindLevel, Energycost10, c=sns.xkcd_rgb["medium green"],alpha=1, label = "$10$%$\ PLR$")
p013, = ax01.plot(WindLevel, Energycost15, c=sns.xkcd_rgb["amber"],alpha=1, label = "$15$%$\ PLR$")
p014, = ax01.plot(WindLevel, Energycost20, c=sns.xkcd_rgb["pale red"],alpha=1, label = "$20$%$\ PLR$")

p021, = ax02.plot(WindLevel, MM5, c=sns.xkcd_rgb["windows blue"],alpha=1, label = "$5$%$\ PLR$")
p022, = ax02.plot(WindLevel, MM10, c=sns.xkcd_rgb["medium green"],alpha=1, label = "$10$%$\ PLR$")
p023, = ax02.plot(WindLevel, MM15, c=sns.xkcd_rgb["amber"],alpha=1, label = "$15$%$\ PLR$")
p024, = ax02.plot(WindLevel, MM20, c=sns.xkcd_rgb["pale red"],alpha=1, label = "$20$%$\ PLR$")

ax01.legend([p011,p012,p013,p014], [p011.get_label(),p012.get_label(),p013.get_label(),p014.get_label()])

legend = ax01.legend(loc='upper center', bbox_to_anchor=(1, 1.15),
          ncol=4, fancybox=True, shadow=True)

ax01.set_axis_bgcolor('whitesmoke')
ax02.set_axis_bgcolor('whitesmoke')

figure(0) 

# f0.savefig('PLRdemandincrease.pdf')

show()

resultsdf_plot7 = pd.read_excel('PLR_plots.xlsx', 'plot7') 
resultsdf_plot8 = pd.read_excel('PLR_plots.xlsx', 'plot8') 

WindLevel = resultsdf_plot7['wind_pen'].tolist()
MMHB = resultsdf_plot7['HighestBid'].tolist()
MM500 = resultsdf_plot7['AP500'].tolist()
MM1000 = resultsdf_plot7['AP1000'].tolist()

MMHB2 = resultsdf_plot8['wind_pen'].tolist()
MM150 = resultsdf_plot8['AP150'].tolist()
MM250 = resultsdf_plot8['AP250'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

f0 = figure(num = 0, figsize = (8, 12))
ax01 = subplot2grid((2, 2), (0, 0))
ax02 = subplot2grid((2, 2), (0, 1))

ax01.set_title(r'$PLR\ demand\ 15\ \%$', y=1.12)
ax02.set_title(r'$PLR\ demand\ 20\ \%$', y=1.12)

ax01.set_ylim(0,0.4)
ax02.set_ylim(0,0.3)

ax01.set_xlim(0,77)
ax02.set_xlim(0,77)

ax01.grid(True)
ax02.grid(True)

ax01.set_xlabel("$Average\ Wind\ Penetration\ Level\ ($%$)$")
ax01.set_ylabel("$Missing\ Money\ from\ Var.\ and\ Fixed\ Cost\ (M$€$/day)$")
ax02.set_xlabel("$Average\ Wind\ Penetration\ Level\ ($%$)$")
ax02.set_ylabel("$Missing\ Money\ from\ Var.\ and\ Fixed\ Cost\ (M$€$/day)$")

p011, = ax01.plot(WindLevel, MMHB, c=sns.xkcd_rgb["windows blue"],alpha=1, label = "$Highest\ Bid$")
p012, = ax01.plot(WindLevel, MM500, c=sns.xkcd_rgb["medium green"],alpha=1, label = "$500\ $€$/MWh$")
p013, = ax01.plot(WindLevel, MM1000, c=sns.xkcd_rgb["pale red"],alpha=1, label = "$1000\ $€$/MWh$")

p021, = ax02.plot(WindLevel, MMHB2, c=sns.xkcd_rgb["windows blue"],alpha=1, label = "$Highest\ Bid$")
p022, = ax02.plot(WindLevel, MM150, c=sns.xkcd_rgb["medium green"],alpha=1, label = "$150\ $€$/MWh$")
p023, = ax02.plot(WindLevel, MM250, c=sns.xkcd_rgb["pale red"],alpha=1, label = "$250\ $€$/MWh$")

ax02.yaxis.tick_right()
ax01.legend([p011,p012,p013], [p011.get_label(),p012.get_label(),p013.get_label()])
ax02.legend([p021,p022,p023], [p021.get_label(),p022.get_label(),p023.get_label()])

legend = ax01.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
          
legend = ax02.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)

ax01.set_axis_bgcolor('whitesmoke')
ax02.set_axis_bgcolor('whitesmoke')
         
figure(0)

# f0.savefig('PLRmissingmoney.pdf') 

show()

resultsdf_plot9 = pd.read_excel('PLR_plots.xlsx', 'plot9') 
resultsdf_plot10 = pd.read_excel('PLR_plots.xlsx', 'plot10') 

WindLevel = resultsdf_plot9['wind_pen'].tolist()
MMHB = resultsdf_plot9['HighestBid'].tolist()
MM500 = resultsdf_plot9['AP500'].tolist()
MM1000 = resultsdf_plot9['AP1000'].tolist()

MMHB2 = resultsdf_plot10['HighestBid'].tolist()
MM150 = resultsdf_plot10['AP150'].tolist()
MM250 = resultsdf_plot10['AP250'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

f0 = figure(num = 0, figsize = (8, 12))
ax01 = subplot2grid((2, 2), (0, 0))
ax02 = subplot2grid((2, 2), (0, 1))

ax01.set_title(r'$PLR\ demand\ 15\ \%$', y=1.12)
ax02.set_title(r'$PLR\ demand\ 20\ \%$', y=1.12)

ax01.set_ylim(0,9)
ax02.set_ylim(0,6.5)

ax01.set_xlim(0,77)
ax02.set_xlim(0,77)

ax01.grid(True)
ax02.grid(True)

ax01.set_xlabel("$Total\ Wind\ Penetration\ Level\ ($%$)$")
ax01.set_ylabel("$Total\ Cost\ (M$€$/day)$")
ax02.set_xlabel("$Average\ Wind\ Penetration\ Level\ ($%$)$")
ax02.set_ylabel("$Total\ Cost\ (M$€$/day)$")

p011, = ax01.plot(WindLevel, MMHB, c=sns.xkcd_rgb["windows blue"],alpha=1, label = "$Highest\ Bid$")
p012, = ax01.plot(WindLevel, MM500, c=sns.xkcd_rgb["medium green"],alpha=1, label = "$500\ $€$/MWh$")
p013, = ax01.plot(WindLevel, MM1000, c=sns.xkcd_rgb["pale red"],alpha=1, label = "$1000\ $€$/MWh$")

p021, = ax02.plot(WindLevel, MMHB2, c=sns.xkcd_rgb["windows blue"],alpha=1, label = "$Highest\ Bid$")
p022, = ax02.plot(WindLevel, MM150, c=sns.xkcd_rgb["medium green"],alpha=1, label = "$150\ $€$/MWh$")
p023, = ax02.plot(WindLevel, MM250, c=sns.xkcd_rgb["pale red"],alpha=1, label = "$250\ $€$/MWh$")

ax02.yaxis.tick_right()
ax01.legend([p011,p012,p013], [p011.get_label(),p012.get_label(),p013.get_label()])
ax02.legend([p021,p022,p023], [p021.get_label(),p022.get_label(),p023.get_label()])

legend = ax01.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
          
legend = ax02.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
         
ax01.set_axis_bgcolor('whitesmoke')
ax02.set_axis_bgcolor('whitesmoke')
         
figure(0)

# f0.savefig('PLRenergycost.pdf') 

show()

resultsdf_plot1 = pd.read_excel('PLR_plots.xlsx', 'plot11') 

WindLevel = resultsdf_plot1['wind_pen'].tolist()
Energycost = resultsdf_plot1['cost_energy'].tolist()
Fixedcost = resultsdf_plot1['relfixedcosts'].tolist()
EnergycostPLR = resultsdf_plot1['cost_energyplr'].tolist()
EnergycostWindPLR = resultsdf_plot1['cost_wind'].tolist()
FixedcostPLR = resultsdf_plot1['relfixedcosts_plr'].tolist()
PLRcost = resultsdf_plot1['cost_plr'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(1)

width = 0.35

ind = np.arange(len(WindLevel))
p3 = plt.bar(ind, EnergycostPLR, width, color=sns.xkcd_rgb["windows blue"], label='$Cost\ of\ Energy$')
p3 = plt.bar(ind, EnergycostWindPLR, width, color=sns.xkcd_rgb["medium green"], bottom=EnergycostPLR,label='$Cost\ of\ Wind$')
new = [x + y for x, y in zip(EnergycostPLR, EnergycostWindPLR)]
p5 = plt.bar(ind, FixedcostPLR, width, color=sns.xkcd_rgb["amber"],bottom=new, label='$Variable\ and\ Fixed\ Cost\ Not\ Covered$')
new = [x + y for x, y in zip(new, FixedcostPLR)]
p4 = plt.bar(ind, PLRcost, width, color=sns.xkcd_rgb["pale red"],bottom=new, label='$Cost\ of\ PLR$')

plt.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
plt.axis([-1, 6, 0, 450])
plt.ylabel('$Cost\ (M$€$/day)$')
plt.xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')
plt.xticks(ind + width/2., ('0', '19', '33', '43', '50', '55'))
plt.yticks(np.arange(0, 475, 50))

plt.legend(loc='upper center', bbox_to_anchor=(.5, 1.15), ncol=2, fancybox=True, shadow=True)

axes = plt.gca()
axes.set_axis_bgcolor('whitesmoke')

# plt.savefig('EUPLRBARPLOT.pdf')

plt.show()

resultsdf_plot1 = pd.read_excel('PLR_plots.xlsx', 'plot12') 

# Results
Iteration = resultsdf_plot1['Iterations'].tolist()

Nuclear = resultsdf_plot1['NuclearProd'].tolist()
Coal = resultsdf_plot1['CoalProd'].tolist()
Gas = resultsdf_plot1['GasProd'].tolist()
Hydro = resultsdf_plot1['HydroProd'].tolist()
Oil = resultsdf_plot1['OilProd'].tolist()
CapReq = resultsdf_plot1['CapRequirement'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig, ax1 = plt.subplots()

width = 0.35  # the width of the bars: can also be len(x) sequence

ind = np.arange(len(Iteration))
p3 = ax1.bar(ind, Nuclear, width, color='olive', label='$Nuclear$')
p4 = ax1.bar(ind, Coal, width, color='darkgreen',bottom=Nuclear, label='$Coal$')
new = [x + y for x, y in zip(Nuclear, Coal)]
p5 = ax1.bar(ind, Hydro, width, color='midnightblue',bottom=new, label='$Hydro$')
new = [x + y for x, y in zip(new, Hydro)]
p6 = ax1.bar(ind, Gas, width, color='blue',bottom=new, label='$Gas$')
new = [x + y for x, y in zip(new, Gas)]
p7 = ax1.bar(ind, Oil, width, color='silver',bottom=new, label='$Oil$')

newxlist = (ind + width/2).tolist()
Iteration = newxlist
ax1.plot(Iteration, CapReq, linestyle='--', c='darkred',alpha=1, label = '$Cap.\ Req.$')

ax1.grid(True, linestyle='-', which='major', color='lightgray', alpha=10000)
ax1.set_xlim([-1,5])
ax1.set_ylim([0,4500])
ax1.set_ylabel('$Installed\ Capacity\ (MW)$')
ax1.set_xlabel('$Iteration\ Number$')

plt.xticks(ind + width/2., ('0', '1', '2', '3', '4'))
ax1.legend(loc='upper center', bbox_to_anchor=(.5, 1.1), ncol=6, fancybox=True, shadow=True)

ax1.set_axis_bgcolor('whitesmoke')

# plt.savefig('PLR24busIteration.pdf')

plt.show()