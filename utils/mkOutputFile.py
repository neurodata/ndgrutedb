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

# Create dir name
filePath = os.path.join(params[1],params[2])

# Create directory
# os.makedirs(directory)
print "#@@# " + filePath + " #@@#"
