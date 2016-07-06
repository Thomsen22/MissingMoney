# Python standard modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Plot of wind pen. level vs. revenue and vs. cap. factor

# Read data from Excel spreadsheet
resultsdf_coal = pd.read_excel('EOMplots.xlsx', 'g15b').set_index('WindLevel') #coal
resultsdf_nuclear = pd.read_excel('EOMplots.xlsx', 'g21').set_index('WindLevel') #nuclear
resultsdf_hydro = pd.read_excel('EOMplots.xlsx', 'g22').set_index('WindLevel') #hydro
resultsdf_gas = pd.read_excel('EOMplots.xlsx', 'g16').set_index('WindLevel') #CCGT
resultsdf_gasSCGT = pd.read_excel('EOMplots.xlsx', 'g23b').set_index('WindLevel') #SCGT
resultsdf_oil = pd.read_excel('EOMplots.xlsx', 'g13').set_index('WindLevel') #oil

# Coal color dataframe
color = {}
for w in resultsdf_coal.index:
    if resultsdf_coal.Revenue[w] > resultsdf_coal.CapCost[w]:
        color[w] = sns.xkcd_rgb["windows blue"]
    elif resultsdf_coal.Revenue[w] < resultsdf_coal.CapCost[w] and resultsdf_coal.Revenue[w] > resultsdf_coal.FixedCostSUCost[w]:
        color[w] = sns.xkcd_rgb["medium green"]
    elif resultsdf_coal.Revenue[w] < resultsdf_coal.FixedCostSUCost[w] and resultsdf_coal.Revenue[w] > resultsdf_coal.VarCost[w]:
        color[w] = sns.xkcd_rgb["amber"]
    elif resultsdf_coal.Revenue[w] <= resultsdf_coal.VarCost[w]:
        color[w] = sns.xkcd_rgb["pale red"]

color_df = pd.DataFrame([[key,value] for key,value in color.items()],columns=['WindLevel','Color']).set_index('WindLevel')

results_df_coal = pd.merge(resultsdf_coal, color_df, right_index = True, left_index = True).reset_index()

results_df_coal.sort_values(['WindLevel'], ascending=[True], inplace=True)

# Nuclear color dataframe
color = {}
for w in resultsdf_nuclear.index:
    if resultsdf_nuclear.Revenue[w] > resultsdf_nuclear.CapCost[w]:
        color[w] = sns.xkcd_rgb["windows blue"]
    elif resultsdf_nuclear.Revenue[w] < resultsdf_nuclear.CapCost[w] and resultsdf_nuclear.Revenue[w] > resultsdf_nuclear.FixedCostSUCost[w]:
        color[w] = sns.xkcd_rgb["medium green"]
    elif resultsdf_nuclear.Revenue[w] < resultsdf_nuclear.FixedCostSUCost[w] and resultsdf_nuclear.Revenue[w] > resultsdf_nuclear.VarCost[w]:
        color[w] = sns.xkcd_rgb["amber"]
    elif resultsdf_nuclear.Revenue[w] <= resultsdf_nuclear.VarCost[w]:
        color[w] = sns.xkcd_rgb["pale red"]

color_df = pd.DataFrame([[key,value] for key,value in color.items()],columns=['WindLevel','Color']).set_index('WindLevel')

results_df_nuclear = pd.merge(resultsdf_nuclear, color_df, right_index = True, left_index = True).reset_index()

results_df_nuclear.sort_values(['WindLevel'], ascending=[True], inplace=True)

# Hydro color dataframe
color = {}
for w in resultsdf_hydro.index:
    if resultsdf_hydro.Revenue[w] > resultsdf_hydro.CapCost[w]:
        color[w] = sns.xkcd_rgb["windows blue"]
    elif resultsdf_hydro.Revenue[w] < resultsdf_hydro.CapCost[w] and resultsdf_hydro.Revenue[w] > resultsdf_hydro.FixedCostSUCost[w]:
        color[w] = sns.xkcd_rgb["medium green"]
    elif resultsdf_hydro.Revenue[w] < resultsdf_hydro.FixedCostSUCost[w] and resultsdf_hydro.Revenue[w] > resultsdf_hydro.VarCost[w]:
        color[w] = sns.xkcd_rgb["amber"]
    elif resultsdf_hydro.Revenue[w] <= resultsdf_hydro.VarCost[w]:
        color[w] = sns.xkcd_rgb["pale red"]

