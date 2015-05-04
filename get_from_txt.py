import pandas as pd

results = pd.read_csv('1990-2000.txt', sep='\t', index_col=False)
# results = results.sort_index(by='PY')   # sort by publication year


timespan = range(1990, 2001, 1)


for year in timespan:
    for i in range(1, len(results)):
        keywords = {}
        if year == results.iloc[i]['PY']:
            keywords = keywords.update({year: results.iloc[i]['DE']})    # Create dictionary of keywords
            # count keyword frequency: top 10
            # count selected keywords

print keywords

# plot keyword and select keywrods frequency by year
