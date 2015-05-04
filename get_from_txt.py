import pandas as pd
from itertools import groupby
from collections import defaultdict

results = pd.read_csv('1990-2000.txt', sep='\t', index_col=False)
# results = results.sort_index(by='PY')   # sort by publication year

#print(type(results.iloc[1]['PY']))

timespan = range(1990, 2001)
keywords = defaultdict(str)
for year in timespan:

    for i in range(1, len(results)):
        if year == results.iloc[i]['PY']:
            keywords_string = results.iloc[i]['DE']
            if isinstance(keywords_string, str):
                keywords[year] = keywords[year] + ";" + keywords_string.lower()   # Create dictionary of keywords, indexed by year
print keywords[1991].split(';')


# count keyword frequency: top 10
# result = dict((key, len(list(group))) for key, group in groupby(sorted(words)))     # groups similar instances (key) and returns a list (group), converts list to dictionary
# l = result.items()                                                                  # convert into a list
# l.sort(key=lambda item: item[1], reverse=True)
#
# # count selected keywords
# result = dict((key, len(list(group))) for key, group in groupby(sorted(words)))     # groups similar instances (key) and returns a list (group), converts list to dictionary
#         l = result.items()                                                                  # convert into a list
#         l.sort(key=lambda item: item[1], reverse=True)
# store in result file: year, counts
#
# print keywords
#
# # plot frequency of keyword and select keywords by year