color_df = pd.DataFrame([[key,value] for key,value in color.items()],columns=['WindLevel','Color']).set_index('WindLevel')

results_df_hydro = pd.merge(resultsdf_hydro, color_df, right_index = True, left_index = True).reset_index()

results_df_hydro.sort_values(['WindLevel'], ascending=[True], inplace=True)

# Gas color dataframe (CCGT)
color = {}
for w in resultsdf_gas.index:
    if resultsdf_gas.Revenue[w] > resultsdf_gas.CapCost[w]:
        color[w] = sns.xkcd_rgb["windows blue"]
    elif resultsdf_gas.Revenue[w] < resultsdf_gas.CapCost[w] and resultsdf_gas.Revenue[w] > resultsdf_gas.FixedCostSUCost[w]:
        color[w] = sns.xkcd_rgb["medium green"]
    elif resultsdf_gas.Revenue[w] < resultsdf_gas.FixedCostSUCost[w] and resultsdf_gas.Revenue[w] > resultsdf_gas.VarCost[w]:
        color[w] = sns.xkcd_rgb["amber"]
    elif resultsdf_gas.Revenue[w] <= resultsdf_gas.VarCost[w]:
        color[w] = sns.xkcd_rgb["pale red"]

color_df = pd.DataFrame([[key,value] for key,value in color.items()],columns=['WindLevel','Color']).set_index('WindLevel')

results_df_gas = pd.merge(resultsdf_gas, color_df, right_index = True, left_index = True).reset_index()

results_df_gas.sort_values(['WindLevel'], ascending=[True], inplace=True)

# Gas color dataframe (SCGT)
color = {}
for w in resultsdf_gasSCGT.index:
    if resultsdf_gasSCGT.Revenue[w] > resultsdf_gasSCGT.CapCost[w]:
        color[w] = sns.xkcd_rgb["windows blue"]
    elif resultsdf_gasSCGT.Revenue[w] < resultsdf_gasSCGT.CapCost[w] and resultsdf_gasSCGT.Revenue[w] > resultsdf_gasSCGT.FixedCostSUCost[w]:
        color[w] = sns.xkcd_rgb["medium green"]
    elif resultsdf_gasSCGT.Revenue[w] < resultsdf_gasSCGT.FixedCostSUCost[w] and resultsdf_gasSCGT.Revenue[w] > resultsdf_gasSCGT.VarCost[w]:
        color[w] = sns.xkcd_rgb["amber"]
    elif resultsdf_gasSCGT.Revenue[w] <= resultsdf_gasSCGT.VarCost[w]:
        color[w] = sns.xkcd_rgb["pale red"]

color_df = pd.DataFrame([[key,value] for key,value in color.items()],columns=['WindLevel','Color']).set_index('WindLevel')

results_df_gasSCGT = pd.merge(resultsdf_gasSCGT, color_df, right_index = True, left_index = True).reset_index()

results_df_gasSCGT.sort_values(['WindLevel'], ascending=[True], inplace=True)

# Oil color dataframe
color = {}
for w in resultsdf_oil.index:
    if resultsdf_oil.Revenue[w] > resultsdf_oil.CapCost[w]:
        color[w] = sns.xkcd_rgb["windows blue"]
    elif resultsdf_oil.Revenue[w] < resultsdf_oil.CapCost[w] and resultsdf_oil.Revenue[w] > resultsdf_oil.FixedCostSUCost[w]:
        color[w] = sns.xkcd_rgb["medium green"]
    elif resultsdf_oil.Revenue[w] < resultsdf_oil.FixedCostSUCost[w] and resultsdf_oil.Revenue[w] > resultsdf_oil.VarCost[w]:
        color[w] = sns.xkcd_rgb["amber"]
    elif resultsdf_oil.Revenue[w] <= resultsdf_oil.VarCost[w]:
        color[w] = sns.xkcd_rgb["pale red"]

