from itertools import cycle
from itertools import groupby
from matplotlib.ticker import MaxNLocator, MultipleLocator
from numpy import *
import fnmatch
import itertools
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import operator
import os
import re
import shutil
import unicodedata
import pandas as pd

# Functions

def remove_punctuation(dataString):
    symbols = ["'", "(", ")", ",", ".", ":", ";", "abstract={", "title={", "{", "}"]
    for item in symbols:
        dataString = dataString.replace(item, " ")
    return dataString


def keywords_cleanup(indata_keywords):
    indata_keywords = indata_keywords.replace(",", ";")
    symbols = ["[", "]", "(", ")", "'", "+", ":", "-", "null"]
    for item in symbols:
        indata_keywords = indata_keywords.replace(item, "")
    return indata_keywords


def remove_similars(dataString):
    data = pd.read_table('code/similars.csv', sep=',')
    for i in range(len(data)):
        dataString = dataString.replace(data.at[i, 'ORIGINAL'], data.at[i, 'REPLACEMENT'])
    return dataString


def get_color():
    for item in ['r', 'b', 'k', 'r', 'b', 'k', 'r', 'b', 'k']:
        yield item


def set_fontsize(fig, fontsize):
    """
    For each text object of a figure fig, set the font size to fontsize
    """
    def match(artist):
        return artist.__module__ == "matplotlib.text"

    for textobj in fig.findobj(match=match):
        textobj.set_fontsize(fontsize)


def strip_accents(s):
    nkfd_form = unicodedata.normalize('NFKD', unicode(s))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

# General plot formatting

# Define some common formatting for the plots

bbox_props = dict(boxstyle="round4,pad=0.3", fc="w", ec="w", lw=1)      # boxes enclosing labels on some plots
# rc({'font.size': 8})
# rc('lines', linewidth=1.3)
dpi_fig = 600           # resolution of the figures in dpi
axes_lw = 0.4             # line thickness for the axes
axes_color = '0.7'        # grey color for the axes
plot_font_size = 8
perso_linewidth = 0.3

# Customizing general matplotlib rc parameters


def init_plotting():        # This will change your default rcParams
    plt.rcParams['figure.figsize'] = (3, 3)
    plt.rcParams['font.size'] = 8
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['axes.labelsize'] = plt.rcParams['font.size']
    plt.rcParams['axes.titlesize'] = 1.5*plt.rcParams['font.size']
    plt.rcParams['legend.fontsize'] = plt.rcParams['font.size']
    plt.rcParams['xtick.labelsize'] = plt.rcParams['font.size']
    plt.rcParams['ytick.labelsize'] = plt.rcParams['font.size']
    plt.rcParams['savefig.dpi'] = 2 * plt.rcParams['savefig.dpi']
    plt.rcParams['axes.linewidth'] = perso_linewidth
    plt.rcParams['savefig.dpi'] = '300'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.edgecolor'] = '0'
    plt.rcParams['axes.grid'] = False
    plt.rcParams['grid.color'] = 'white'
    plt.rcParams['grid.linestyle'] = '-'
    plt.rcParams['grid.linewidth'] = '0.1'
    plt.rcParams['axes.axisbelow'] = True
    plt.rcParams['lines.markersize'] = 2.3
    plt.rcParams['lines.markeredgewidth'] = '0.1'
    plt.rcParams['lines.color'] = 'r'
    # plt.rcParams['lines.marker']= 'o'
    plt.rcParams['lines.linestyle'] = ''
    plt.rcParams['xtick.color'] = '0'
    plt.rcParams['ytick.color'] = '0'
    plt.rcParams['axes.color_cycle'] = ['#3778bf', '#feb308', '#a8a495', '#7bb274', '#825f87']
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['right'].set_visible('False')
    plt.gca().spines['top'].set_visible('False')
    plt.gca().spines['top'].set_color('none')
    plt.gca().xaxis.set_ticks_position('bottom')
    plt.gca().yaxis.set_ticks_position('left')
    plt.rcParams['ytick.minor.size'] = 1.5
    plt.rcParams['ytick.major.width'] = perso_linewidth
    plt.rcParams['ytick.minor.width'] = perso_linewidth
    plt.rcParams['xtick.major.width'] = perso_linewidth
    plt.rcParams['xtick.minor.width'] = perso_linewidth
init_plotting()

# Plotting of keyword frequency
# defining line style and thickness to be cycled through when plotting multiple keywords on the same plot
lines = ["-", ":"]
linewidth = ["0.5", "0.75", "1", "1.5"]
linecycler = cycle(lines)
lwcycler = cycle(linewidth)

# Initialization of the script

# set paths to working folders
# script     = argv
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
color = get_color()


# Keyword stats

# reading common words list, convert the txt into a list
listOfWords = []
with open('code/CommonkeywordList.txt', 'r') as fh:
    listOfWords = fh.read()

