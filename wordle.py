# Section of the script for counting frequency of words in title and abstract and writing results into text files for ploting word clouds
# uses list of common scientific words and regular words (from google most common words list) as filters
# some parts are already incorporated into the main my_OTM.py


# reading common keywords list, convert the txt into a list
common_keywords = []
with open('code/CommonkeywordList.txt', 'r') as fh:
    common_keywords = fh.read()

common_words = []
with open('code/commonWords.txt', 'r') as fh:
    common_words = fh.read()
       #
        # preparing the raw text file for the wordle, using only the most frequent words
        # remove all entries with count less than 3, so that rarely used words are not considered
        keyword_sorted = [item for item in l if item[1] > 2]                                       # unnecessary if filter is applied correctly
        keyword_sorted_temp = filter(lambda word: word[0] not in common_keywords, keyword_sorted) # remove all common keywords
        keyword_sorted_curated = filter(lambda word: word[0] not in common_words, keyword_sorted_temp)    # remove all common words
        wordle_list = keyword_sorted_curated[:150]                                               # select only the 150 most frequent words of the year (limit for word cloud)
        wordle_string = ' '.join(((e[0] + ' ') * int(e[1])) for e in wordle_list)                # prepare the data for the wordle file

        # save wordle_string in txt file
        wordle_file = dirResults + year + '-wordle.txt'
        with open(wordle_file, 'w') as wf:
            wf.write(wordle_string)