color_df = pd.DataFrame([[key,value] for key,value in color.items()],columns=['WindLevel','Color']).set_index('WindLevel')

results_df_oil = pd.merge(resultsdf_oil, color_df, right_index = True, left_index = True).reset_index()

results_df_oil.sort_values(['WindLevel'], ascending=[True], inplace=True)

# Coal
ys_coal = results_df_coal['CapFactor'].tolist()
xs_coal = results_df_coal['Revenue'].tolist()
zs_coal = results_df_coal['WindLevel'].tolist()
c_coal = results_df_coal['Color'].tolist()
# Nuclear
ys_nuclear = results_df_nuclear['CapFactor'].tolist()
xs_nuclear = results_df_nuclear['Revenue'].tolist()
zs_nuclear = results_df_nuclear['WindLevel'].tolist()
c_nuclear = results_df_nuclear['Color'].tolist()
# Hydro
ys_hydro = results_df_hydro['CapFactor'].tolist()
xs_hydro = results_df_hydro['Revenue'].tolist()
zs_hydro = results_df_hydro['WindLevel'].tolist()
c_hydro = results_df_hydro['Color'].tolist()
# Gas CCGT
ys_gas = results_df_gas['CapFactor'].tolist()
xs_gas = results_df_gas['Revenue'].tolist()
zs_gas = results_df_gas['WindLevel'].tolist()
c_gas = results_df_gas['Color'].tolist()
# Gas GCT
ys_gas_SCGT = results_df_gasSCGT['CapFactor'].tolist()
xs_gas_SCGT = results_df_gasSCGT['Revenue'].tolist()
zs_gas_SCGT = results_df_gasSCGT['WindLevel'].tolist()
c_gas_SCGT = results_df_gasSCGT['Color'].tolist()
# Oil
ys_oil = results_df_oil['CapFactor'].tolist()
xs_oil = results_df_oil['Revenue'].tolist()
zs_oil = results_df_oil['WindLevel'].tolist()
c_oil = results_df_oil['Color'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

# Revenue vs. windpenetration level
fig = plt.figure(1)
ax = fig.add_subplot(111)

ax.scatter(zs_coal, xs_coal, facecolor=c_coal, marker='o', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$Coal$')
ax.scatter(zs_nuclear, xs_nuclear, facecolor=c_nuclear, marker='v', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$Nuclear$')
ax.scatter(zs_hydro, xs_hydro, facecolor=c_hydro, marker='s', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$Hydro$')
ax.scatter(zs_gas, xs_gas, facecolor=c_gas, marker='p', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$CCGT$')
ax.scatter(zs_gas_SCGT, xs_gas_SCGT, facecolor=c_gas_SCGT, marker='*', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$SCGT$')
ax.scatter(zs_oil, xs_oil, facecolor=c_oil, marker='h', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$Oil$')

ax.plot(zs_coal, xs_coal, '--', c='grey', linewidth=0.5)
ax.plot(zs_nuclear, xs_nuclear, '--', c='grey', linewidth=0.5)
ax.plot(zs_hydro, xs_hydro, '--', c='grey', linewidth=0.5)
ax.plot(zs_gas, xs_gas, '--', c='grey', linewidth=0.5)
ax.plot(zs_gas_SCGT, xs_gas_SCGT, '--', c='grey', linewidth=0.5)
ax.plot(zs_oil, xs_oil, '--', c='grey', linewidth=0.5)

ax.set_xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')
ax.set_ylabel('$Revenue\ ($€$/MW-day)$')
ax.set_axis_bgcolor('whitesmoke')

ax.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)

legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=3, fancybox=True, shadow=True)
          
legend.legendHandles[0].set_color('grey')
legend.legendHandles[1].set_color('grey')
legend.legendHandles[2].set_color('grey')
legend.legendHandles[3].set_color('grey')
legend.legendHandles[4].set_color('grey')
legend.legendHandles[5].set_color('grey')

txt = ('$Red:\ Revenue\ <\ Variable\ Costs$\n$Yellow:\ Variable\ Costs\ <\ Revenue\ <\ Fixed\ Costs$\n$Green:\ Fixed\ Costs\ <\ Revenue\ <\ Capital\ Costs$\n$Blue:\ Revenue\ >\ All\ Costs$')
fig.text(.1,-.15,txt)

#plt.savefig('revenuevswind.pdf')

plt.show()

# Capacity factor vs. wind penetration level
fig = plt.figure(2)
ax = fig.add_subplot(111)

ax.scatter(zs_coal, ys_coal, marker='o', edgecolor = 'k', linewidth='1', facecolor='grey', s=80, alpha=1, label = '$Coal$')
ax.scatter(zs_nuclear, ys_nuclear, marker='v', edgecolor = 'k', linewidth='1', facecolor='grey', s=80, alpha=1, label = '$Nuclear$')
ax.scatter(zs_hydro, ys_hydro, marker='s', edgecolor = 'k', linewidth='1', facecolor='grey',s=80, alpha=1, label = '$Hydro$')
ax.scatter(zs_gas, ys_gas, marker='p', edgecolor = 'k', linewidth='1', facecolor='grey', s=80, alpha=1, label = '$CCGT$')
ax.scatter(zs_gas_SCGT, ys_gas_SCGT, marker='*', edgecolor = 'k', linewidth='1', facecolor='grey', s=80, alpha=1, label = '$SCGT$')
ax.scatter(zs_oil, ys_oil, marker='h', edgecolor = 'k', linewidth='1', facecolor='grey', s=80, alpha=1, label = '$Oil$')

ax.plot(zs_coal, ys_coal, '--', c='grey', linewidth=0.5)
ax.plot(zs_nuclear, ys_nuclear, '--', c='grey', linewidth=0.5)
ax.plot(zs_hydro, ys_hydro, '--', c='grey', linewidth=0.5)
ax.plot(zs_gas, ys_gas, '--', c='grey', linewidth=0.5)
ax.plot(zs_gas_SCGT, ys_gas_SCGT, '--', c='grey', linewidth=0.5)
ax.plot(zs_oil, ys_oil, '--', c='grey', linewidth=0.5)

ax.set_xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')
ax.set_ylabel('$Capacity\ Factor$')
ax.set_axis_bgcolor('whitesmoke')

ax.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)

legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=3, fancybox=True, shadow=True)

#plt.savefig('capfactorvswind.pdf')

plt.show()

#%% Plot of total system costs (needed support)
resultsdf_systemcosts = pd.read_excel('EOMplots.xlsx', 'systemcostsED')

# Results
WindLevel = resultsdf_systemcosts['WindLevel'].tolist()
relvarcosts = resultsdf_systemcosts['relvarcosts'].tolist()
relfixedcosts = resultsdf_systemcosts['relfixedcosts'].tolist()
relcapcosts = resultsdf_systemcosts['relcapcosts'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(3)
f, (ax3, ax2, ax) = plt.subplots(3, 1, sharex=True)

ax.plot(WindLevel, relvarcosts, c=sns.xkcd_rgb["windows blue"],alpha=1, label = '$Variable\ Costs$')
ax2.plot(WindLevel, relfixedcosts, c=sns.xkcd_rgb["medium green"],alpha=1, label = '$+\ Fixed\ Costs$')
ax3.plot(WindLevel, relcapcosts, c=sns.xkcd_rgb["pale red"],alpha=1, label = '$+\ Capital\ Costs$')

ax.set_ylim(0, 0.01)
ax2.set_ylim(0.05,0.35)
ax3.set_ylim(0.75,1.5)

ax.spines['top'].set_visible(False)
ax2.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax3.spines['bottom'].set_visible(False)
ax3.xaxis.tick_top()
ax3.tick_params(labeltop='off')

ax.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax2.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax3.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)

ax.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax2.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax3.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)

d = .015  
kwargs = dict(transform=ax2.transAxes, color='k', clip_on=False)
ax2.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
ax2.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagona

kwargs.update(transform=ax.transAxes)  # switch to the bottom axes
ax.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
ax.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

kwargs = dict(transform=ax3.transAxes, color='k', clip_on=False)
ax3.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
ax3.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

ax.set_xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')
ax.set_ylabel('$Support\ Needed\ (M$€$/day)$')
ax.yaxis.set_label_coords(0.05, 0.5, transform=f.transFigure)
legend = ax.legend(loc='upper center', bbox_to_anchor=(0.2,3.75),
          ncol=3, fancybox=True, shadow=True)
legend = ax2.legend(loc='upper center', bbox_to_anchor=(.5,2.55),
          ncol=3, fancybox=True, shadow=True)
legend = ax3.legend(loc='upper center', bbox_to_anchor=(.8,1.35),
          ncol=3, fancybox=True, shadow=True)

ax.set_axis_bgcolor('whitesmoke')
ax2.set_axis_bgcolor('whitesmoke')
ax3.set_axis_bgcolor('whitesmoke')

# plt.savefig('neededsupport.pdf')

plt.show()

#%% Scatter plot of UC vs ED total support needed

resultsdf_systemcostsUC = pd.read_excel('EOMplots.xlsx', 'systemcostsUC')
resultsdf_systemcostsED = pd.read_excel('EOMplots.xlsx', 'systemcostsED')

# Results from UC 
WindLevelUC = resultsdf_systemcostsUC['WindLevel'].tolist()
relvarcostsUC = resultsdf_systemcostsUC['relvarcosts'].tolist()
relfixedcostsUC = resultsdf_systemcostsUC['relfixedcosts'].tolist()
relcapcostsUC = resultsdf_systemcostsUC['relcapcosts'].tolist()

# Results from ED 
WindLevelED = resultsdf_systemcostsED['WindLevel'].tolist()
relvarcostsED = resultsdf_systemcostsED['relvarcosts'].tolist()
relfixedcostsED = resultsdf_systemcostsED['relfixedcosts'].tolist()
relcapcostsED = resultsdf_systemcostsED['relcapcosts'].tolist()

cmap=plt.cm.viridis
cmap.set_under(cmap(int(0)))
WindLevelED_array = np.asarray(WindLevelED)

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(4)
ax = fig.add_subplot(111)

cax = ax.scatter(relfixedcostsED, relfixedcostsUC, c=WindLevelED_array, marker='o', s=100, alpha=1, label = '$Actual\ Relation$', cmap=cmap, vmin=0, vmax=WindLevelED_array.max())

relcapcostsED_array = np.asarray(relfixedcostsED)
relcapcostsUC_array = np.asarray(relfixedcostsUC)

m, b = np.polyfit(relcapcostsED_array, relcapcostsUC_array, 1)
ax.plot(relcapcostsED_array, m*relcapcostsED_array + b, '-', c='grey', label='$Linear\ Regression\ Line\ (Actual\ Relation)$')

x = np.arange(0.05,0.45,0.05) 
ax.plot(x,x,'--',c='black', label = '$Perfect\ Relation$')

ax.set_axis_bgcolor('whitesmoke')
ax.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)

legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=3, fancybox=True, shadow=True)

