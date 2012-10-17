# Copyright 2009
# Human Language Technology Center of Excellence
# Johns Hopkins University
# Author: Glen A. Coppersmith [coppersmith@jhu.edu]

from math import sqrt
#import random

#To allow other non-graph functions of this file to be used when nx is not present.
try:
    import networkx as nx
except:
    print "Not importing NetworkX, functionality may be impacted."
try:
    import scipy.linalg
except:
    print "Not importing scipy.linalg, functionality may be impacted."

from numpy import *
import time

  ####################################
 # Support for Command Line Options #
####################################

def floatRange( start, end, step):
    """
    Provides almost equivalent functionality to the builtin range()
    function for floating points -- the 'end' number is also included
    floatRange( 0, 1, 0.2) gives [0,0.2,0.4,0.6,0.8,1.0]
    instead of [0,0.2,0.4,0.6,0.8], as would be expected from range()
    >>> stringToFloatRange(\"[0,1,0.25]\")
    [0.0, 0.25, 0.5, 0.75, 1.0]

    """
    vec = []
    for i in range( int(start/step), int(end/step)+1):
        vec.append( float(i) * step)
    return vec

def stringToFloatRange(argString):
    """
    Converts a string such as \"[0,1,0.2]\"
    to the equivalent range, with values cast as floats:
    [0,0.2,0.4,0.6,0.8,1.0]
    """
    args = argString[1:-1].split(",")
    return floatRange(float(args[0]), float(args[1]), float(args[2]))

def stringToIntRange(argString):
    """
    Converts a string such as \"[0,4,1]\"
    to the equivalent range, with values cast as integers:
    >>>stringToIntRange(\"[0,4,1]\")
    [0, 1, 2, 3]    
    """
    args = argString[1:-1].split(",")
    return range( int(args[0]), int(args[1]), int(args[2]))

###########################
# Graph to flat text file #
###########################
def graphToText(thisGraph, n, p, m, q, r, workingDir, header=False):
    """
    Writes out the graph to a flat text file.
    If the 'header' flag is turned on, the first line
    in the file is the number of vertices.
    Every subsequent line is an edge from v_i to v_j, space delimited:
    v_i v_j
    The filename of the newly creatd graph file is returned for convenience.
    """
    import os
    fullDirectory = workingDir+"FlatGraph_n"+str(n)+"_p"+str(p)+\
                "_m"+str(m)+"_q"+str(q)+"/"
    os.system("mkdir -p "+fullDirectory)
    filename = fullDirectory+"r"+str(r)+".txt"
    FILE = open(filename, "w")
    if header:
        FILE.write(str(n)+"\n")
    for edge in thisGraph.edges():
        FILE.write(str(edge[0])+" "+str(edge[1])+"\n")
    FILE.close()
    return filename


##################################
# Results to/from flat text file #
##################################
def writeResultsToFile(filename, resultList):
    """
    Writes a result list to a flat text file, one result per line.
    """
    FILE = open(filename, 'w')
    for result in resultList:
        FILE.write(str(result)+"\n")
    FILE.close()

def readResultsFromFile(filename):
    """
    Reads a result list formated for one result per line
    and returns the resulting array.
    """
    resultList = []
    FILE = open(filename, 'r')
    for line in FILE:
        resultList.append(float(line.strip()))
    FILE.close()
    return resultList

#################
## Erdos Renyi ##
#################

def generate_R_er_noseed(n, p, m, q, R, invariant, random, \
                         workingDir="", graphTextOutputOn=False, \
                         verbose=False):
    """
    Generates R Monte Carlo experiments and returns the results
    of the graphs evaluated for a given invariant.
    Also optionally writes each graph to a flat text file [graphTextOutputOn=True]
    n is the number of nodes or vertices.
    p is the probability of connection between the 'non-chattering' vertices.
    m is the number of 'chattering' vertices.
    q is the probabilty of connection between the 'chattering' vertices.
    invariant is the integer representing the invariant to be measured:
    SIZE = 1 #Size
    MAX_DEGREE = 2 #Max Degree
    MAD_G = 3 #Maximum Average Degree, Greedy Method
    MAD_E = 4 #Maximum Average Degree, Eigenvalue Method
    SCAN_STATISTIC = 5 #Scan Statistic
    TRIANGLES = 6 #Number Of Triangles
    CLUSTERING_COEFFICIENT = 7 #Clustering Coefficient
    AVERAGE_PATH_LENGTH = 8 #Average Path Length
    random is an instantiation of the python 'random' module, already set with random.seed(.).
    workingDir allows the specification of a directory to output files.

    For graphs without an anomaly ('chattering vertices') simply set m and q to 0:
    generate_R_er_noseed(n,p,0,0,R,invariant,random)
    """
    import os
    
    monteCarlos = []
    for r in range(0,R):
        #Create a new networkx graph and add n nodes, named by their index
        G = nx.Graph()
        G.add_nodes_from( range(0,n) )

        #Loop through the n choose 2 possible edges, and create them with probability
        #determined by their placement (anomalous or chattering vertices ['eggs' are at the beginning)
        innerCounter = 0
        outerCounter = 0
        thisDotProduct = 0.0
        for outerCounter in range(0, len(G.nodes()) ):
            for innerCounter in range(outerCounter+1, len(G.nodes()) ):

                #If the inner counter is in the egg, then the outer counter is too
                if (innerCounter < m): 
                    thisConnectionProbability = q
                else:
                    thisConnectionProbability = p
                if random.random() <= thisConnectionProbability:
                    G.add_edge(outerCounter, innerCounter)

        thisReplicateInvariantValue = -1

        #If the graph text output is requested:
        if graphTextOutputOn:
            flatGraphFilename = graphToText(G,n,p,m,q,r,workingDir,header=True)
        thisReplicateInvariantValue = evaluate_graph( G, invariant)
        monteCarlos.append( thisReplicateInvariantValue)
        if verbose:
            print "["+str(r)+"]==("+str(m)+","+str(q)+")==> Invariant["+str(invariant)+"]:",monteCarlos[-1]
    return monteCarlos


