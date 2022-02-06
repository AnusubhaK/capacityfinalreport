"""
JSON Parser script to read POD information
"""

import os
import argparse
import math
import json

# Define global variables for processing
InputWorkerNodePool = []
InputBusiness = []

CalcPodLoadDict = {
                "CPU": 0,
                "RAM": 0,
                "Storage": 0,
}

CalcReqWorkersDict = {
                "CPU": 0,
                "RAM": 0,
                "Storage": 0,
                "Count": 0
}

# JSON parser to read WorkerNodePool details
def readjsonwebform(filpath):
    filejson = open(filpath,) 
    data = json.load(filejson)
    InputBusiness.append (data['Business'])
    for WorkerNode in data['Capacity']['WorkerNodePool']:
        InputWorkerNodePool.append (WorkerNode)
    filejson.close()



if __name__ == "__main__":

    # configuration of command line interface:
    parser = argparse.ArgumentParser(description='Script for parsing POD details using JSON outputs')
    parser.add_argument('-w', '--webjson',required=True, help="path to json file from web input")
    # parser.add_argument('-p', '--podpath',required=True, help="path to excel file with cluster capacity")
    parser.add_argument('-o', '--outfile', help="path to output file to write the results")
    args = parser.parse_args()
    args_dict = vars(args)

    #Read input JSON files
    readjsonwebform(args.webjson)
    print (InputWorkerNodePool)
    print (InputBusiness)

    ResultFile = open(args.outfile, "w") 
    
    #Calcualtions

    ResultFile.write ("-----------------------------------------------------------------\n")       
    ResultFile.write ("               Worker Node Calculation Script                    \n")
    ResultFile.write ("-----------------------------------------------------------------\n")

    ResultFile.close()
    print("Script processing complete...")

    
    
    
    