legend.legendHandles[2].set_color('black')
        
ax.set_xlabel('$Total\ Support\ Needed\ w/o\ UC\ (M$€$/day)$')
ax.set_ylabel('$Total\ Support\ Needed\ w/\ UC\ (M$€$/day)$')

cbar = fig.colorbar(cax, extend='min')
cbar.set_label('$Wind\ Penetration\ Level ($%$)$', rotation=270, labelpad=20)

# plt.savefig('EDvsUCforfixedcosts.pdf')

plt.show()


#%% Scatter plot of UC/ED for different costs. Finding difference.

difvar = [a/b*100 for a,b in zip(relvarcostsED,relvarcostsUC)]
diffixed = [a/b*100 for a,b in zip(relfixedcostsED,relfixedcostsUC)]
difcap = [a/b*100 for a,b in zip(relcapcostsED,relcapcostsUC)]

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(5)
ax = fig.add_subplot(111)

ax.scatter(WindLevelED, difvar, marker='o', edgecolor = 'k', linewidth='1', facecolor=sns.xkcd_rgb["windows blue"], s=80, alpha=1, label = '$Variable\ Cost$')
ax.scatter(WindLevelED, diffixed, marker='v', edgecolor = 'k', linewidth='1', facecolor=sns.xkcd_rgb["medium green"], s=80, alpha=1, label = '$+\ Fixed\ Costs$')
ax.scatter(WindLevelED, difcap, marker='s', edgecolor = 'k', linewidth='1', facecolor=sns.xkcd_rgb["pale red"], s=80, alpha=1, label = '$+\ Capital\ Costs$')

