# Python standard modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Plot of capacity market simulations
resultsdf_plot1 = pd.read_excel('CMplots.xlsx', 'plot1') 

# Results
WindLevel = resultsdf_plot1['wind_pen'].tolist()
Energycost = resultsdf_plot1['cost_energy'].tolist()
Windcost = resultsdf_plot1['cost_energy_wind'].tolist()
Capcost = resultsdf_plot1['capmarket_cost'].tolist()
Fixedcost = resultsdf_plot1['mm_varfixed'].tolist()
Totalcost = resultsdf_plot1['total_cost'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(1)

plt.plot(WindLevel, Totalcost, sns.xkcd_rgb["deep purple"],alpha=1, label = r"$Total\; Cost$")
plt.plot(WindLevel, Energycost, sns.xkcd_rgb["denim blue"],alpha=1, label = r"$Cost\; of\; Energy$")
plt.plot(WindLevel, Windcost, sns.xkcd_rgb["amber"],alpha=1, label = r"$Cost\; of\; Energy\; incl.\; Wind$")
plt.plot(WindLevel, Capcost, sns.xkcd_rgb["pale red"],alpha=1, label = r"$Capacity\; Payments$")
plt.plot(WindLevel, Fixedcost, sns.xkcd_rgb["medium green"],alpha=1, label = r"$Missing\; Money$")


plt.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
plt.axis([0, 77, 0, 2.5])
plt.ylabel('$Cost\ (M$€$/day)$')
plt.xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')

plt.legend(loc='upper center', bbox_to_anchor=(.5, 1.15), ncol=3, fancybox=True, shadow=True)

axes = plt.gca()
axes.set_axis_bgcolor('whitesmoke')

# plt.savefig('capmarket_simulaton.pdf')
        
plt.show()

# Capacity market simulations including a CO2 price

resultsdf_plot1 = pd.read_excel('Cmplots.xlsx', 'plot2')

# Base
WindLevel = resultsdf_plot1['wind_pen'].tolist()
Energycost = resultsdf_plot1['cost_energy'].tolist()
Capcost = resultsdf_plot1['cost_capmarket'].tolist()
total = resultsdf_plot1['cost_total'].tolist()

# CO2, + nuke
Energycostnuke = resultsdf_plot1['cost_energy_co2'].tolist()
Capcostnuke = resultsdf_plot1['cost_capmarket_co2'].tolist()
totalnuke = resultsdf_plot1['cost_total_co2'].tolist()

# CO2, - nuke
Energycostnonuke = resultsdf_plot1['cost_energy_co2_nonuclear'].tolist()
Capcostnonuke = resultsdf_plot1['cost_capmarket_co2_nonuclear'].tolist()
totalnonuke = resultsdf_plot1['cost_total_co2_nonuclear'].tolist()

Energycostnukechange = resultsdf_plot1['cost_energy_co2_nuclearchange'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(1)

plt.plot(WindLevel, Energycost, sns.xkcd_rgb["windows blue"],alpha=1, label = "$Cost$ $of$ $Energy$ $(base)$")
plt.plot(WindLevel, Capcost, sns.xkcd_rgb["pale red"],alpha=1, label = "$Capacity$ $Payments$ $(base)$")
plt.plot(WindLevel, Energycostnuke, sns.xkcd_rgb["medium green"],alpha=1, linestyle='--')
plt.plot(WindLevel, Capcostnuke, sns.xkcd_rgb["amber"],alpha=1, linestyle='--') 
plt.plot(WindLevel, Energycostnonuke, sns.xkcd_rgb["medium green"],alpha=1, label = "$Cost$ $of$ $Energy$ $(CO2$ $price)$")
plt.plot(WindLevel, Capcostnonuke, sns.xkcd_rgb["amber"],alpha=1, label = "$Capacity$ $Payments$ $(CO2$ $price)$")

plt.plot(WindLevel, Energycostnukechange, sns.xkcd_rgb["medium green"],alpha=1, linestyle='--') 

plt.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
plt.axis([0, 77, 0, 3])
plt.ylabel('$Cost\ (M$€$/day)$')
plt.xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')

axes = plt.gca()
axes.set_axis_bgcolor('whitesmoke')

plt.legend(loc='upper center', bbox_to_anchor=(.5, 1.15), ncol=2, fancybox=True, shadow=True)

#plt.savefig('CO2capmarket.pdf')

plt.show()

resultsdf_plot1 = pd.read_excel('CMplots.xlsx', 'plot3')

# Results
WindLevel = resultsdf_plot1['wind_pen'].tolist()
SolarLevel = resultsdf_plot1['solar_pen'].tolist()
CMcost = resultsdf_plot1['cost_capacity'].tolist()
Energycost = resultsdf_plot1['cost_energy'].tolist()
RenPen = resultsdf_plot1['ren_pen'].tolist()

resultsdf_plot2 = pd.read_excel('CMplots.xlsx', 'plot4')

# Results
WindLevel2 = resultsdf_plot2['wind_pen'].tolist()
SolarLevel2 = resultsdf_plot2['solar_pen'].tolist()
CMcost2 = resultsdf_plot2['cost_capacity'].tolist()
Energycost2 = resultsdf_plot2['cost_energy'].tolist()
RenPen2 = resultsdf_plot2['ren_pen'].tolist()

resultsdf_plot3 = pd.read_excel('Cmplots.xlsx', 'plot5')

# Results
CMcostnew1 = resultsdf_plot3['CM1'].tolist()
Ecost1 = resultsdf_plot3['E1'].tolist()
CMcostnew2 = resultsdf_plot3['CM2'].tolist()
Ecost2 = resultsdf_plot3['E2'].tolist()

cmap=plt.cm.viridis
cmap.set_under(cmap(int(0)))
Colorscale_array = np.asarray(RenPen2)

sns.set_color_codes("dark")
sns.set_style('ticks')

fig, ax1 = plt.subplots()

ax1.plot(CMcostnew1, Ecost1,c='gray',alpha=0.5,linestyle='-')

cax = ax1.scatter(CMcost, Energycost, c=Colorscale_array, marker='o', s=100, alpha=1, cmap=cmap, vmin=0, vmax=Colorscale_array.max())
cax = ax1.scatter(CMcost2, Energycost2, c=Colorscale_array, marker='*', s=100, alpha=1, cmap=cmap, vmin=0, vmax=Colorscale_array.max())

ax1.set_axis_bgcolor('whitesmoke')
ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax1.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
        
ax1.set_xlabel('$Capacity\ Payments\ (M$€$/day)$')
ax1.set_ylabel('$Energy\ Payments\ (M$€$/day)$')

cbar = fig.colorbar(cax, extend='min')
cbar.set_label('$Renewable\ Penetration\ (\%)$', rotation=270, labelpad=20)

# plt.savefig('CapMarketWindSolarTotal.pdf')

plt.show()

resultsdf_plot1 = pd.read_excel('Cmplots.xlsx', 'plot6')

# Results
WindLevel = resultsdf_plot1['wind_pen'].tolist()
SolarLevel = resultsdf_plot1['solar_pen'].tolist()
Cost = resultsdf_plot1['cost_total'].tolist()

resultsdf_plot2 = pd.read_excel('Cmplots.xlsx', 'plot7')

# Results
WindLevel2 = resultsdf_plot2['wind_pen'].tolist()
SolarLevel2 = resultsdf_plot2['solar_pen'].tolist()
Cost2 = resultsdf_plot2['cost_total'].tolist()

resultsdf_plot3 = pd.read_excel('Cmplots.xlsx', 'plot5')

# Results
CMcost1 = resultsdf_plot3['CM1'].tolist()
Ecost1 = resultsdf_plot3['E1'].tolist()
CMcost2 = resultsdf_plot3['CM2'].tolist()
Ecost2 = resultsdf_plot3['E2'].tolist()

cmap=plt.cm.viridis
cmap.set_under(cmap(int(0)))
Colorscale_array = np.asarray(Cost2)

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(4)
ax = fig.add_subplot(111)

# Winter plot
# cax = ax.scatter(WindLevel, SolarLevel, c=Colorscale_array, marker='o', s=100, alpha=1, cmap=cmap, vmin=0, vmax=Colorscale_array.max())

# Summer plot
cax = ax.scatter(WindLevel2, SolarLevel2, c=Colorscale_array, marker='*', s=100, alpha=1, cmap=cmap, vmin=0, vmax=Colorscale_array.max())

ax.set_axis_bgcolor('whitesmoke')
ax.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
        
ax.set_xlabel('$Wind\ Penetration\ Level\ (\%)$')
ax.set_ylabel('$Solar\ Penetration\ Level\ (\%)$')

cbar = fig.colorbar(cax, extend='min')
cbar.set_label('$Total\ Cost\ (M$€$/day)$', rotation=270, labelpad=20)

#plt.savefig('CapMarketWindSolarSummer.pdf')
#plt.savefig('CapMarketWindSolarWinter.pdf')

plt.show()

# Capacity market plot European system

resultsdf_plot1 = pd.read_excel('Cmplots.xlsx', 'plot8') 

# Results
WindLevel = resultsdf_plot1['wind_pen'].tolist()
Energycost = resultsdf_plot1['cost_energy'].tolist()
Windcost = resultsdf_plot1['cost_wind'].tolist()
Capcost = resultsdf_plot1['cost_capacity'].tolist()
Fixedcost = resultsdf_plot1['mm_varfixed'].tolist()
Totalcost = resultsdf_plot1['cost_total'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(1)

plt.plot(WindLevel, Totalcost, sns.xkcd_rgb["deep purple"],alpha=1, label = r"$Total\; Cost$")
plt.plot(WindLevel, Energycost, sns.xkcd_rgb["windows blue"],alpha=1, label = r"$Cost\; of\; Energy$")
plt.plot(WindLevel, Windcost, sns.xkcd_rgb["amber"],alpha=1, label = r"$Cost\; of\; Energy\; incl.\; Wind$")
plt.plot(WindLevel, Capcost, sns.xkcd_rgb["pale red"],alpha=1, label = r"$Capacity\; Payments$")
plt.plot(WindLevel, Fixedcost, sns.xkcd_rgb["medium green"],alpha=1, label = r"$Missing\; Money$")

plt.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
plt.axis([0, 55, 0, 500])
plt.ylabel('$Cost\ (M$€$/day)$')
plt.xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')

plt.legend(loc='upper center', bbox_to_anchor=(.5, 1.15), ncol=3, fancybox=True, shadow=True)

axes = plt.gca()

axes.set_axis_bgcolor('whitesmoke')

# plt.savefig('CapMarketEUWind.pdf')  
     
plt.show()

resultsdf_plot1 = pd.read_excel('Cmplots.xlsx', 'plot9') 

# Results
Iteration = resultsdf_plot1['Iterations'].tolist()
Energycost = resultsdf_plot1['Energy'].tolist()
Capcost = resultsdf_plot1['Cap'].tolist()
Capcostzonal = resultsdf_plot1['CapZonal'].tolist()

Nuclear = resultsdf_plot1['NuclearProd'].tolist()
Coal = resultsdf_plot1['CoalProd'].tolist()
Gas = resultsdf_plot1['GasProd'].tolist()
Hydro = resultsdf_plot1['HydroProd'].tolist()
Oil = resultsdf_plot1['OilProd'].tolist()
Unknown = resultsdf_plot1['TotalUnknown'].tolist()
Geothermal = resultsdf_plot1['GeothermalProd'].tolist()
Waste = resultsdf_plot1['WasteProd'].tolist()
CapReq = resultsdf_plot1['CapRequirement'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig, ax1 = plt.subplots()

width = 0.35  # the width of the bars: can also be len(x) sequence

ax2 = ax1.twinx()

ind = np.arange(len(Iteration))
p3 = ax1.bar(ind, Nuclear, width, color='olive', label='$Nuclear$')
p4 = ax1.bar(ind, Coal, width, color='darkgreen',bottom=Nuclear, label='$Coal$')
new = [x + y for x, y in zip(Nuclear, Coal)]
p5 = ax1.bar(ind, Gas, width, color='midnightblue',bottom=new, label='$Gas$')
new = [x + y for x, y in zip(new, Gas)]
p6 = ax1.bar(ind, Hydro, width, color='blue',bottom=new, label='$Hydro$')
new = [x + y for x, y in zip(new, Hydro)]
p7 = ax1.bar(ind, Oil, width, color='silver',bottom=new, label='$Oil$')
new = [x + y for x, y in zip(new, Oil)]
p8 = ax1.bar(ind, Unknown, width, color='gray',bottom=new, label='$Unknown$')

newxlist = (ind + width/2).tolist()
Iteration = newxlist
ax1.plot(Iteration, CapReq, linestyle='--', c='darkred',alpha=1, label = '$Cap.\ Req.$')

ax1.grid(True, linestyle='-', which='major', color='lightgray', alpha=10000)
ax1.set_xlim([-1,5])
ax1.set_ylim([0,550])
ax1.set_ylabel('$Installed\ Capacity\ (GW)$')
ax1.set_xlabel('$Iteration\ Number$')

newxlist = (ind + width/2).tolist()
Iteration = newxlist

ax2.plot(Iteration, Energycost, c='gray',alpha=1)
ax2.scatter(Iteration, Energycost, facecolor='gray', marker='o', edgecolor = 'gray', linewidth='1', s=80, alpha=1, label = '$Cost\ of\ Energy$')
ax2.plot(Iteration, Capcost, c='darkgoldenrod',alpha=1)
ax2.scatter(Iteration, Capcost, facecolor='darkgoldenrod', marker='o', edgecolor = 'darkgoldenrod', linewidth='1', s=80, alpha=1, label = '$Capacity\ Payments$')
ax2.set_xlim([-1,5])
ax2.set_ylim([0,250])
ax2.set_ylabel('$Costs\ (M$€$/day)$')

plt.xticks(ind + width/2., ('0', '1', '2', '3', '4'))
ax1.legend(loc='upper center', bbox_to_anchor=(.35, 1.15), ncol=4, fancybox=True, shadow=True)
ax2.legend(loc='upper center', bbox_to_anchor=(.85, 1.15), ncol=1, fancybox=True, shadow=True)

ax1.set_axis_bgcolor('whitesmoke')

# plt.savefig('CapMarketEUIteration.pdf')

plt.show()

resultsdf_plot1 = pd.read_excel('Cmplots.xlsx', 'plot10') 

# Results
WindLevel = resultsdf_plot1['wind_pen'].tolist()
g15b = resultsdf_plot1['g15bD'].tolist()
g21 = resultsdf_plot1['g21D'].tolist()
g22 = resultsdf_plot1['g22D'].tolist()
g16 = resultsdf_plot1['g16D'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(1)
ax = fig.add_subplot(111)

ax.scatter(WindLevel, g15b, facecolor=sns.xkcd_rgb["windows blue"], marker='o', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$Coal$')
ax.scatter(WindLevel, g21, facecolor=sns.xkcd_rgb["medium green"], marker='v', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$Nuclear$')
ax.scatter(WindLevel, g22, facecolor=sns.xkcd_rgb["amber"], marker='s', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$Hydro$')
ax.scatter(WindLevel, g16, facecolor=sns.xkcd_rgb["pale red"], marker='p', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$CCGT$')

ax.plot(WindLevel, g15b, '--', c='grey', linewidth=0.5)
ax.plot(WindLevel, g21, '--', c='grey', linewidth=0.5)
ax.plot(WindLevel, g22, '--', c='grey', linewidth=0.5)
ax.plot(WindLevel, g16, '--', c='grey', linewidth=0.5)

ax.set_xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')
ax.set_ylabel('$Capacity\ Market\ Bid\ ($€$/MW-day)$')
ax.set_axis_bgcolor('whitesmoke')

ax.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)

legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.10),
          ncol=4, fancybox=True, shadow=True)
          
# plt.savefig('CapMarketClearingPrices.pdf')

plt.show()



resultsdf_plot1 = pd.read_excel('Cmplots.xlsx', 'plot11') 

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

width = 0.35  

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
ax1.set_ylim([0,3000])
ax1.set_ylabel('$Installed\ Capacity\ (MW)$')
ax1.set_xlabel('$Iteration\ Number$')

plt.xticks(ind + width/2., ('0', '1', '2', '3', '4'))
ax1.legend(loc='upper center', bbox_to_anchor=(.5, 1.1), ncol=6, fancybox=True, shadow=True)

ax1.set_axis_bgcolor('whitesmoke')

# plt.savefig('CapMarket24busIteration.pdf')

plt.show()



