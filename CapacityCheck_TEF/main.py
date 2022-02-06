"""
JSON Parser script to read POD information
"""

import os
import argparse
import math
import json
import csv

# Define global variables for processing
InputWorkerNodePool = []
InputBusiness = []
InputClusterCapacity = []

# Constant settings
ClusterReservedCapacity = 10 # Percentage of reserved cluster to leave free for calculation
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
        "WorkerNodes" : 0, 
        "CPU": 0,
        "RAM": 0,
        "Storage": 0,
    },
    {   # Capacity master nodes calculated from predefined constant
        "MasterNodes" : 0, 
        "CPU": 0,
        "RAM": 0,
        "Storage": 0,
    },
    {   # Capacity Net total worker nodes including worker node (WorkerNodePool + WorkerNode)
        "TotalReqNodes" : 0, 
        "CPU": 0,
        "RAM": 0,
        "Storage": 0,
    }    
]
# Result to hold the final calculated cluster allocation
ResultClusters = []
# Result to dump out JSON data
ResultJSONDumpOut = {}


# JSON Write out result
def writeresultJSON(filepath):
    # Data write results out from variables
    ResultJSONDumpOut.update ({"Business": InputBusiness}) 
    ResultJSONDumpOut.update ({"WorkerNodeCapacity": ResultCalculations_WN[0]}) 
    ResultJSONDumpOut.update ({"MasterNodeCapacity": ResultCalculations_WN[1]}) 
    ResultJSONDumpOut.update ({"TotalCapacityRequired": ResultCalculations_WN[2]}) 
    ResultJSONDumpOut.update ({"Clusters": ResultClusters}) 

    with open(filepath, "w") as outfile:
        json_object = json.dumps(ResultJSONDumpOut, indent = 4)
        outfile.write(json_object)


# JSON parser to read WorkerNodePool details
def readjsonwebform(filpath):
    filejson = open(filpath,) 
    data = json.load(filejson)
    InputBusiness.append (data['Business'])
    for WorkerNode in data['Capacity']['WorkerNodePool']:
        InputWorkerNodePool.append (WorkerNode)
    filejson.close()


# Read Cluster capacity details from csv file
def readcsvclustercapacity(filpath):
    with open(filpath, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader) # Read field names, but its not used at the moment
        for row in csvreader:
            InputClusterCapacity.append(row)


# Calculate WorkerNode
def calculate_workernode():
    
    # Calculate required worker nodes from worker node pool
    for WorkerNode in InputWorkerNodePool:
        #ResultCalculations_WN[0]['Web_NoOfWorkerNodePool'] = ResultCalculations_WN[0]['Web_NoOfWorkerNodePool'] + 1
        ResultCalculations_WN[0]['WorkerNodes'] = ResultCalculations_WN[0]['WorkerNodes'] + WorkerNode['Nodecount']
        ResultCalculations_WN[0]['CPU'] = ResultCalculations_WN[0]['CPU'] + (WorkerNode['Nodecount'] * WorkerNode['NodeCPU'])
        ResultCalculations_WN[0]['RAM'] = ResultCalculations_WN[0]['RAM'] + (WorkerNode['Nodecount'] * WorkerNode['NodeRAM'])
        ResultCalculations_WN[0]['Storage'] = ResultCalculations_WN[0]['Storage'] + (WorkerNode['Nodecount'] * WorkerNode['NodeStorage'])
    
    # Calculate required Master Node from required workernodes
    for MasterNodeConst in MasterNodeCapacity:
        if (ResultCalculations_WN[0]['WorkerNodes'] <= MasterNodeConst['Capacity']):
            ResultCalculations_WN[1]['MasterNodes'] = MasterNodeConst['ReqMasterNodeCnt']
            ResultCalculations_WN[1]['CPU'] = MasterNodeConst['ReqMasterNodeCnt'] * MasterNodeConst['CPU']
            ResultCalculations_WN[1]['RAM'] = MasterNodeConst['ReqMasterNodeCnt'] * MasterNodeConst['RAM']
            ResultCalculations_WN[1]['Storage'] = MasterNodeConst['ReqMasterNodeCnt'] * MasterNodeConst['Storage']
            break
    
    # Calculate consolidated net capacity requirement
    ResultCalculations_WN[2]['TotalReqNodes'] = ResultCalculations_WN[0]['WorkerNodes'] + ResultCalculations_WN[1]['MasterNodes']
    ResultCalculations_WN[2]['CPU'] = ResultCalculations_WN[0]['CPU'] + ResultCalculations_WN[1]['CPU']
    ResultCalculations_WN[2]['RAM'] = ResultCalculations_WN[0]['RAM'] + ResultCalculations_WN[1]['RAM']
    ResultCalculations_WN[2]['Storage'] = ResultCalculations_WN[0]['Storage'] + ResultCalculations_WN[1]['Storage']


# Calculate Cluster Capacity
def calculateclustercapacity():
    # Loop through all clustres and check if capacity is possible
    ClusterReservedCapacity_Divider = (100-ClusterReservedCapacity)/100
    for cluster in InputClusterCapacity:
        # skip processing if cluster name or row is empty
        if (len(cluster[0]) == 0):
            continue
        
        ClusterActCPU = math.floor(float(cluster[1]) * ClusterReservedCapacity_Divider)    #Excel Col-2 Free CPU, reduce 10% as buffer and round down
        ClusterActRAM = math.floor(float(cluster[2]) * ClusterReservedCapacity_Divider)    #Excel Col-3 Free RAM, reduce 10% as buffer and round down
        ClusterActCAP = math.floor(float(cluster[3]) * ClusterReservedCapacity_Divider)    #Excel Col-4 Free Memory, reduce 10% as buffer and round down
        
        ClustersRes = {}
        ClustersRes.update ({"Name": cluster[0]})       #Excel Col-1 Cluster Name
        ClustersRes.update ({"FreeCPU": ClusterActCPU})      
        ClustersRes.update ({"FreeRAM": ClusterActRAM})      
        ClustersRes.update ({"FreeStorage": ClusterActCAP})

        if((ResultCalculations_WN[2]['CPU'] <= ClusterActCPU) and (ResultCalculations_WN[2]['RAM'] <= ClusterActRAM) and \
        (ResultCalculations_WN[2]['Storage'] <= ClusterActCAP)):
            ClustersRes.update ({"HasCapacity": "Yes"})
        else:
            ClustersRes.update ({"HasCapacity": "No"})
        # Add calculated result to final result list
        ClustersRes.update ({"ReservedCapacityPercent": ClusterReservedCapacity})
        ResultClusters.append (ClustersRes)
        print(ClustersRes)


if __name__ == "__main__":

    # configuration of command line interface:
    parser = argparse.ArgumentParser(description='Script for parsing POD details using JSON outputs')
    parser.add_argument('-w', '--webjson',required=True, help="path to json file from web input")
    parser.add_argument('-c', '--clustcsv',required=True, help="path to excel file with cluster free capacity")
    parser.add_argument('-o', '--outfile', help="path to output file to write the results")
    args = parser.parse_args()
    args_dict = vars(args)

    print ("Calculating Cluster capacity with " + str(ClusterReservedCapacity) + " percent reserverd capacity...")
    #Read inputs JSON + CSV files
    readjsonwebform(args.webjson)
    readcsvclustercapacity(args.clustcsv)

    #Calcualtions
    calculate_workernode()
    print(ResultCalculations_WN[2])
    calculateclustercapacity()

    #Write result
    writeresultJSON(args.outfile)
    print("Script processing complete...")

    
    
    
    
