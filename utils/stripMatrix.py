#!/usr/bin/python

## Make a directory based on input parent directory and desired directory name ##
## mkDir(parentDir, dirName)

############################################################################################
## (c) 2012 The Johns Hopkins University / Applied Physics Laboratory.  All Rights Reserved.
############################################################################################

from sys import argv
import string
import random
import os


# read in command line args
params = list(argv)

# Read File
inFile = open(params[1])
buffer = []
keepCurrentSet = True
pointer = 0
matrix = "'"
for line in inFile:
	if pointer > 1:
		if pointer < 6:		
			matrix += line
	pointer += 1
matrix = matrix[:-2]
matrix += "'"
inFile.close()
	

# Print Matrix
print "#@@# " + matrix + " #@@#"