ax.plot(WindLevelED, difvar, '--', c='grey', linewidth=0.5)
ax.plot(WindLevelED, diffixed, '--', c='grey', linewidth=0.5)
ax.plot(WindLevelED, difcap, '--', c='grey', linewidth=0.5)

ax.set_axis_bgcolor('whitesmoke')
ax.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)

legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=3, fancybox=True, shadow=True)

ax.set_xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')
ax.set_ylabel('$Support\ Needed\ using\ UC\ over\ Support\ Needed\ using\ ED\ ($%$)$')

ax.set_xlim(-5,75)

# plt.savefig('EDvsUCforallcosts.pdf')

plt.show()

resultsdf_systemcosts = pd.read_excel('EOMplots.xlsx', 'EUsim')

# Results
WindLevel = resultsdf_systemcosts['WindLevel'].tolist()
relvarcosts = resultsdf_systemcosts['relvarcosts'].tolist()
relfixedcosts = resultsdf_systemcosts['relfixedcosts'].tolist()
relcapcosts = resultsdf_systemcosts['relcapcosts'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

fig = plt.figure(3)
f, (ax3, ax2, ax) = plt.subplots(3, 1, sharex=True)

ax.plot(WindLevel, relvarcosts, c=sns.xkcd_rgb["windows blue"],alpha=1, label = '$Variable\ Costs$')
ax2.plot(WindLevel, relfixedcosts, c=sns.xkcd_rgb["medium green"],alpha=1, label = '$+\ Fixed\ Costs$')
ax3.plot(WindLevel, relcapcosts, c=sns.xkcd_rgb["pale red"],alpha=1, label = '$+\ Capital\ Costs$')

ax.set_ylim(8,12.5)
ax2.set_ylim(58,88)
ax3.set_ylim(240,310)
ax.set_xlim(0,55)

ax.spines['top'].set_visible(False)
ax2.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax3.spines['bottom'].set_visible(False)
ax3.xaxis.tick_top()
ax3.tick_params(labeltop='off') 

ax.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax2.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax3.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)

