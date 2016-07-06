# Python standard modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


resultsdf_plot1 = pd.read_excel('PremiumPlots.xlsx', 'plot1') 

# Results
WindProd = resultsdf_plot1['WindProd'].tolist()
NuclearProd = resultsdf_plot1['NuclearProd'].tolist()
CoalProd = resultsdf_plot1['CoalProd'].tolist()
GasProd = resultsdf_plot1['GasProd'].tolist()
HydroProd = resultsdf_plot1['HydroProd'].tolist()
OilProd = resultsdf_plot1['OilProd'].tolist()

Iteration = resultsdf_plot1['Iteration'].tolist()
Energycost = resultsdf_plot1['Energy'].tolist()
Premiumcost = resultsdf_plot1['Premium'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig, ax1 = plt.subplots()

width = 0.35  # the width of the bars: can also be len(x) sequence

ax2 = ax1.twinx()

ind = np.arange(len(Iteration))
p3 = ax1.bar(ind, WindProd, width, color='olive', label='$WindProd$')
p4 = ax1.bar(ind, NuclearProd, width, color='darkgreen',bottom=WindProd, label='$NuclearProd$')
new = [x + y for x, y in zip(WindProd, NuclearProd)]
p5 = ax1.bar(ind, CoalProd, width, color='midnightblue',bottom=new, label='$CoalProd$')
new = [x + y for x, y in zip(new, CoalProd)]
p6 = ax1.bar(ind, GasProd, width, color='blue',bottom=new, label='$GasProd$')
new = [x + y for x, y in zip(new, GasProd)]
p7 = ax1.bar(ind, HydroProd, width, color='silver',bottom=new, label='$HydroProd$')
new = [x + y for x, y in zip(new, HydroProd)]
p8 = ax1.bar(ind, OilProd, width, color='gray',bottom=new, label='$OilProd$')

ax1.grid(True, linestyle='-', which='major', color='lightgray', alpha=10000)
ax1.set_xlim([-1,5])
ax1.set_ylim([0,330])
ax1.set_ylabel('$Energy\ Production\ (GWh)$')
ax1.set_xlabel('$Iteration\ Number$')

newxlist = (ind + width/2).tolist()
Iteration = newxlist

ax2.plot(Iteration, Energycost, c='gray',alpha=1)
ax2.scatter(Iteration, Energycost, facecolor='gray', marker='o', edgecolor = 'gray', linewidth='1', s=80, alpha=1, label = '$Energy\ Cost$')
ax2.plot(Iteration, Premiumcost, c='darkgoldenrod',alpha=1)
ax2.scatter(Iteration, Premiumcost, facecolor='darkgoldenrod', marker='o', edgecolor = 'darkgoldenrod', linewidth='1', s=80, alpha=1, label = '$Premium\ Cost$')
ax2.set_xlim([-1,5])
ax2.set_ylim([-1,7])
ax2.set_ylabel('$Costs\ (M$€$/day)$')

plt.xticks(ind + width/2., ('0', '1', '2', '3', '4'))
ax1.legend(loc='upper center', bbox_to_anchor=(.35, 1.15), ncol=3, fancybox=True, shadow=True)
ax2.legend(loc='upper center', bbox_to_anchor=(.85, 1.15), ncol=1, fancybox=True, shadow=True)

ax1.set_axis_bgcolor('whitesmoke')

# plt.savefig('PremiumIterations.pdf')

plt.show()

resultsdf_plot1 = pd.read_excel('PremiumPlots.xlsx', 'plot2') 

# Results
InstallWind = resultsdf_plot1['installedcap'].tolist()
CostConv = resultsdf_plot1['costconv'].tolist()
Total = resultsdf_plot1['total'].tolist()
FixedCost = resultsdf_plot1['mmfixed'].tolist()
PremiumCost = resultsdf_plot1['premiumcost'].tolist()
WindPen = resultsdf_plot1['windpen'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()

ax1.plot(InstallWind , CostConv, sns.xkcd_rgb["windows blue"],alpha=1, label='$Cost\ of\ Energy\ incl.\ Wind$')
ax1.plot(InstallWind , Total, sns.xkcd_rgb["denim blue"],alpha=1, label='$Total\ Cost$')
ax1.plot(InstallWind , FixedCost, sns.xkcd_rgb["pale red"],alpha=1, label='$Missing\ Money$')
ax1.plot(InstallWind , PremiumCost, sns.xkcd_rgb["medium green"],alpha=1, label='$Cost\ of\ Premium$')

ax2.plot(InstallWind , WindPen, c='gray',alpha=0.5,linestyle='--')
ax2.scatter(InstallWind , WindPen, facecolor='gray', marker='o', edgecolor = 'gray', linewidth='1', s=50, alpha=1, label = '$Wind\ Penetration$')

ax1.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax1.set_xlim([0,3000])
ax1.set_ylim([0,2.5])
ax1.set_ylabel('$Costs\ (M$€$/day)$')
ax1.set_xlabel('$Installed\ Wind\ Capacity\ (MW)$')

ax2.set_ylim([0,60])
ax2.set_ylabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')

ax1.legend(loc='upper center', bbox_to_anchor=(.35, 1.15), ncol=2, fancybox=True, shadow=True)
ax2.legend(loc='upper center', bbox_to_anchor=(.85, 1.15), ncol=1, fancybox=True, shadow=True)

ax1.set_axis_bgcolor('whitesmoke')

# plt.savefig('WindvsPremiumNuclear.pdf')

plt.show()

resultsdf_plot1 = pd.read_excel('PremiumPlots.xlsx', 'plot3') 

# Results
InstallWind = resultsdf_plot1['installedcap'].tolist()
CostConv = resultsdf_plot1['costconv'].tolist()
Total = resultsdf_plot1['total'].tolist()
FixedCost = resultsdf_plot1['mmfixed'].tolist()
PremiumCost = resultsdf_plot1['premiumcost'].tolist()
WindPen = resultsdf_plot1['windpen'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()

ax1.plot(InstallWind , CostConv, sns.xkcd_rgb["windows blue"],alpha=1, label='$Cost\ of\ Energy\ incl.\ Wind$')
ax1.plot(InstallWind , Total, sns.xkcd_rgb["denim blue"],alpha=1, label='$Total\ Cost$')
ax1.plot(InstallWind , FixedCost, sns.xkcd_rgb["pale red"],alpha=1, label='$Missing\ Money$')
ax1.plot(InstallWind , PremiumCost, sns.xkcd_rgb["medium green"],alpha=1, label='$Cost\ of\ Premium$')

ax2.plot(InstallWind , WindPen, c='gray',alpha=0.5,linestyle='--')
ax2.scatter(InstallWind , WindPen, facecolor='gray', marker='o', edgecolor = 'gray', linewidth='1', s=50, alpha=1, label = '$Wind\ Penetration$')

ax1.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax1.set_xlim([0,3000])
ax1.set_ylim([0,2.5])
ax1.set_ylabel('$Costs\ (M$€$/day)$')
ax1.set_xlabel('$Installed\ Wind\ Capacity\ (MW)$')

ax2.set_ylim([0,60])
ax2.set_ylabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')

ax1.legend(loc='upper center', bbox_to_anchor=(.35, 1.15), ncol=2, fancybox=True, shadow=True)
ax2.legend(loc='upper center', bbox_to_anchor=(.85, 1.15), ncol=1, fancybox=True, shadow=True)

ax1.set_axis_bgcolor('whitesmoke')

# plt.savefig('WindvsPremiumCoal.pdf')

plt.show()

