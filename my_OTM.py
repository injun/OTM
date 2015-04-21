from itertools import cycle
from itertools import groupby
from matplotlib.ticker import MaxNLocator, MultipleLocator, FormatStrFormatter
from numpy import *
from scipy import stats
import fnmatch
import itertools
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import math
from os.path import getsize as get_size
import numpy as np
import operator
import os
import re
import scipy as sp
import shutil
import time
import unicodedata
import pandas as pd

# set paths for working directories

rootPath = './bibsample/'       # folder containing the query result files *.bib
pattern = '*.bib'               # extension of query result files
dirResults = './results/'       # output results folder

# empty the results folder
if os.path.exists(dirResults):
    shutil.rmtree(dirResults)       # delete if it exists
os.makedirs(dirResults)             # create a new, empty results folder

# Data Input
# read the list of keywords to be analysed
analyse = []
fh = open('code/keywordList.txt', 'r')
for line in fh:
    analyse.append(line.strip().split(','))

# Do the analysis for each year
for root, dirs, files in os.walk(rootPath):
    counter = 0
    for filename in fnmatch.filter(files, pattern):
        filenameOut = filename
        filename += rootPath
        year = (filenameOut[0:4])               # retrieves year from results filename
        file_size = os.path.getsize(filename)   # get the current file size for the counter
        indata = (open(filename)).read()        # retrieves full text from results file

        # initialize the counters for superconductivity papers (stats measured for each year)
        page_length_supercon = []
        papers_supercon = 0

        # removing the DUPLICATES in the original data
        everything_list = re.findall(r'\n@((.|\n)*?)\},\n\}\n', indata)     # separates indata per article
        everything_list = list(set(everything_list))                        # removes duplicates
        total_records += len(everything_list)                               # total number of records ( all!)
        everything_list = ' '.join(str(e) for e in everything_list)         # convert back to a string
        everything_list = everything_list.lower()                           # convert everything lower case