ax.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax2.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax3.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)

d = .015  
kwargs = dict(transform=ax2.transAxes, color='k', clip_on=False)
ax2.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
ax2.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagona

kwargs.update(transform=ax.transAxes)  # switch to the bottom axes
ax.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
ax.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

kwargs = dict(transform=ax3.transAxes, color='k', clip_on=False)
ax3.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
ax3.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

ax.set_xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')
ax.set_ylabel('$Support\ Needed\ (M$€$/day)$')
ax.yaxis.set_label_coords(0.075, 0.5, transform=f.transFigure)
#ax3.set_title(r'$Total\ support\ needed\ to\ cover\ missing\ money$', y=1.08)
legend = ax.legend(loc='upper center', bbox_to_anchor=(0.2,3.75),
          ncol=3, fancybox=True, shadow=True)
legend = ax2.legend(loc='upper center', bbox_to_anchor=(.5,2.55),
          ncol=3, fancybox=True, shadow=True)
legend = ax3.legend(loc='upper center', bbox_to_anchor=(.8,1.35),
          ncol=3, fancybox=True, shadow=True)

ax.set_axis_bgcolor('whitesmoke')
ax2.set_axis_bgcolor('whitesmoke')
ax3.set_axis_bgcolor('whitesmoke')

# plt.savefig('neededsupportEU.pdf')

plt.show()

# Read data from Excel spreadsheet
resultsdf_coal = pd.read_excel('EOMplots.xlsx', 'coalDE').set_index('WindLevel') #coal
resultsdf_nuclear = pd.read_excel('EOMplots.xlsx', 'nuclearDE').set_index('WindLevel') #nuclear
resultsdf_hydro = pd.read_excel('EOMplots.xlsx', 'hydroDE').set_index('WindLevel') #hydro
resultsdf_gas = pd.read_excel('EOMplots.xlsx', 'gasDE').set_index('WindLevel') #CCGT

