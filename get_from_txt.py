from collections import defaultdict
from itertools import groupby
import shutil
import os
import pandas as pd


# set path to working folders
root_csv = './csv_results/'           # folder containing the query result files *.bib
dir_top10 = './results/top10'           # output results folder
if os.path.exists(dir_top10):
    shutil.rmtree(dir_top10)       # delete results folder if exists
os.makedirs(dir_top10)             # creates a new, empty one


results = pd.read_csv('csv_results/1-200.csv', sep=',', index_col=False)
# results = results.sort_index(by='PY')   # sort by publication year

timespan = range(2000, 2007)
keywords = defaultdict(str)
frequency = defaultdict(str)
top_global = defaultdict(str)
top10_results = ''
top_global_results = ''


# Get most frequent author and index keywords and organize by year
for year in timespan:
    for i in range(1, len(results)):
        if year == results.iloc[i]['Year']:
            author_keywords = results.iloc[i]['Author Keywords']    # TODO: eliminate blank spaces and null results
            index_keywords = results.iloc[i]['Index Keywords']
            if isinstance(author_keywords, str):
                keywords[year] = keywords[year] + ";" + author_keywords.lower()
            if isinstance(index_keywords, str):
                keywords[year] = keywords[year] + ';' + index_keywords.lower()
    keywords[year] = keywords[year].split(';')

# count keyword frequency: top 10
    frequency[year] = dict((key, len(list(group))) for key, group in groupby(sorted(keywords[year])))     # groups similar instances (key) and returns a list (group), converts list to dictionary
    frequency_list = frequency[year].items()
    frequency_list.sort(key=lambda item: item[1], reverse=True)
    top_10_keywords = frequency_list[:10]   # get only 10 highest counts

    # Save results to files
    with open('results/top_10_keywords.txt', 'w') as of:
        for word in top_10_keywords:
            current_keyword = str(word[0])
            current_count = str(word[1])
            current_year = str(year)
            top10_results = top10_results + current_keyword + ', ' + current_count + '\n'
            outFileKeywordName = dir_top10 + '_' + current_year + '.csv'
            out_fileKeyword = open(outFileKeywordName, 'a+')
            out_fileKeyword.write(top10_results)
            out_fileKeyword.close()
            top10_results = ''

# get frequency of top 10 keywords / year organized by year
    for keyword, freq in top_10_keywords:
        top_global.setdefault(keyword, {})[year] = freq

# save global keyword frequency per year
with open('results/topglobal_keywords.txt', 'w') as of:
    for keyword in top_global:
        for year in top_global[keyword]:
            count = top_global[keyword][year]
            top_global_results = top_global_results + str(year) + ', ' + str(count) + ' \n'
        out_file_name = dir_top10 + '_' + keyword + '.csv'
        out_file = open(out_file_name, 'a+')
        out_file.write(top_global_results)
        out_file.close()
        top_global_results = ''



    #

#
# # plot frequency of keyword and select keywords by year