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

# Constant settings
MasterNodeCapacity = [
            {   
                "Capacity" : 10, # Capacity for <= 10
                "ReqMasterNodeCnt" : 3, # Required master node count
                "CPU": 2,
                "RAM": 8,
                "Storage": 50
            },
            {   
                "Capacity" : 100, # Capacity for <= 100
                "ReqMasterNodeCnt" : 5, # Required master node count
                "CPU": 4,
                "RAM": 16,
                "Storage": 50
            },
            {  
                "Capacity" : 250, # Capacity for <= 250
                "ReqMasterNodeCnt" : 7, # Required master node count
                "CPU": 8,
                "RAM": 32,
                "Storage": 50
            },
            {   
                "Capacity" : 500, # Capacity for <= 500
                "ReqMasterNodeCnt" : 10, # Required master node count
                "CPU": 16,
                "RAM": 64,
                "Storage": 50
            }            
]

#Result variables defintion
ResultCalculations_WN = [
    {   # Capacity Worker node pool calculated from web input json
        #"Web_NoOfWorkerNodePool" : 0, 
        "Web_TotalNoOfWorkerNodes" : 0, 
        "CPU": 0,
        "RAM": 0,
        "Storage": 0,
    },
    {   # Capacity master nodes calculated from predefined constant
        "Const_NoOfMasterNodes" : 0, 
        "CPU": 0,
        "RAM": 0,
        "Storage": 0,
    },
    {   # Capacity Net total worker nodes including worker node (WorkerNodePool + WorkerNode)
        "Net_NoOfNodes" : 0, 
        "CPU": 0,
        "RAM": 0,
        "Storage": 0,
    }    
]


# JSON parser to read WorkerNodePool details
def readjsonwebform(filpath):
    filejson = open(filpath,) 
    data = json.load(filejson)
    InputBusiness.append (data['Business'])
    for WorkerNode in data['Capacity']['WorkerNodePool']:
        InputWorkerNodePool.append (WorkerNode)
    filejson.close()

# Calculate WorkerNode
def calculate_workernode():
    
    # Calculate required worker nodes from worker node pool
    for WorkerNode in InputWorkerNodePool:
        #ResultCalculations_WN[0]['Web_NoOfWorkerNodePool'] = ResultCalculations_WN[0]['Web_NoOfWorkerNodePool'] + 1
        ResultCalculations_WN[0]['Web_TotalNoOfWorkerNodes'] = ResultCalculations_WN[0]['Web_TotalNoOfWorkerNodes'] + WorkerNode['Nodecount']
        ResultCalculations_WN[0]['CPU'] = ResultCalculations_WN[0]['CPU'] + (WorkerNode['Nodecount'] * WorkerNode['NodeCPU'])
        ResultCalculations_WN[0]['RAM'] = ResultCalculations_WN[0]['RAM'] + (WorkerNode['Nodecount'] * WorkerNode['NodeRAM'])
        ResultCalculations_WN[0]['Storage'] = ResultCalculations_WN[0]['Storage'] + (WorkerNode['Nodecount'] * WorkerNode['NodeStorage'])
    
    # Calculate required Master Node from required workernodes
    for MasterNodeConst in MasterNodeCapacity:
        if (ResultCalculations_WN[0]['Web_TotalNoOfWorkerNodes'] <= MasterNodeConst['Capacity']):
            ResultCalculations_WN[1]['Const_NoOfMasterNodes'] = MasterNodeConst['ReqMasterNodeCnt']
            ResultCalculations_WN[1]['CPU'] = MasterNodeConst['ReqMasterNodeCnt'] * MasterNodeConst['CPU']
            ResultCalculations_WN[1]['RAM'] = MasterNodeConst['ReqMasterNodeCnt'] * MasterNodeConst['RAM']
            ResultCalculations_WN[1]['Storage'] = MasterNodeConst['ReqMasterNodeCnt'] * MasterNodeConst['Storage']
            break
    
    # Calculate consolidated net capacity requirement
    ResultCalculations_WN[2]['Net_NoOfNodes'] = ResultCalculations_WN[0]['Web_TotalNoOfWorkerNodes'] + ResultCalculations_WN[1]['Const_NoOfMasterNodes']
    ResultCalculations_WN[2]['CPU'] = ResultCalculations_WN[0]['CPU'] + ResultCalculations_WN[1]['CPU']
    ResultCalculations_WN[2]['RAM'] = ResultCalculations_WN[0]['RAM'] + ResultCalculations_WN[1]['RAM']
    ResultCalculations_WN[2]['Storage'] = ResultCalculations_WN[0]['Storage'] + ResultCalculations_WN[1]['Storage']



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

    ResultFile = open(args.outfile, "w") 
    
    #Calcualtions
    calculate_workernode()
    print ( ResultCalculations_WN[0])
    print ( ResultCalculations_WN[1])
    print (ResultCalculations_WN[2])
    

    ResultFile.write ("-----------------------------------------------------------------\n")       
    ResultFile.write ("               Worker Node Calculation Script                    \n")
    ResultFile.write ("-----------------------------------------------------------------\n")

    ResultFile.close()
    print("Script processing complete...")

    
    
    
    