# Coal color dataframe
color = {}
for w in resultsdf_coal.index:
    if resultsdf_coal.Revenue[w] > resultsdf_coal.CapCost[w]:
        color[w] = sns.xkcd_rgb["windows blue"]
    elif resultsdf_coal.Revenue[w] < resultsdf_coal.CapCost[w] and resultsdf_coal.Revenue[w] > resultsdf_coal.FixedCostSUCost[w]:
        color[w] = sns.xkcd_rgb["medium green"]
    elif resultsdf_coal.Revenue[w] < resultsdf_coal.FixedCostSUCost[w] and resultsdf_coal.Revenue[w] > resultsdf_coal.VarCost[w]:
        color[w] = sns.xkcd_rgb["amber"]
    elif resultsdf_coal.Revenue[w] <= resultsdf_coal.VarCost[w]:
        color[w] = sns.xkcd_rgb["pale red"]

color_df = pd.DataFrame([[key,value] for key,value in color.items()],columns=['WindLevel','Color']).set_index('WindLevel')

results_df_coal = pd.merge(resultsdf_coal, color_df, right_index = True, left_index = True).reset_index()

results_df_coal.sort_values(['WindLevel'], ascending=[True], inplace=True)

# Nuclear color dataframe
color = {}
for w in resultsdf_nuclear.index:
    if resultsdf_nuclear.Revenue[w] > resultsdf_nuclear.CapCost[w]:
        color[w] = sns.xkcd_rgb["windows blue"]
    elif resultsdf_nuclear.Revenue[w] < resultsdf_nuclear.CapCost[w] and resultsdf_nuclear.Revenue[w] > resultsdf_nuclear.FixedCostSUCost[w]:
        color[w] = sns.xkcd_rgb["medium green"]
    elif resultsdf_nuclear.Revenue[w] < resultsdf_nuclear.FixedCostSUCost[w] and resultsdf_nuclear.Revenue[w] > resultsdf_nuclear.VarCost[w]:
        color[w] = sns.xkcd_rgb["amber"]
    elif resultsdf_nuclear.Revenue[w] <= resultsdf_nuclear.VarCost[w]:
        color[w] = sns.xkcd_rgb["pale red"]

color_df = pd.DataFrame([[key,value] for key,value in color.items()],columns=['WindLevel','Color']).set_index('WindLevel')

results_df_nuclear = pd.merge(resultsdf_nuclear, color_df, right_index = True, left_index = True).reset_index()

results_df_nuclear.sort_values(['WindLevel'], ascending=[True], inplace=True)

# Hydro color dataframe
color = {}
for w in resultsdf_hydro.index:
    if resultsdf_hydro.Revenue[w] > resultsdf_hydro.CapCost[w]:
        color[w] = sns.xkcd_rgb["windows blue"]
    elif resultsdf_hydro.Revenue[w] < resultsdf_hydro.CapCost[w] and resultsdf_hydro.Revenue[w] > resultsdf_hydro.FixedCostSUCost[w]:
        color[w] = sns.xkcd_rgb["medium green"]
    elif resultsdf_hydro.Revenue[w] < resultsdf_hydro.FixedCostSUCost[w] and resultsdf_hydro.Revenue[w] > resultsdf_hydro.VarCost[w]:
        color[w] = sns.xkcd_rgb["amber"]
    elif resultsdf_hydro.Revenue[w] <= resultsdf_hydro.VarCost[w]:
        color[w] = sns.xkcd_rgb["pale red"]

color_df = pd.DataFrame([[key,value] for key,value in color.items()],columns=['WindLevel','Color']).set_index('WindLevel')

results_df_hydro = pd.merge(resultsdf_hydro, color_df, right_index = True, left_index = True).reset_index()

results_df_hydro.sort_values(['WindLevel'], ascending=[True], inplace=True)