# read the list of keywords to be analysed; have to be exactly 8 keywords, or the plot panels won't work
analyse = []
fh = open('code/keywordList.txt', 'r')
for line in fh:
    analyse.append(line.strip().split(','))

# Do the analysis for each query file/year
for root, dirs, files in os.walk(rootPath):
    counter = 0
    for filename in fnmatch.filter(files, pattern):
        filenameOut = filename
        filename = rootPath + filename
        year = (filenameOut[0:4])               # retrieves year from results filename
        # file_size = os.path.getsize(filename)   # get the current file size for the counter
        indata = (open(filename)).read()        # retrieves full text from results file

# removing the DUPLICATES from the imported query file
        everything_list = re.findall(r'\n@((.|\n)*?)\},\n\}\n', indata)     # separates indata per article
        everything_list = list(set(everything_list))                        # removes duplicates
        total_records += len(everything_list)                               # total number of records ( all!)
        everything_list = ' '.join(str(e) for e in everything_list)         # convert back to a string
        everything_list = everything_list.lower()                           # convert everything lower case
        # count the number of RECORDS for the current year
        article_list = re.findall(r'url=\{(.*?)\},', everything_list)
        count = len(article_list)
        del article_list

        # ----------------------------------------------------------- #
        # #### Network analysis on keywords from the query results ####
        # ----------------------------------------------------------- #
        indata_keywords = re.findall(r'keywords=\{((.|\n)*?)},', everything_list)
        indata_keywords = str(indata_keywords)
        indata_keywords_authors = re.findall(r'author_keywords=\{((.|\n)*?)},', everything_list)
        indata_keywords_authors = str(indata_keywords_authors)
        indata_keywords = indata_keywords + ',' + indata_keywords_authors
        indata = remove_punctuation(indata)
        indata_keywords = remove_similars(indata_keywords)

        regex = '([a-z0-9 -]*?);'
        split = re.split(regex, indata_keywords)
        listOfKeywords = split
        listOfKeywords = filter(None, listOfKeywords)   # remove empty keywords which were showing up for some reason

        keyword_graph_string = ''       #creates permutation for gephy netwqeok analysis
        elements = [re.findall(r'[a-z0-9]{3,}', item) for item in listOfKeywords]
        elements = [item for item in elements if len(item) > 1]
        for elem in elements:
            for x in itertools.combinations(elem, 2):
                x = str(x).replace('(', '')
                x = x.replace(')', '')
                x = x.replace("'", '')
                keyword_graph_string += x + '\n'

# ----------------------------------------------------------- #
# Analysis of the frequency of words in titles and abstracts  #
# ----------------------------------------------------------- #

# extract only the content of titles and abstracts
        indata_abs = re.findall(r'abstract=\{((.|\n)*?)},', everything_list)
        indata_abs = list(set(indata_abs))
        indata_abs = str(indata_abs).strip('[]')
        indata_title = re.findall(r'title=\{((.|\n)*?)},', everything_list)
        indata_title = list(set(indata_title))
        indata_title = str(indata_title).strip('[]')

        indata = indata_title + indata_abs  # combine the abstract and title data
        indata = indata.lower()
        indata = indata.replace("title={", " ")
        indata = indata.replace("abstract={", " ")
        indata = indata.replace("}", " ")

        rough_length = str(len(indata))
        indata = remove_punctuation(indata)
        indata = remove_similars(indata)
        words = indata.split()  # convert the file into a list of words, for frequency analysis

        # count the occurrences of each word in the results files
        result = dict((key, len(list(group))) for key, group in groupby(sorted(words)))
        l = result.items()
        l.sort(key=lambda item: item[1], reverse=True)    # sort results by decreasing order

        # preparing the raw text file for the wordle, using only the most frequent words
        # remove all entries with count less than 3, so that rarely used words are not considered
        keyword_sorted = [item for item in l if item[1] > 2]
        keyword_sorted_curated = filter(lambda name: name[0] not in listOfWords, keyword_sorted) # remove all keywords from the common words list
        wordle_list = keyword_sorted_curated[:150] # select only the 150 most frequent words of the year
        wordle_string = ' '.join(((e[0] + ' ') * int(e[1])) for e in wordle_list) # prepare the data for the wordle file

        # save wordle_string in txt file
        wordle_file = dirResults + year + '-wordle.txt'
        with open(wordle_file, 'w') as wf:
            wf.write(wordle_string)

        # prepare the string for the result file for all the keywords investigated
        for t in analyse:
            batch_keyword = t[0]
            if [s for s in l if batch_keyword in s]:
                keywordCount = str(dict(l)[batch_keyword])
            else:
                keywordCount = '0'  # if no occurence of keyword found during the year
            keyword_results = keyword_results + year + ', ' + keywordCount + ', ' + str(count) + ', ' + rough_length + ', ' + '\n'
            # keyword_results = keyword_results + year + ', ' + keywordCount + ', ' + str(count) + ', ' + rough_length
            # + ', ' + str(average_abstract_length) + ', '  + str(average_title_length) + '\n'
            outFileKeywordName = dirResults + batch_keyword + '-results.csv'
            out_fileKeyword = open(outFileKeywordName, 'a+')
            out_fileKeyword.write(keyword_results)
            out_fileKeyword.close()
            keyword_results = ''

        keyword_graph_string = strip_accents(keyword_graph_string)

        outFileName = dirResults + 'keywords_graphe.csv'
        with open(outFileName, 'a+') as of:
            of.write(keyword_graph_string)

        # ----------------------------------------------------------- #
        # WRITE all the results in the various files
        # ----------------------------------------------------------- #

        outFileName = dirResults + filenameOut + '-results.txt'
        with open(outFileName, 'w') as of:
            for t in keyword_sorted_curated:
                of.write(','.join(str(s) for s in t) + '\n')    # write the count for all words found in data file

