
# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Created by Disa Mhembere
# Email: disa@jhu.edu
# Author: Disa Mhembere
# Adapted from Author: Glen A. Coppersmith 
# For the purpose of developing ground truths for the MR biggraph
# graph invariant computations

from math import sqrt
import os
from math import ceil
import argparse

import numpy as np
import networkx as nx
import scipy.linalg
import cPickle as pickle
from numpy import *
import time

####################
####################
## EVALUATE GRAPH ##
####################
####################
  
def evaluate_graph( thisReplicate, invariant):
    """
    Take the NetworkX graph in thisReplicate and evaluate it using
    the invariant specified. Return said value.
    """
    
    doAllInvariants = False
    if invariant == -1:
        doAllInvariants = True
        print "Doing all invariants at once, returning an array of them instead of a single value..."
        thisReplicateInvariantValue = []
       
    ########
    # SIZE #
    ########
    if (invariant == 1 or doAllInvariants):
        size = thisReplicate.number_of_edges()
        if doAllInvariants:
            thisReplicateInvariantValue.append(size)
        else:
            thisReplicateInvariantValue = size

    ##############
    # MAX DEGREE #
    ##############
    if (invariant == 2 or doAllInvariants):
        
        degArr = [] 
        
        maxDegree = -1
        replicateDegree = thisReplicate.degree()
        for entry in replicateDegree:
            if maxDegree < entry:
                maxDegree = entry
                
            degArr.append(replicateDegree[entry])
            writeArrayToFile(degArr, os.path.join("bench",str(thisReplicate.number_of_nodes()),"degArr.txt"))
            
        degArr = np.array(degArr)
        np.save(os.path.join("bench",str(thisReplicate.number_of_nodes()),"degArr.npy"), degArr)
            
        if doAllInvariants:
            thisReplicateInvariantValue.append(maxDegree)
        else:
            thisReplicateInvariantValue = maxDegree

    ##################
    # EIGENVALUE MAD #
    ##################
    if (invariant == 4 or doAllInvariants):
        thisEigenvalues, thisEigenvectors = linalg.eig(nx.adj_matrix(thisReplicate) )
        thisEigenvalues.sort()
        if len(thisEigenvalues) > 0:
            MADe = float(thisEigenvalues[-1])
            np.save(os.path.join("bench",str(thisReplicate.number_of_nodes()),"MAD.npy"), MADe)
            
        else:
            MADe= 0
        if doAllInvariants:
            thisReplicateInvariantValue.append(MADe)
        else:
            thisReplicateInvariantValue = MADe
            
    ##################
    # SCAN STATISTIC #
    ##################
    if (invariant == 5 or doAllInvariants):
        maxScanStat = -1
        
        scanStatArr = []
        
        for node in thisReplicate.nodes():
            tempNodeList = thisReplicate.neighbors(node)
            tempNodeList.append(node) #Append the central node to the neighborhood before inducing the subgraph, since it is left out by neighbors(.)
            inducedSubgraph = thisReplicate.subgraph(tempNodeList)
            thisNodeScanStat = inducedSubgraph.number_of_edges() #The number of edges in the 1-hop neighborhood of node
            
            scanStatArr.append(thisNodeScanStat)
            
            if thisNodeScanStat > maxScanStat:
                maxScanStat = thisNodeScanStat
        
        writeArrayToFile(scanStatArr, os.path.join("bench",str(thisReplicate.number_of_nodes()),"scanStatArr.txt"))
        
        scanStatArr = np.array(scanStatArr)
        np.save(os.path.join("bench",str(thisReplicate.number_of_nodes()),"scanStatArr.npy"), scanStatArr)
        
        if doAllInvariants:
            thisReplicateInvariantValue.append(maxScanStat)
        else:
            thisReplicateInvariantValue = maxScanStat
        
    #################
    # NUM TRIANGLES #
    #################
    if (invariant == 6 or doAllInvariants):
        
        triArr = []
        
        triangleList = nx.triangles(thisReplicate) #This returns a dict with the number of triangles each node participates in
        
        # This maintains order
        for vertex in sorted(triangleList.keys()):
            triArr.append(int(round(triangleList[vertex]/3.0)))
        
        triangles = sum(triangleList.values())/3
        
        writeArrayToFile(triArr,os.path.join("bench",str(thisReplicate.number_of_nodes()),"triArr.txt"))
        
        triArr = np.array(triArr)
        np.save(os.path.join("bench",str(thisReplicate.number_of_nodes()),"triArr.npy"), triArr)
        
        if doAllInvariants:
            thisReplicateInvariantValue.append(triangles)
        else:
            thisReplicateInvariantValue = triangles

    ##########################
    # Clustering Coefficient #
    ##########################
    if (invariant==8 or doAllInvariants):
        try:
            cc = nx.average_clustering( thisReplicate )
            ccArr = nx.clustering( thisReplicate )
            writeArrayToFile(ccArr.values(),os.path.join("bench",str(thisReplicate.number_of_nodes()),"ccArr.txt"))
            
            ccArr = np.array(ccArr)
            ccArr = ccArr[()].values()
            np.save(os.path.join("bench",str(thisReplicate.number_of_nodes()),"ccArr.npy"), ccArr)
            
        except ZeroDivisionError: #This only occurs with degenerate Graphs --GAC
            cc = -999
        if doAllInvariants:
            thisReplicateInvariantValue.append(cc)
        else:
            thisReplicateInvariantValue = cc

    #######################
    # Average Path Length #
    #######################
    if (invariant == 9 or doAllInvariants):
        apl = -1 * nx.average_shortest_path_length( thisReplicate ) #Since smaller APL is in favor of HA over H0, we use -1 * APL instead of APL. --GAC
        
        pairsArr = length = nx.all_pairs_shortest_path(thisReplicate)
        aplArr = []
        for vert in thisReplicate:
            total = 0
            for neigh in range (len(pairsArr[vert])):
                total += (len(pairsArr[vert][neigh]) - 1)
            aplArr.append(ceil(total/float(len(pairsArr[vert]))))
        
        writeArrayToFile(aplArr,os.path.join("bench",str(thisReplicate.number_of_nodes()),"aplArr.txt"))
        
        aplArr = np.array(aplArr)
        np.save(os.path.join("bench",str(thisReplicate.number_of_nodes()),"aplArr.npy"), aplArr)
        
        if doAllInvariants:
            thisReplicateInvariantValue.append(apl)
        else:
            thisReplicateInvariantValue = apl
    
    ##########
    # DEGREE #
    ##########
    
    if (doAllInvariants):
        thisReplicateInvariantValue.append(thisReplicate.number_of_nodes())
        
    ##############
    # GREEDY MAD #
    ##############
    # We put this last because it actually deconstructs the Graph
    if (invariant == 3 or doAllInvariants):
        maxAverageDegree = -1
        nodeList = thisReplicate.nodes()
        while nodeList: #While there's something left
            degreeList = thisReplicate.degree(nodeList)
            smallestDegree = len(nodeList)+3
            smallestID = -1
            for nodeID in range(0, len(degreeList)): #Search for the node with the smallest degree
                if thisReplicate.degree( nodeList[nodeID] ) < smallestDegree:
                    smallestID = nodeList[nodeID]
                    smallestDegree = thisReplicate.degree( nodeList[nodeID] )
            #Calculate the average degree
            sumDegree = 0.0
            for degree in degreeList:
                sumDegree += degree
            if sumDegree > 0:
                thisAverageDegree = sumDegree / float(len(nodeList))
            else:
                thisAverageDegree = 0

            #If this average degree is larger than any we've seen previously, store it
            if thisAverageDegree > maxAverageDegree:
                maxAverageDegree = thisAverageDegree

            #Remove the vertex with the smallest degree
            #**** DISA EDIT***** thisReplicate.delete_node(smallestID)
            thisReplicate.remove_node(smallestID)
            nodeList.remove(smallestID)

        if doAllInvariants:
            thisReplicateInvariantValue.append(maxAverageDegree)
        else:
            thisReplicateInvariantValue = maxAverageDegree
        
    return thisReplicateInvariantValue

################
# ARRAY WRITER #
################

def writeArrayToFile(arr, name):
    f = open(name, 'w')
    for ind, val in enumerate (arr):
        f.write(str(ind)+ " : " + str(val) + "\n")
    f.close()

#################
# DICT TO ARRAY #
#################

def writeDictToFile(dic, name):
    f = open(name, 'w')
    for ind in range (len(dic)):
        f.write(str(ind)+ " : " + str(dic[ind]) + "\n")
    f.close()

def main():
    parser = argparse.ArgumentParser(description='Performs bench statistics on networkX graphs')
    parser.add_argument('G_fn', action='store',help='Full filename of networkX graph')
    parser.add_argument('tnum', type = int, default=-1, action='store',help='Test number. Each test assigned a number. See source code for understanding. Default is all tests are run')
    
    result = parser.parse_args()
    evaluate_graph( pickle.load(open(result.Gfn, "rb")), result.tnum )

if __name__ == '__main__':
    main()