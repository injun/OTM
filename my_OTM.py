from itertools import groupby
import fnmatch
import os
import shutil
from plot_keywords import plotting as plt_keywords
from get_sections import *


# set paths to working folders
rootPath = './bibsample/'           # folder containing the query result files *.bib
pattern = '*.bib'                   # extension of query result files
dirResults = './results/'           # output results folder
if os.path.exists(dirResults):
    shutil.rmtree(dirResults)       # delete results folder if exists
os.makedirs(dirResults)             # creates a new, empty one


# initialization of variables
keyword_results = ''
keyword_graph_string = ''
total_records = 0       # total number of records (articles) in all results files

# Keyword stats

# reading common keywords file, convert into a list
common_keywords = []
with open('code/CommonkeywordList.txt', 'r') as fh:
    common_keywords = fh.read()
common_words = []
with open('code/commonWords.txt', 'r') as fh:
    common_words = fh.read()
# read the list of keywords to be analysed; have to be exactly 8 keywords, or the plot panels won't work
analyse = []
fh = open('code/keywordList.txt', 'r')
for line in fh:
    analyse.append(line.strip().split(','))

# Frequency analysis for each query file/year
for root, dirs, files in os.walk(rootPath):
    counter = 0
    for filename in fnmatch.filter(files, pattern):
        filenameOut = filename
        filename = rootPath + filename
        year = (filenameOut[0:4])               # retrieves year from results filename
        indata = (open(filename)).read()        # retrieves full text from results file

        everything_list = get_articles(indata)          # separate articles in results file
        total_records += count_articles(indata)         # count total number of articles
        indata = get_title_abstract(everything_list)    # extract abstracts
        words = indata.split()                          # convert the file into a list of words, for frequency analysis

        # count the occurrences of each word in the results files
        result = dict((key, len(list(group))) for key, group in groupby(sorted(words)))     # groups similar instances (key) and returns a list (group), converts list to dictionary
        l = result.items()                                                                  # convert into a list
        l.sort(key=lambda item: item[1], reverse=True)                                      # sort results by decreasing order

        # preparing the raw text file for the wordle, using only the most frequent words
        # remove all entries with count less than 3, so that rarely used words are not considered
        keyword_sorted = [item for item in l if item[1] > 2]
        keyword_sorted_temp = filter(lambda word: word[0] not in common_keywords, keyword_sorted) # remove all common keywords
        keyword_sorted_curated = filter(lambda word: word[0] not in common_words, keyword_sorted_temp)    # remove all common words

        # prepare the string for the result file for all the keywords investigated
        for t in analyse:
            batch_keyword = t[0]
            if [s for s in l if batch_keyword in s]:
                keywordCount = str(dict(l)[batch_keyword])
            else:
                keywordCount = '0'  # if no occurence of keyword found during the year
            keyword_results = keyword_results + year + ', ' + keywordCount + ', ' + str(total_records) + ', ' + '\n'
            outFileKeywordName = dirResults + batch_keyword + '-results.csv'
            out_fileKeyword = open(outFileKeywordName, 'a+')
            out_fileKeyword.write(keyword_results)
            out_fileKeyword.close()
            keyword_results = ''

        # Output to files

        outFileName = dirResults + filenameOut + '-results.txt'
        with open(outFileName, 'w') as of:
            for t in keyword_sorted_curated:
                of.write(','.join(str(s) for s in t) + '\n')    # write the count for all words found in data file

plt_keywords(analyse, dirResults)   # plot keyword frequency