# Gas color dataframe (CCGT)
color = {}
for w in resultsdf_gas.index:
    if resultsdf_gas.Revenue[w] > resultsdf_gas.CapCost[w]:
        color[w] = sns.xkcd_rgb["windows blue"]
    elif resultsdf_gas.Revenue[w] < resultsdf_gas.CapCost[w] and resultsdf_gas.Revenue[w] > resultsdf_gas.FixedCostSUCost[w]:
        color[w] = sns.xkcd_rgb["medium green"]
    elif resultsdf_gas.Revenue[w] < resultsdf_gas.FixedCostSUCost[w] and resultsdf_gas.Revenue[w] > resultsdf_gas.VarCost[w]:
        color[w] = sns.xkcd_rgb["amber"]
    elif resultsdf_gas.Revenue[w] <= resultsdf_gas.VarCost[w]:
        color[w] = sns.xkcd_rgb["pale red"]

color_df = pd.DataFrame([[key,value] for key,value in color.items()],columns=['WindLevel','Color']).set_index('WindLevel')

results_df_gas = pd.merge(resultsdf_gas, color_df, right_index = True, left_index = True).reset_index()

results_df_gas.sort_values(['WindLevel'], ascending=[True], inplace=True)

# Coal
ys_coal = results_df_coal['CapFactor'].tolist()
xs_coal = results_df_coal['Revenue'].tolist()
zs_coal = results_df_coal['WindLevel'].tolist()
c_coal = results_df_coal['Color'].tolist()
# Nuclear
ys_nuclear = results_df_nuclear['CapFactor'].tolist()
xs_nuclear = results_df_nuclear['Revenue'].tolist()
zs_nuclear = results_df_nuclear['WindLevel'].tolist()
c_nuclear = results_df_nuclear['Color'].tolist()
# Hydro
ys_hydro = results_df_hydro['CapFactor'].tolist()
xs_hydro = results_df_hydro['Revenue'].tolist()
zs_hydro = results_df_hydro['WindLevel'].tolist()
c_hydro = results_df_hydro['Color'].tolist()
# Gas CCGT
ys_gas = results_df_gas['CapFactor'].tolist()
xs_gas = results_df_gas['Revenue'].tolist()
zs_gas = results_df_gas['WindLevel'].tolist()
c_gas = results_df_gas['Color'].tolist()

sns.set_color_codes("dark")
sns.set_style('ticks')

# Revenue vs. windpenetration level
fig = plt.figure(1)
ax = fig.add_subplot(111)

ax.scatter(zs_coal, xs_coal, facecolor=c_coal, marker='o', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$Coal$')
ax.scatter(zs_nuclear, xs_nuclear, facecolor=c_nuclear, marker='v', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$Nuclear$')
ax.scatter(zs_hydro, xs_hydro, facecolor=c_hydro, marker='s', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$Hydro$')
ax.scatter(zs_gas, xs_gas, facecolor=c_gas, marker='p', edgecolor = 'k', linewidth='1', s=80, alpha=1, label = '$CCGT$')

ax.plot(zs_coal, xs_coal, '--', c='grey', linewidth=0.5)
ax.plot(zs_nuclear, xs_nuclear, '--', c='grey', linewidth=0.5)
ax.plot(zs_hydro, xs_hydro, '--', c='grey', linewidth=0.5)
ax.plot(zs_gas, xs_gas, '--', c='grey', linewidth=0.5)

ax.set_xlabel('$Average\ Wind\ Penetration\ Level\ ($%$)$')
ax.set_ylabel('$Revenue\ ($€$/MW-day)$')
ax.set_axis_bgcolor('whitesmoke')

ax.yaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)
ax.xaxis.grid(True, linestyle='-', which='major', color='lightgray', alpha=0.5)

legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=4, fancybox=True, shadow=True)
          
legend.legendHandles[0].set_color('grey')
legend.legendHandles[1].set_color('grey')
legend.legendHandles[2].set_color('grey')
legend.legendHandles[3].set_color('grey')

txt = ('$Red:\ Revenue\ <\ Variable\ Costs$\n$Yellow:\ Variable\ Costs\ <\ Revenue\ <\ Fixed\ Costs$\n$Green:\ Fixed\ Costs\ <\ Revenue\ <\ Capital\ Costs$\n$Blue:\ Revenue\ >\ All\ Costs$')
fig.text(.1,-.15,txt)

# plt.savefig('revenuevswindEU.pdf')

plt.show()