# Second master plot, with the KEYWORDS results

number_of_keywords = len(analyse)
gs = gridspec.GridSpec(number_of_keywords/4+2, 4)

plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(4, 4))
sub1 = plt.subplot(gs[:2, :3])
sub1.set_ylabel('Occurence [a.u.]')
sub1.xaxis.set_major_locator(MaxNLocator(5))
minorLocator = MultipleLocator(1)
majorLocator = MultipleLocator(10)
sub1.xaxis.set_minor_locator(minorLocator)
sub1.axes.set_xlim(left=1970, right=2013)
sub1.tick_params(which='minor', color=axes_color, width=axes_lw)
sub1.tick_params(which='major', color=axes_color, width=axes_lw)
sub1.set_yticklabels([])
sub1.xaxis.grid(True, linestyle='-', linewidth=axes_lw, color=axes_color)
sub1.yaxis.grid(False)
sub1.set_yticks([])
sub1.yaxis.tick_left()
sub1.yaxis.tick_right()
sub1.spines['right'].set_visible(False)

# plt.grid(True)
for loc, spine in sub1.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)

i = 0
for t in analyse:
    t = t[0]
    outFileCSV = dirResults + t + '-results.csv'
    result = genfromtxt(outFileCSV, delimiter=',')

    # convert the input array to separate arrays for plotting
    valeurYear = [x[0] for x in result]
    minYear = min(valeurYear)
    maxYear = max(valeurYear)
    valeurLength = [x[3] for x in result]
    valeur_ref = min(valeurLength)
    valeurY = [(x[1]/x[3]*valeur_ref) for x in result]  # normalization par nombre de characteres de toutes resultats .dans l'ann+ee
    max_valeurYear = max(valeurY)
    acolor = next(color)
    sub1.plot(valeurYear, valeurY, next(linecycler), lw=next(lwcycler), color=acolor, label=t, alpha=1)
    sub3 = plt.subplot(gs[(i/4)+2, i % 4])
    sub3.set_title(t, fontsize=9)
    sub3.xaxis.set_major_locator(majorLocator)
    sub3.axes.set_xlim(right=2001, left=1989)
    [label.set_visible(False) for label in sub3.get_xticklabels()]
    sub3.set_yticks([])
    sub3.xaxis.set_minor_locator(minorLocator)
    sub3.axhline(linewidth=axes_lw, color=axes_color)
    sub3.axvline(linewidth=axes_lw, color=axes_color)
    sub3.spines['top'].set_visible(False)
    sub3.spines['right'].set_visible(False)
    sub3.spines['left'].set_visible(False)
    sub3.spines['bottom'].set_visible(False)
    sub3.plot(valeurYear, valeurY / max_valeurYear, 'ro', label=t, alpha=1, lw=2)
    sub3.tick_params(which='minor', color=axes_color, width=axes_lw)
    sub3.tick_params(which='major', color=axes_color, width=axes_lw)
    sub3.xaxis.grid(True, linestyle='-', linewidth=axes_lw, color=axes_color)
    sub3.yaxis.grid(False)
    i += 1

# sort the legend in alphabetical order
handles, labels = sub1.get_legend_handles_labels()
hl = sorted(zip(handles, labels),
            key=operator.itemgetter(1))
handles2, labels2 = zip(*hl)
leg = sub1.legend(handles2, labels2,  bbox_to_anchor=(0.96, 0.5), loc='center left', prop={'size': 9}, handlelength=1.3, handletextpad=0.5)
leg.get_frame().set_alpha(0)    # this will make the box totally transparent
leg.get_frame().set_edgecolor('white')  # this will make the edges of the border white

set_fontsize(plt, plot_font_size)

plt.tight_layout()

fig_name = 'figure keyword.png'
plt.savefig(fig_name, dpi=dpi_fig)