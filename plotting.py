from matplotlib.ticker import MaxNLocator, MultipleLocator
import matplotlib.gridspec as gridspec
import operator
import matplotlib.pyplot as plt
from numpy import genfromtxt
from itertools import cycle

def get_color():
    for color in cycle(['r', 'b', 'k']):
        yield color

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

# Plotting of keyword frequency
# defining line style and thickness to be cycled through when plotting multiple keywords on the same plot
lines = ["-", ":"]
linewidth = ["0.5", "0.75", "1", "1.5"]
linecycler = cycle(lines)
lwcycler = cycle(linewidth)

def set_fontsize(fig, fontsize):
    """
    For each text object of a figure fig, set the font size to fontsize
    """
    def match(artist):
        return artist.__module__ == "matplotlib.text"

    for textobj in fig.findobj(match=match):
        textobj.set_fontsize(fontsize)


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

color = get_color()
# ----------------------------------------------------------- #
# Analysis of the frequency of words in titles and abstracts  #
# ----------------------------------------------------------- #

# Second master plot, with the KEYWORDS results
def plot(analyse, dirResults):
    number_of_keywords = len(analyse)
    gs = gridspec.GridSpec(number_of_keywords/4+2, 4)

    plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(4, 4))
    sub1 = plt.subplot(gs[:2, :3])
    sub1.set_ylabel('Occurence [a.u.]')
    sub1.xaxis.set_major_locator(MaxNLocator(5))
    minorLocator = MultipleLocator(1)
    majorLocator = MultipleLocator(10)
    sub1.xaxis.set_minor_locator(minorLocator)
    sub1.axes.set_xlim(left=1989, right=2001)
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
        valeurLength = [x[2] for x in result]
        valeur_ref = min(valeurLength)
        valeurY = [(x[1]/x[2]*valeur_ref) for x in result]  # normalization par nombre de articles dans l'annee
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
        sub3.plot(valeurYear, valeurY / max_valeurYear, 'k-', label=t, alpha=1, lw=0.75)
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
    leg.get_frame().set_alpha(0)            # this will make the box totally transparent
    leg.get_frame().set_edgecolor('white')  # this will make the edges of the border white

    set_fontsize(plt, plot_font_size)

    plt.tight_layout()

    fig_name = 'figure keyword.png'
    plt.savefig(fig_name, dpi=dpi_fig)