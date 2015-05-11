import pandas as pd
from collections import defaultdict
from itertools import groupby

results = pd.read_csv('1-200.csv', sep=',', index_col=False)
# results = results.sort_index(by='PY')   # sort by publication year

timespan = range(2000, 2016)
keywords = defaultdict(str)
frequency = defaultdict(str)
keyword_results = ''

for year in timespan:
    for i in range(1, len(results)):
        if year == results.iloc[i]['Year']:
            author_keywords = results.iloc[i]['Author Keywords']
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
    print top_10_keywords
    with open('top_10_keywords.txt', 'w') as of:
        for word in top_10_keywords:
            print word[0]
            keyword_results = keyword_results + str(year) + ', ' + word[0] + ', ' + word[1] + '\n'
            outFileKeywordName = year + '-results.csv'
            out_fileKeyword = open(outFileKeywordName, 'a+')
            out_fileKeyword.write(keyword_results)
            out_fileKeyword.close()
            keyword_results = ''

# store in result file: year, counts
#
# print keywords
#
# # plot frequency of keyword and select keywords by year