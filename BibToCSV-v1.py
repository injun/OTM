import os
import re
import shutil
from sys import argv
import fnmatch
import itertools

script = argv
rootPath = './bibsample/'
pattern = '*.bib'
dirResults = './' + 'resultsCeramicomics/'

shutil.rmtree(dirResults)

if not os.path.exists(dirResults):
    os.makedirs(dirResults)

aff_string = ""
combs = []
auth_combs = []

for root, dirs, files in os.walk(rootPath):
    counter = 0
    for filename in fnmatch.filter(files, pattern):
        filenameOut = filename
        filename = rootPath + filename
        year = (filenameOut[0:4])
        indata = (open(filename)).read()

        everything_list = re.findall(r'\n\@((.|\n)*?)\},\n\}\n', indata)
        everything_list = list(set(everything_list))
        everything_list = ' '.join(str(e) for e in everything_list)
        everything_list = everything_list.lower()

        title_list = re.findall(r'title=\{(.*?)\},', everything_list)
        title_list = list(set(title_list))  # remove duplicates in the list
        title_list = [a.replace("title={", "") for a in title_list]
        title_list = [a.replace("}", "") for a in title_list]
        affiliation_list = re.findall(r'affiliation=\{(.*?)\},', everything_list)
        affiliation_list = [str(item).replace("united ", "united") for item in affiliation_list]
        affiliation_list = [str(item).replace("south ", "south") for item in affiliation_list]
        affiliation_list = [str(item).replace("north ", "north") for item in affiliation_list]
        affiliation_list = [str(item).replace("russian ", "russian") for item in affiliation_list]
        affiliation_list = [re.findall(r', ([A-Z]*[a-z]*){1}[;}]', item) for item in affiliation_list]
        affiliation_list = [item for item in affiliation_list if len(item) > 1]

        for item in affiliation_list:
            for x in itertools.combinations(item, 2):
                combs.append(x)

        outFileName = dirResults + 'countries.csv'
        with open(outFileName, 'a+') as of:
            for item in combs:
                item = str(item).replace("'", "")
                item = item.replace("(", "")
                item = item.replace(")", "")
                of.write(str(item) + '\n')
        print year


print "done"