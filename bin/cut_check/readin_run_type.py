#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2023-03-22 14:45:19 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#
import pandas as pd
import os, sys

################################################################################################################################################
'''
User Inputs
'''

#ROOTPrefix = sys.argv[1]

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

run_type_dir = UTILPATH+"/DB/CUTS/run_type/"
general_dir = UTILPATH+"/DB/CUTS/general/"
param_dir = UTILPATH+"/DB/PARAM/"

runTypeDict = {

    "fADCdeadtime" : run_type_dir+"fADCdeadtime.cuts",
    "coin_heep" : run_type_dir+"coin_heep.cuts",
    "hSing_optics" : run_type_dir+"hSing_optics.cuts",
    "hSing_prod" : run_type_dir+"hSing_prod.cuts",
    "pSing_optics" : run_type_dir+"pSing_optics.cuts",
    "pSing_prod" : run_type_dir+"pSing_prod.cuts",
    "coinpeak" : run_type_dir+"coinpeak.cuts",
    "coin_prod" : run_type_dir+"coin_prod.cuts",
    "lumi" : run_type_dir+"lumi.cuts",
    "pid_eff" : run_type_dir+"pid_eff.cuts",
    "simc_coin_heep" : run_type_dir+"simc_coin_heep.cuts",
    "simc_sing_heep" : run_type_dir+"simc_sing_heep.cuts",

}

# Matches run type cuts with the general cuts (e.g pid, track, etc.)
generalDict = {
    "pid" : general_dir+"pid.cuts",
    "track" : general_dir+"track.cuts",
    "accept" : general_dir+"accept.cuts",
    "coin_time" : general_dir+"coin_time.cuts",
    "current" : general_dir+"current.cuts",
    "misc" : general_dir+"misc.cuts",
}

# Matches general cuts with run number specific cuts
paramDict = {
    "accept" : param_dir+"Acceptance_Parameters.csv",
    "track" : param_dir+"Tracking_Parameters.csv",
    "CT" : param_dir+"Timing_Parameters.csv",
    "pid" : param_dir+"PID_Parameters.csv",
    "misc" : param_dir+"Misc_Parameters.csv",
    "current" : param_dir+"Current_Parameters.csv"
}

for key, val in runTypeDict.items():
    print("{} -> {}".format(key,val))

def readcutname(cut):

    file_content = []
    with open(runTypeDict[cut], "r") as f:
        for line in f:
            if "#" not in line:
                file_content.append(line)
        
    print(" ".join(file_content))

    return file_content

def grabcut(cuts, user_inp):

    cuts = cuts.split("=")
    cut_name = cuts[0].strip()
    cut_lst = cuts[1].split("+")

    out_cuts = ""
    
    file_content = []
    if user_inp in cut_name:
        for cut in cut_lst:
            for key, val in generalDict.items():
                if key in cut:
                    cut_key = cut.strip().split(".")[0]
                    cut_val = cut.strip().split(".")[1]
                    with open(generalDict[cut_key], "r") as f:
                        for line in f:
                            if "#" not in line:
                                if cut_val in line:
                                    file_content.append(line.split("=")[1])

        out_cuts = cut_name+" = "+",".join(file_content).replace("\n","")

        print(out_cuts)
    
    return out_cuts

def runcut(cut, user_inp, runNum):
    
    cuts = grabcut(cut, user_cut_inp).split("=")
    print(cuts)
    cut_name = cuts[0].strip()
    cut_lst = cuts[1].split(",")

    for cut in cut_lst:
        for key, val in paramDict.items():
            if key in cut:
                # Splits string and checks for abs() so that it does not cut string around these curved brackets
                if "." in val and "abs" not in val:
                    paramVal = val.split(")")[0]
                    paramVal = paramVal.split(".")[1]
                    # Search param dictionary for values based off paramName key
                    fout = paramDict[key]
                    try:
                        data = dict(pd.read_csv(fout))
                    except IOError:
                        print("ERROR 9: %s not found in %s" % (paramVal,fout))
                    for i,evt in enumerate(data['Run_Start']):
                        # Check if run number is defined in param file
                        if data['Run_Start'][i] <= np.int64(runNum) <= data['Run_End'][i]:
                            cut  = cut.replace(paramName+"."+paramVal,str(data[paramVal][i]))
                            if (DEBUG):
                                print("paramVal ",paramVal, "= ",data[paramVal][i])
                            pass
                        else:
                            # print("!!!!ERROR!!!!: Run %s not found in range %s-%s" % (np.int64(runNum),data['Run_Start'][i],data['Run_End'][i])) # Error 10
                            continue

    

user_run_type_inp =  input('\n\nPlease enter a run type cut...')
cut_lst = readcutname(user_run_type_inp)

while True:    

    user_cut_inp =  input('\n\nPlease enter a specific cut (type exit to end)...')

    if user_cut_inp[0:3] == "bye" or user_cut_inp[0:4] == "exit":
        break

    while True:

        user_check_inp =  input('\nWould you like to check cuts for  specific run number? (yes or no)...')

        if "y" in user_check_inp:
            user_run_inp =  input('\nPlease enter run number (type exit to end)...')
            if user_run_inp[0:3] == "bye" or user_run_inp[0:4] == "exit":
                break
            try:
                runNum = int(user_run_inp)
            except:
                print("Need a proper run number...")
                continue
            for cut in cut_lst:
                print(cut)
                runcut(cut, user_cut_inp, runNum)
        elif "n" in user_check_inp:
            for cut in cut_lst:
                grabcut(cut, user_cut_inp)
            break
        else:
            print("Please answer yes or no...")
