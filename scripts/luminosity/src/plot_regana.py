#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2023-05-15 09:48:01 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import sys, os

################################################################################################################################################
'''
ltsep package import and pathing definitions
'''

# Import package for cuts
from ltsep import Root

lt=Root(os.path.realpath(__file__))

# Add this to all files for more dynamic pathing
USER=lt.USER # Grab user info for file finding
HOST=lt.HOST
REPLAYPATH=lt.REPLAYPATH
UTILPATH=lt.UTILPATH
SCRIPTPATH=lt.SCRIPTPATH
ANATYPE=lt.ANATYPE

################################################################################################################################################

print("\nRunning as %s on %s, hallc_replay_lt path assumed as %s" % (USER, HOST, REPLAYPATH))

sys.path.insert(0,"%s/luminosity/src/%sLT" % (SCRIPTPATH,ANATYPE))
import data_path

settingList = ["10p6cl1","10p6cl2","10p6cl3","8p2cl1"]
momentumList = [-3.266, -4.204, -6.269, -5.745] # HMS
#momentumList = [6.842, 6.053, -6.269, -5.745] # SHMS

dataDict = {}

all_relyield = np.array([])
all_uncern_relyield = np.array([])
all_current = np.array([])

for i,s in enumerate(settingList):
    dataDict[s] = {}
    data_val = data_path.get_file(s,SCRIPTPATH)
    target = data_val[0]
    inp_f = data_val[2] # out_f is inp_f for global analysis

    # Converts csv data to dataframe
    try:
        data = pd.read_csv(inp_f)
        # replace NaN values with the mean of the column
        data = data.fillna(data.mean())
        print(inp_f)
        print(data.keys())
        dataDict[s]['momentum'] = momentumList[i]
        dataDict[s]['current'] = data['current']
        dataDict[s]['rel_yield'] = data['yieldRel_HMS_track']
        dataDict[s]['yield'] = data['yield_HMS_track']
        dataDict[s]['yield_error'] = data['uncern_yieldRel_HMS_track']
        # reshape the currents, yields, and yield errors into column vectors
        dataDict[s]['x'] = dataDict[s]["current"][:, np.newaxis]
        dataDict[s]['y'] = dataDict[s]["rel_yield"][:, np.newaxis]

        # create a linear regression object and fit the data
        dataDict[s]['reg'] = LinearRegression().fit(dataDict[s]['x'], dataDict[s]['y'])

        # calculate the chi-squared value
        dataDict[s]['expected_y'] = dataDict[s]['reg'].predict(dataDict[s]['x'])
        #dataDict[s]['chi_squared'] = np.sum((dataDict[s]['y'] - dataDict[s]['expected_y'])**2 / dataDict[s]['yield_error']**2)

        np.append(all_relyield,[val for val in data['yieldRel_HMS_track']])
        np.append(all_uncern_relyield,[val for val in data['uncern_yieldRel_HMS_track']])
        np.append(all_current,[val for val in data['current']])
        
    except IOError:
        print("Error: %s does not appear to exist." % inp_f)
        sys.exit(0)

print(dataDict.keys())
print(dataDict.values())

################################################################################################################################################

all_current = all_current.flatten()[:, np.newaxis]
all_relyield = all_relyield.np.flatten()[:, np.newaxis]
all_reg = LinearRegression().fit(all_current, all_relyield)


################################################################################################################################################

# Define a list of error bar formats and plot styles to cycle through
fmt_list = ['o', 's', '^', 'd']
style_list = ['-', '--', ':', '-.']
color_list = ['red', 'green', 'blue', 'orange']

relyield_fig = plt.figure(figsize=(12,8))

# plot the data with error bars and the regression line
for i, s in enumerate(settingList):
    plt.errorbar(dataDict[s]['x'][:,0], dataDict[s]['y'][:,0], yerr=dataDict[s]['yield_error'], fmt=fmt_list[i], label="{0}, {1}".format(s,dataDict[s]['momentum']), color=color_list[i])
    plt.plot(dataDict[s]['x'], dataDict[s]['reg'].predict(dataDict[s]['x']), linestyle=style_list[i], color=color_list[i])
    plt.plot(all_relyield, all_reg.predict(all_relyield), linestyle=':', color='purple')
    # print the slope, intercept, and chi-squared value
    print('Slope:', dataDict[s]['reg'].coef_[0][0])
    print('Intercept:', dataDict[s]['reg'].intercept_[0])
    #print('Chi-squared:', dataDict[s]['chi_squared'])
plt.xlabel('Current')
plt.ylabel('Rel. Yield')
plt.title('Rel. Yield vs Current')
plt.legend()

yield_fig = plt.figure(figsize=(12,8))

# plot the data with error bars and the regression line
for i, s in enumerate(settingList):
    plt.errorbar(dataDict[s]['x'][:,0], dataDict[s]['yield'], yerr=dataDict[s]['yield_error'], fmt=fmt_list[i], label="{0}, {1}".format(s,dataDict[s]['momentum']), color=color_list[i])
plt.xlabel('Current')
plt.ylabel('Yield')
plt.title('Yield vs Current')
plt.legend()

momentum_fig = plt.figure(figsize=(12,8))

# plot the data with error bars and the regression line
for i, s in enumerate(settingList):
    plt.errorbar(dataDict[s]['x'][:,0], np.ones_like(dataDict[s]['x'][:,0])*dataDict[s]['momentum'], yerr=dataDict[s]['yield_error'], fmt=fmt_list[i], label="{0}".format(s), color=color_list[i])
plt.xlabel('Current')
plt.ylabel('Momentum')
plt.title('Momentum vs Current')
plt.legend()

plt.show()