def get_critical_from_null_graph(thisNull, alpha, verbose=False):
    """
    Obtain from the distribution of graphs from our Null Hypothesis
    what the critical value for a specified alpha (for a given invariant)
    is.
    Return both the critical value and the portion of those graphs
    equal to the critical value that should be rejected.
    """
    R = len(thisNull)

    thisNull.sort()
    criticalPlace = int(alpha * R) + 1
    if verbose:
        print "Alpha, CritPlace:", alpha, criticalPlace 
    if (criticalPlace <= 1):
        print "Critical Place is too small to be correct, criticalPlace being set to the length of the vector"
        criticalPlace = 1
    criticalValue = thisNull[ -1 * criticalPlace ] #Counts criticalPlace places from the end of the array

    if verbose:
        print "Crit:", criticalValue

    #Test: How many are strictly greater than the crit value
    strictlyGreater = 0
    equalTo = 0
    for i in thisNull:
        if i > criticalValue:
            strictlyGreater += 1
        if i == criticalValue:
            equalTo += 1
    if verbose:
        print "Strictly Greater in Null:", strictlyGreater
        print "Strictly Equal To in Null:", equalTo

    alpha_d_hat = strictlyGreater / float(R)
    
    discreteCounter = 0.0
    for entry in thisNull:
        if entry == criticalValue:
            discreteCounter += 1.0

    if verbose:
        print "DiscCounter:", discreteCounter
        print "Alpha D Hat:", alpha_d_hat

    randomizedRejectionLevel = (alpha - alpha_d_hat) / ((1.0 / float(R)) * equalTo)

    if verbose:
        print "RandomizedRejectLevel:", randomizedRejectionLevel

    return [criticalValue, randomizedRejectionLevel]

def calculate_power_for_alt_graph(thisAlt, criticalValue, randomizedRejectLevel):
    """
    Calculates power for a given distribution of alternate graphs
    and a given critical value and randomized reject level.
    """
    #Sort in ascending order
    thisAlt.sort()

    #Determine how many replicates are present
    R = len(thisAlt)
    
    #if the entire distribution is above the critical value, then beta = 1
    if thisAlt[ 0 ] > criticalValue:
        beta = 1.0
    #otherwise, walk through the values to calculate beta
    else:
        counter = 0
        position = -1
        while thisAlt[ position ] > criticalValue:
            counter += 1
            position -= 1
        #Reject with some probability those where the alternative equals the critical value
        matchesCritValue = 0
        try:
            while thisAlt[ position ] == criticalValue:
                matchesCritValue += 1
                position -= 1
        #This means we have reached the end of those that match the critical value
        except IndexError:
            pass
        counterPre = counter
        random.seed(8271982)    
        for match in range(0, matchesCritValue):
            if random.random() < randomizedRejectLevel:
                counter += 1
        beta = counter / float(R)
    return beta

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
        maxDegree = -1
        replicateDegree = thisReplicate.degree()
        for entry in replicateDegree:
            if maxDegree < entry:
                maxDegree = entry
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
        for node in thisReplicate.nodes():
            tempNodeList = thisReplicate.neighbors(node)
            tempNodeList.append(node) #Append the central node to the neighborhood before inducing the subgraph, since it is left out by neighbors(.)
            inducedSubgraph = thisReplicate.subgraph(tempNodeList)
            thisNodeScanStat = inducedSubgraph.number_of_edges() #The number of edges in the 1-hop neighborhood of node
            if thisNodeScanStat > maxScanStat:
                maxScanStat = thisNodeScanStat
        if doAllInvariants:
            thisReplicateInvariantValue.append(maxScanStat)
        else:
            thisReplicateInvariantValue = maxScanStat
        
    #################
    # NUM TRIANGLES #
    #################
    if (invariant == 6 or doAllInvariants):
        triangleList = nx.triangles(thisReplicate) #This returns a list with the number of triangles each node participates in
        #**** DISA EDIT***** triangles = sum(triangleList) / 3 #Correct for each triangle being counted 3 times        
        triangles = sum(triangleList.values())/3
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
        if doAllInvariants:
            thisReplicateInvariantValue.append(apl)
        else:
            thisReplicateInvariantValue = apl
        
        
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
    

