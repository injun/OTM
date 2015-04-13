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

# series of unused impor commands

# import matplotlib as mp
# import matplotlib.cm as cm
# import matplotlib.font_manager as fm
# import matplotlib.mlab as mlab
# import simplejson
# import prettyplotlib
# from matplotlib.font_manager import FontProperties
# from scipy.interpolate import spline
# from scipy.stats import norm
# from sys import argv
# import csv

# Definition of functions


class ProgressBar():
    def __init__(self, width=50):
        self.pointer = 0
        self.width = width

    def __call__(self, x, year, time_left):
        # x in percent
        self.pointer = int(self.width * (x / 100.0))
        minutes = int(time_left / 60)
        seconds = int(time_left % 60)
        if minutes == 0:
            return "|" + "#" * self.pointer + "-" * (self.width - self.pointer) + \
                   "|\n %d percent done, doing year %s, estimated time left:  %ss" % (int(x), year, seconds)
        else:
            return "|" + "#" * self.pointer + "-" * (self.width - self.pointer) + \
                   "|\n %d percent done, doing year %s, estimated time left: %smin %ss" % (
                       int(x), year, minutes, seconds)


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def remove_punctuation(datastring):
    symbols = ["'", "(", ")", ",", ".", ":", ";", "abstract={", "title={", "{", "}"]
    for item in symbols:
        datastring = datastring.replace(item, " ")
    return datastring


def keywords_cleanup(keywords):
    keywords = keywords.replace(",", ";")
    symbols = ["[", "]", "(", ")", "'", "+", ":", "-", "null"]
    for symbol in symbols:
        keywords = keywords.replace(symbol, "")
    return keywords


def remove_similars(dataString):
    data = pd.read_table('code/similars.csv', sep=',')
    for item in range(len(data)):
        dataString = dataString.replace(data.at[item, 'ORIGINAL'], data.at[item, 'REPLACEMENT'])
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


# Define some common formatting for the plots

bbox_props = dict(boxstyle="round4,pad=0.3", fc="w", ec="w", lw=1)  # boxes enclosing labels on some plots
# rc({'font.size': 8})
# rc('lines', linewidth=1.3)
dpi_fig = 600  # resolution of the figures in dpi
axes_lw = 0.4  # line thickness for the axes
axes_color = '0.7'  # grey color for the axes
plot_font_size = 8
perso_linewidth = 0.3

# Customizing general matplotlib rc parameters


def init_plotting():  # This will change your default rcParams
    plt.rcParams['figure.figsize'] = (3, 3)
    plt.rcParams['font.size'] = 8
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['axes.labelsize'] = plt.rcParams['font.size']
    plt.rcParams['axes.titlesize'] = 1.5 * plt.rcParams['font.size']
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

# Plots for keyword frequency
# defining line style and thickness to be cycled through when plotting multiple keywords on the same plot
lines = ["-", ":"]
linewidth = ["0.5", "0.75", "1", "1.5"]
linecycler = cycle(lines)
lwcycler = cycle(linewidth)


# Initialization of the script

# script     = argv
rootPath = './bibsample/'  # folder containing the bibliography query results
pattern = '*.bib'  # extension of exported bibliography files
dirResults = './results/'  # where to write the results

# empty the results folder
if os.path.exists(dirResults):
    shutil.rmtree(dirResults)  # delete it if it exists
os.makedirs(dirResults)  # create a new, empty results folder

# initialization of arrays and variables needed later
keyword_results = ''
keyword_graph_string = ''
total_records = 0
directory_size = get_size(rootPath)
color = get_color()
start_time = time.time()
pb = ProgressBar()
abstract_length_array = []
title_length_array = []
page_length_array = []

# defining the relevant fields for the different journals
bio_journal_dic = {"acta biomaterialia": 1, "acta chirurgiae orthopaedicae et traumatologiae cechoslovaca": 1,
                   "acta odontologica scandinavica": 1, "acta orthopaedica": 1, "actualites odonto-stomatologiques": 1,
                   "american journal of dentistry": 1,
                   "american journal of orthodontics and dentofacial orthopedics": 1,
                   "american journal of orthodontics and dentofacial orthopedics : official publication of the american association of orthodontists, its constituent societies, and the american board of orthodontics": 1,
                   "american journal of otology": 1, "analytical and bioanalytical chemistry": 1,
                   "angle orthodontist": 1, "annals of occupational hygiene": 1, "australian dental journal": 1,
                   "biomaterials": 1, "biomaterials medical devices and artificial organs": 1,
                   "biomedical materials": 1, "biomedical sciences instrumentation": 1, "biomedizinische technik": 1,
                   "bone": 1, "chinese journal of clinical rehabilitation": 1, "clinical materials": 1,
                   "clinical oral implants research": 1, "clinical oral investigations": 1,
                   "clinical orthopaedics and related research": 1, "current opinion in dentistry": 1,
                   "das dental-labor. le laboratoire dentaire. the dental laboratory": 1,
                   "dental clinics of north america": 1, "dental materials": 1, "dental materials journal": 1,
                   "dentistry today": 1, "deutsche stomatologie (berlin, germany : 1990)": 1,
                   "egyptian dental journal": 1, "environmental health perspectives": 1,
                   "european journal of dentistry": 1, "european journal of orthopaedic surgery and traumatology": 1,
                   "european spine journal": 1, "general dentistry": 1,
                   "hiroshima daigaku shigaku zasshi. the journal of hiroshima university dental society": 1,
                   "hua xi kou qiang yi xue za zhi \= huaxi kouqiang yixue zazhi \= west china journal of stomatology": 1,
                   "indian journal of dental research": 1, "international endodontic journal": 1,
                   "international journal of oral and maxillofacial implants": 1,
                   "international journal of prosthodontics": 1, "international orthopaedics": 1,
                   "journal of adhesive dentistry": 1, "journal of arthroplasty": 1,
                   "journal of biomedical materials research": 1,
                   "journal of biomedical materials research - part a": 1,
                   "journal of biomedical materials research - part b applied biomaterials": 1,
                   "journal of bone and joint surgery - series a": 1, "journal of bone and joint surgery - series b": 1,
                   "journal of clinical rehabilitative tissue engineering research": 1, "journal of dental research": 1,
                   "journal of dental technology : the peer-reviewed publication of the national association of dental laboratories": 1,
                   "journal of dentistry": 1, "journal of esthetic and restorative dentistry": 1,
                   "journal of esthetic and restorative dentistry : official publication of the american academy of esthetic dentistry . [et al.]": 1,
                   "journal of esthetic dentistry": 1, "journal of esthetic dentistry (canada)": 1,
                   "journal of fermentation and bioengineering": 1,
                   "journal of occupational health and safety - australia and new zealand": 1,
                   "journal of oral and maxillofacial surgery": 1, "journal of oral rehabilitation": 1,
                   "journal of orthopaedic research": 1, "journal of prosthetic dentistry": 1,
                   "journal of prosthodontic research": 1, "journal of prosthodontics": 1,
                   "journal of the american dental association": 1,
                   "journal of the japanese orthopaedic association": 1,
                   "journal of the mechanical behavior of biomedical materials": 1,
                   "medicina oral, patologia oral y cirugia bucal": 1,
                   "orthopaedics and traumatology: surgery and research": 1, "orthopedics": 1,
                   "practical periodontics and aesthetic dentistry : ppad": 1,
                   "practical procedures & aesthetic dentistry : ppad": 1,
                   "practical procedures & aesthetic dentistry : ppad.": 1,
                   "proceedings of the institution of mechanical engineers, part h: journal of engineering in medicine": 1,
                   "shika zairyo, kikai \= journal of the japanese society for dental materials and devices": 1,
                   "shikai tenbo \= dental outlook": 1, "spine": 1, "spine journal": 1, "stomatologie der ddr": 1,
                   "stomatologiia": 1, "stomatologiya": 1,
                   "the european journal of esthetic dentistry : official journal of the european academy of esthetic dentistry": 1,
                   "the international journal of oral & maxillofacial implants": 1,
                   "the international journal of prosthodontics": 1, "the journal of adhesive dentistry": 1,
                   "the journal of prosthetic dentistry": 1, "tissue engineering": 1, "tissue engineering - part a": 1,
                   "zhonghua kou qiang yi xue za zhi \= zhonghua kouqiang yixue zazhi \= chinese journal of stomatology": 1,
                   "zhonghua kou qiang yi xue za zhi \= zhonghua kouqiang yixue zazhi \= chinese journal of stomatology.": 1,
                   "international journal of computerized dentistry": 1, "journal of biomaterials applications": 1,
                   "journal of materials science: materials in medicine": 1, "lasers in medical science": 1,
                   "operative dentistry": 1, "seminars in arthroplasty": 1,
                   "trends in biomaterials and artificial organs": 1, "les cahiers de prothese": 1,
                   "journal of contemporary dental practice": 1, "archives of orthopaedic and trauma surgery": 1,
                   "attualita dentale": 1,
                   "compendium of continuing education in dentistry (jamesburg, n.j. : 1995)": 1,
                   "hotetsu rinsho. practice in prosthodontics": 1, 'l" information dentaire': 1,
                   "quintessence of dental technology": 1,
                   "spectrochimica acta - part a: molecular and biomolecular spectroscopy": 1,
                   "the medical journal of malaysia": 1, "zeitschrift fur orthopadie und ihre grenzgebiete": 1}
ceram_journal_dic = {"advances in applied ceramics": 1, "am ceram soc bull": 1, "ber deut keram gesell": 1,
                     "ber dtsch keram ges": 1, "boletin de la sociedad espanola de ceramica y vidrio": 1,
                     "british ceramic transactions": 1, "british ceramic. transactions and journal": 1,
                     "bull soc fr ceram": 1, "bulletin de la societe francaise de ceramique": 1, "canadian ceramics": 1,
                     "canadian ceramics quarterly": 1, "ceram age": 1, "ceramic transactions": 1, "ceramica": 1,
                     "ceramics - art and perception": 1, "ceramics - silikaty": 1, "ceramics - technical": 1,
                     "ceramics international": 1, "ceramurgia": 1, "ceramurgia international": 1,
                     "cfi ceramic forum international": 1, "fract in ceram mater": 1, "fract mech of ceram": 1,
                     "glass and ceramics": 1, "glass and ceramics (english translation of steklo i keramika)": 1,
                     "in: technology of glass, ceramic, or glass, ceramic to metal sealing, presented at asme winter annual meeting, (boston, u.s.a": 1,
                     "industrial ceramics": 1, "industrie ceramique and verriere": 1,
                     "industrie ceramique et verriere": 1, "interceram: international ceramic review": 1,
                     "international journal of applied ceramic technology": 1,
                     "international journal of high technology ceramics": 1, "j am ceram soc": 1, "j cer soc jap": 1,
                     "j ceram soc jpn": 1, "j. american ceramic society": 1,
                     "journal of ceramic processing research": 1, "journal of the american ceramic society": 1,
                     "journal of the australasian ceramic society": 1, "journal of the australian ceramic society": 1,
                     "journal of the canadian ceramic society": 1,
                     "journal of the ceramic society of japan. international ed.": 1,
                     "journal of the european ceramic society": 1, "journal of the korean ceramic society": 1,
                     "keramische zeitschrift": 1, "kuei suan jen hsueh pao/ journal of the chinese ceramic society": 1,
                     "kuei suan jen hsueh pao/journal of the chinese ceramic society": 1, "proc br ceram soc": 1,
                     "proc brit ceram soc (mechanical properties of ceramics)": 1,
                     "proceedings - australian ceramic conference": 1, "proceedings of the british ceramic society": 1,
                     "refractories": 1, "refractories (english translation of ogneupory)": 1,
                     "refractories and industrial ceramics": 1,
                     "sci of ceram, conf, 7th int, proc, pap, juan-les-pins, fr, sep 24-26 1973": 1,
                     "silicates industriels": 1, "trans j brit cer soc": 1, "trans j brit ceram soc": 1,
                     "transactions and journal of the british ceramic society": 1,
                     "transactions of the indian ceramic society": 1, "american ceramic society bulletin": 1,
                     "ci news (ceramics international)": 1, "applied clay science": 1, "journal of electroceramics": 1,
                     "keram z": 1, "naihuo cailiao/refractories": 1,
                     "nippon seramikkusu kyokai gakujutsu ronbunshi/journal of the ceramic society of japan": 1,
                     "revue internationale des hautes temperatures et des refractaires": 1, "steklo i keramika": 1,
                     "tile & brick international": 1, "trans indian ceram soc": 1, "world cement": 1,
                     "yogyo kyokai shi/journal of the ceramic society of japan": 1}
chem_journal_dic = {"actualite chimique": 1, "aiche journal": 1,
                    "angewandte chemie - international edition in english": 1, "applied catalysis a: general": 1,
                    "applied catalysis b: environmental": 1, "applied organometallic chemistry": 1,
                    "applied spectroscopy": 1, "catalysis today": 1, "central european journal of chemistry": 1,
                    "chemical engineering journal": 1, "chemical engineering research and design": 1,
                    "chemical engineering science": 1, "chemicke listy": 1, "chemie-ingenieur-technik": 1,
                    "chemistry and industry (london)": 1, "chemistry of materials": 1, "chemosphere": 1, "chemtech": 1,
                    "chinese journal of catalysis": 1, "chinese journal of chemical engineering": 1,
                    "electrochemical and solid-state letters": 1, "electrochemistry communications": 1,
                    "electrochimica acta": 1, "energy and fuels": 1, "eurasian chemico-technological journal": 1,
                    "european journal of inorganic chemistry": 1, "fuel cells": 1, "fuel cells bulletin": 1,
                    "glass physics and chemistry": 1, "industrial and engineering chemistry research": 1,
                    "inorganic chemistry": 1, "international journal of chemical reactor engineering": 1,
                    "journal of analytical atomic spectrometry": 1, "journal of applied chemistry of the ussr": 1,
                    "journal of applied electrochemistry": 1, "journal of chemical engineering of japan": 1,
                    "journal of chemical physics": 1, "journal of industrial and engineering chemistry": 1,
                    "journal of solid state chemistry": 1, "journal of solid state electrochemistry": 1,
                    "journal of the american chemical society": 1, "journal of the electrochemical society": 1,
                    "korean journal of chemical engineering": 1,
                    "mechanical and corrosion properties. series a, key engineering materials": 1, "quimica nova": 1,
                    "radiation physics and chemistry": 1, "radiochemistry": 1,
                    "russian journal of applied chemistry": 1, "russian journal of electrochemistry": 1,
                    "russian journal of inorganic chemistry": 1, "studies in surface science and catalysis": 1,
                    "topics in catalysis": 1, "analytica chimica acta": 1, "asian journal of chemistry": 1,
                    "berichte der bunsengesellschaft/physical chemistry chemical physics": 1,
                    "chinese journal of inorganic chemistry": 1, "corrosion science": 1,
                    "fresenius' journal of analytical chemistry": 1,
                    "fresenius' zeitschrift f\xc3\xbcr analytische chemie": 1,
                    "huagong xuebao/journal of chemical industry and engineering (china)": 1,
                    "huaxue gongcheng/chemical engineering (china)": 1, "journal of materials chemistry": 1,
                    "journal of radioanalytical and nuclear chemistry": 1,
                    "journal of sol-gel science and technology": 1, "mikrochimica acta": 1, "monatshefte fur chemie": 1,
                    "nace - international corrosion conference series": 1, "progress in solid state chemistry": 1,
                    "sensors and actuators: b. chemical": 1, "thermochimica acta": 1,
                    "world academy of science, engineering and technology": 1,
                    "zairyo to kankyo/ corrosion engineering": 1}
mater_journal_dic = {"acta materialia": 1, "acta metallurgica et materialia": 1,
                     "advanced composite materials: the official journal of the japan society of composite materials": 1,
                     "advanced composites bulletin": 1, "advanced engineering materials": 1,
                     "advanced functional materials": 1, "advanced materials": 1, "advanced materials and processes": 1,
                     "advanced materials research": 1, "advanced performance materials": 1,
                     "annales de chimie: science des materiaux": 1, "applied mechanics and materials": 1,
                     "bulletin of materials science": 1, "cailiao gongcheng/journal of materials engineering": 1,
                     "cailiao kexue yu gongyi/material science and technology": 1,
                     "cailiao yanjiu xuebao/chinese journal of materials research": 1, "composite structures": 1,
                     "composites": 1, "composites - part a: applied science and manufacturing": 1,
                     "composites engineering": 1, "composites part a: applied science and manufacturing": 1,
                     "composites part b: engineering": 1, "composites science and technology": 1,
                     "computational materials science": 1,
                     "fatigue and fracture of engineering materials and structures": 1,
                     "frontiers of materials science in china": 1, "high performance structures and materials": 1,
                     "high temperature materials and processes": 1, "inorganic materials": 1,
                     "international journal of inorganic materials": 1,
                     "international journal of materials and product technology": 1,
                     "international journal of materials research": 1,
                     "international journal of minerals, metallurgy and materials": 1,
                     "international journal of refractory metals and hard materials": 1,
                     "journal of advanced materials": 1, "journal of alloys and compounds": 1,
                     "journal of composite materials": 1,
                     "journal of engineering materials and technology, transactions of the asme": 1,
                     "journal of hazardous materials": 1, "journal of intelligent material systems and structures": 1,
                     "journal of magnetism and magnetic materials": 1,
                     "journal of materials engineering and performance": 1, "journal of materials processing tech.": 1,
                     "journal of materials processing technology": 1, "journal of materials research": 1,
                     "journal of materials science": 1, "journal of materials science and technology": 1,
                     "journal of materials science letters": 1, "journal of materials synthesis and processing": 1,
                     "journal of non-crystalline solids": 1, "journal of nuclear materials": 1,
                     "journal of porous materials": 1,
                     "jsme international journal, series 1: solid mechanics, strength of materials": 1,
                     "jsme international journal, series a: mechanics and material engineering": 1,
                     "jsme international journal, series a: solid mechanics and material engineering": 1,
                     "key engineering materials": 1, "korean journal of materials research": 1,
                     "manufacturing engineering": 1, "mater sci res": 1, "materiali in tehnologije": 1,
                     "materials and design": 1, "materials and manufacturing processes": 1,
                     "materials at high temperatures": 1, "materials characterization": 1,
                     "materials chemistry & physics": 1, "materials chemistry and physics": 1,
                     "materials engineering": 1, "materials evaluation": 1, "materials forum": 1,
                     "materials letters": 1, "materials research": 1, "materials research bulletin": 1,
                     "materials research innovations": 1, "materials science and engineering": 1,
                     "materials science and engineering a": 1, "materials science and engineering b": 1,
                     "materials science and engineering b: solid-state materials for advanced technology": 1,
                     "materials science and engineering c": 1, "materials science and technology": 1,
                     "materials science forum": 1, "materials science monographs": 1, "materials science research": 1,
                     "materials science research international": 1, "materials science- poland": 1,
                     "materials technology": 1, "materials transactions": 1, "materials transactions, jim": 1,
                     "materials world": 1, "materialwissenschaft und werkstofftechnik": 1,
                     "metallurgical and materials transactions a": 1,
                     "metallurgical and materials transactions a: physical metallurgy and materials science": 1,
                     "metallurgical and materials transactions b: process metallurgy and materials processing science": 1,
                     "metallurgical transactions a": 1, "metals and materials bury st edmunds": 1,
                     "metals and materials international": 1, "mrl bulletin of research and development": 1,
                     "mrs bulletin": 1, "nanostructured materials": 1, "nature materials": 1, "optical materials": 1,
                     "polymer composites": 1, "revista romana de materiale/ romanian journal of materials": 1,
                     "science and technology of advanced materials": 1, "scripta materialia": 1,
                     "scripta metallurgica": 1, "scripta metallurgica et materiala": 1, "soft materials": 1,
                     "solar energy materials": 1, "soviet journal of superhard materials": 1, "synthetic metals": 1,
                     "current opinion in solid state and materials science": 1,
                     "journal of metastable and nanocrystalline materials": 1,
                     "journal of reinforced plastics and composites": 1, "reviews on advanced materials science": 1,
                     "revista materia": 1, "strength of materials": 1, "stroitel'nye materialy": 1,
                     "archives of metallurgy and materials": 1, "construction and building materials": 1,
                     "diamond and related materials": 1,
                     "fenmo yejin cailiao kexue yu gongcheng/materials science and engineering of powder metallurgy": 1,
                     "fuhe cailiao xuebao/acta materiae compositae sinica": 1, "functional materials letters": 1,
                     "gaofenzi cailiao kexue yu gongcheng/polymeric materials science and engineering": 1, "glass": 1,
                     "glass international": 1, "glass science and technology": 1,
                     "glass science and technology frankfurt": 1,
                     "glass science and technology: glastechnische berichte": 1, "glass technology": 1,
                     "glass technology: european journal of glass science and technology part a": 1,
                     "glastechnische berichte": 1,
                     "gongneng cailiao yu qijian xuebao/journal of functional materials and devices": 1,
                     "gongneng cailiao/journal of functional materials": 1,
                     "hangkong cailiao xuebao/journal of aeronautical materials": 1,
                     "indian journal of engineering and materials sciences": 1,
                     "inorganic materials: applied research": 1,
                     "jingangshi yu moliao moju gongcheng/diamond & abrasives engineering": 1,
                     "jingangshi yu moliao moju gongcheng/diamond and abrasives engineering": 1,
                     "jinshu rechuli/heat treatment of metals": 1, "jinshu xuebao/ acta metallurgica sinica": 1,
                     "jinshu xuebao/acta metallurgica sinica": 1, "jom": 1, "journal of applied polymer science": 1,
                     "journal of inorganic and organometallic polymers": 1,
                     "journal of iron and steel research international": 1,
                     "journal of korean institute of metals and materials": 1, "journal of metals": 1,
                     "journal of optoelectronics and advanced materials": 1,
                     "journal of polymer science, part b: polymer physics": 1, "journal of the less-common metals": 1,
                     "journal of thermoplastic composite materials": 1,
                     "journal of university of science and technology beijing: mineral metallurgy materials (eng ed)": 1,
                     "journal wuhan university of technology, materials science edition": 1, "macromolecules": 1,
                     "mecanique, materiaux, electricite": 1, "metall": 1, "metallofizika i noveishie tekhnologii": 1,
                     "metallurg": 1, "metalurgia international": 1, "microporous and mesoporous materials": 1,
                     "new materials & new processes": 1,
                     "nippon kinzoku gakkaishi/journal of the japan institute of metals": 1,
                     "polymer engineering and science": 1, "polymers for advanced technologies": 1,
                     "powder metallurgy": 1, "powder metallurgy and metal ceramics": 1,
                     "powder metallurgy international": 1, "powder technology": 1, "rapid prototyping journal": 1,
                     "rare metals": 1, "rengong jingti xuebao/journal of synthetic crystals": 1,
                     "revista de metalurgia (madrid)": 1, "smart materials and structures": 1,
                     "soviet powder metallurgy and metal ceramics": 1, "steel research international": 1,
                     "sumitomo metals": 1, "sverkhtverdye materialy": 1,
                     "tetsu-to-hagane/journal of the iron and steel institute of japan": 1,
                     "tezhong zhuzao ji youse hejin/special casting and nonferrous alloys": 1,
                     "the carbide and tool journal": 1,
                     "transactions of nonferrous metals society of china (english edition)": 1,
                     "transactions of the indian institute of metals": 1,
                     "transactions of the iron and steel institute of japan": 1,
                     "upb scientific bulletin, series b: chemistry and materials science": 1,
                     "welding international": 1, "wuji cailiao xuebao/journal of inorganic materials": 1,
                     "xiyou jinshu / chinese journal of rare metals": 1,
                     "xiyou jinshu cailiao yu gongcheng/rare metal materials and engineering": 1,
                     "zairyo/journal of the society of materials science, japan": 1,
                     "zeitschrift fuer metallkunde/materials research and advanced techniques": 1,
                     "zeitschrift fuer werkstofftechnik/materials technology and testing": 1,
                     "zhongguo youse jinshu xuebao/chinese journal of nonferrous metals": 1, "acta metallurgica": 1,
                     "annual conference on materials for coal conversion and utilization (proceedings)": 1,
                     "archives of materials science and engineering": 1,
                     "fenmo yejin jishu/powder metallurgy technology": 1}
other_journal_dic = {'acta mechanica': 1, 'advanced packaging': 1, 'agard conference proceedings': 1,
                     'american antiquity': 1, 'ancient mesoamerica': 1, "annali dell'istituto superiore di sanita": 1,
                     'antiquity': 1, 'applications of cryogenic technology': 1,
                     'archaeology, ethnology and anthropology of eurasia': 1, 'archaeometry': 1,
                     'archeologicke rozhledy': 1, 'archeometriai muhely': 1, 'arts of asia': 1,
                     'bulletin de la societe prehistorique francaise': 1,
                     'bulletin of the japan society of precision engineering': 1, 'c e ca': 1,
                     'cailiao rechuli xuebao/transactions of materials and heat treatment': 1, 'carbon': 1,
                     'china foundry': 1, 'chinese journal of aeronautics': 1, 'chinese science bulletin': 1,
                     'chungara': 1, 'cirp annals - manufacturing technology': 1,
                     'colloids and surfaces a: physicochemical and engineering aspects': 1,
                     'communications in computer and information science': 1, 'crafts': 1, 'cryogenics': 1,
                     'cutting tool engineering': 1, 'dalton transactions': 1, 'defence science journal': 1,
                     'desalination': 1, 'desalination and water treatment': 1, 'die quintessenz der zahntechnik': 1,
                     'doklady akademii nauk': 1, 'doktorsavhandlingar vid chalmers tekniska hogskola': 1,
                     'dongbei daxue xuebao/journal of northeastern university': 1, 'dyes and pigments': 1, 'energy': 1,
                     'energy and environmental science': 1, 'engineer': 1, 'engineering failure analysis': 1,
                     'engineering fracture mechanics': 1, 'engineering. cornell quarterly': 1,
                     'environmental geology': 1, 'environmental science and technology': 1, 'estudios atacamenos': 1,
                     'european cells and materials': 1, 'european journal of oral sciences': 1,
                     'european polymer journal': 1, 'filtration and separation': 1, 'fiz nizk temp': 1,
                     'fizika i khimiya obrabotki materialov': 1, 'fizika nizkikh temperatur (kharkov)': 1,
                     'fizika nizkikh temperatur (kiev)': 1, 'fiziko-khimicheskaya mekhanika materialov': 1,
                     'foundry trade journal': 1, 'freiberger forschungshefte (reihe) a': 1,
                     'fusion engineering and design': 1, 'fusion science and technology': 1, 'fusion technology': 1,
                     'gaodianya jishu/high voltage engineering': 1, 'gaswaerme international': 1, 'geliotekhnika': 1,
                     'geoarchaeology - an international journal': 1,
                     'guti huojian jishu/journal of solid rocket technology': 1,
                     'huanan ligong daxue xuebao/journal of south china university of technology (natural science)': 1,
                     'huanjing kexue/environmental science': 1, 'hyperfine interactions': 1,
                     'iarc scientific publications': 1, 'ibm journal of research and development': 1,
                     'ibm technical disclosure bulletin': 1, 'iee colloquium (digest)': 1,
                     'in: proc. jsle int. tribology conf., (tokyo, japan: jul. 8-10, 1985)': 1, 'industrial heating': 1,
                     'industrial laboratory': 1, 'informacije midem': 1, 'injury': 1, 'instrum exp tech': 1,
                     'instruments and experimental techniques new york': 1, 'international applied mechanics': 1,
                     'international journal of advanced manufacturing technology': 1,
                     'international journal of fracture': 1, 'international journal of hydrogen energy': 1,
                     'international journal of impact engineering': 1,
                     'international journal of machine tools and manufacture': 1,
                     'international journal of manufacturing technology and management': 1,
                     'international journal of solids and structures': 1, 'intersecciones en antropologia': 1,
                     'inzhenerno-fizicheskii zhurnal': 1, 'inzynieria chemiczna i procesowa': 1, 'ionics': 1,
                     'isij international': 1, 'israel journal of technology': 1, 'izv akad nauk sssr neorg mater': 1,
                     'izvestiya akademii nauk. ser. fizicheskaya': 1, 'j eng power trans asme': 1,
                     'j. japan society precision engineering': 1, "jane's defence weekly": 1,
                     'jixie gongcheng xuebao/chinese journal of mechanical engineering': 1,
                     'jixie gongcheng xuebao/journal of mechanical engineering': 1,
                     'journal of adhesion science and technology': 1,
                     'journal of applied mechanics, transactions asme': 1, 'journal of applied oral science': 1,
                     'journal of applied sciences': 1, 'journal of archaeological method and theory': 1,
                     'journal of archaeological science': 1, 'journal of astm international': 1,
                     'journal of central south university of technology (english edition)': 1,
                     'journal of computational and theoretical nanoscience': 1,
                     'journal of engineering for gas turbines and power': 1,
                     'journal of failure analysis and prevention': 1, 'journal of field archaeology': 1,
                     'journal of food engineering': 1, 'journal of harbin institute of technology (new series)': 1,
                     'journal of japan society of lubrication engineers': 1,
                     'journal of manufacturing science and engineering, transactions of the asme': 1,
                     'journal of mechanical science and technology': 1, 'journal of mechanical working technology': 1,
                     'journal of membrane science': 1, 'journal of micromechanics and microengineering': 1,
                     'journal of microscopy': 1, 'journal of molecular structure': 1,
                     'journal of nanoparticle research': 1, 'journal of power sources': 1, 'journal of rare earths': 1,
                     'journal of sound and vibration': 1, 'journal of testing and evaluation': 1,
                     'journal of the acoustical society of america': 1,
                     'journal of the mechanics and physics of solids': 1, 'journal of the royal society interface': 1,
                     'journal of thermal spray technology': 1, 'journal of tribology': 1,
                     "kang t'ieh/iron and steel (peking)": 1, 'konstruktion': 1, 'kunsthandwerk und design': 1,
                     'kunststoffe international': 1, 'latin american antiquity': 1, 'le vide, les couches minces': 1,
                     'lecture notes in computer science (including subseries lecture notes in artificial intelligence and lecture notes in bioinformatics)': 1,
                     'lecture notes in electrical engineering': 1, 'liteinoe proizvodstvo': 1,
                     'litejnoe proizvodstvo': 1, 'lubrication engineering': 1, 'machine design': 1,
                     'machining science and technology': 1, 'malaysian journal of microscopy': 1, 'mcic rep 78-36': 1,
                     'measurement science and technology': 1, 'mechanics of materials': 1, 'medziagotyra': 1,
                     'metal powder report': 1, 'micron': 1,
                     'minutes of the meeting - pennsylvania electric association, engineering section': 1,
                     'mocaxue xuebao/tribology': 1, 'modern casting': 1, 'nasa technical memorandum': 1,
                     'national technical report': 1, 'natl tech rep': 1, 'natl tech rep matsushita electr ind': 1,
                     'nato science for peace and security series b: physics and biophysics': 1, 'nature': 1,
                     'nec research and development': 1, 'neorganiceskie materialy': 1,
                     'nihon kikai gakkai ronbunshu, a hen/transactions of the japan society of mechanical engineers, part a': 1,
                     'nippon hotetsu shika gakkai zasshi': 1,
                     'nippon kikai gakkai ronbunshu, a hen/transactions of the japan society of mechanical engineers, part a': 1,
                     'nippon kikai gakkai ronbunshu, b hen/transactions of the japan society of mechanical engineers, part b': 1,
                     'nippon kikai gakkai ronbunshu, c hen/transactions of the japan society of mechanical engineers, part c': 1,
                     'nippon kinzoku gakkai-si': 1, 'nippon shishubyo gakkai kaishi': 1, 'nist special publication': 1,
                     'nongye jixie xuebao/transactions of the chinese society of agricultural machinery': 1,
                     'ntisearch': 1, 'nuclear and chemical waste management': 1, 'ogneupory': 1,
                     'ogneupory i tekhnicheskaya keramika': 1, 'otolaryngologic clinics of north america': 1,
                     'plasma processes and polymers': 1, 'plasma science and technology': 1, 'pollution engineering': 1,
                     'poroshkovaya metallurgiya': 1, 'power': 1,
                     'prace naukowe instytutu budownictwa politechniki wroclawskiej': 1,
                     'praktische metallographie/practical metallography': 1, 'pribory i tekhnika eksperimenta': 1,
                     'problemy prochnosti': 1, 'proceedings - computer networking symposium': 1,
                     'proceedings of the institution of mechanical engineers, part b: journal of engineering manufacture': 1,
                     'proceedings of the national academy of sciences of the united states of america': 1,
                     'proceedings of the royal society a: mathematical, physical and engineering sciences': 1,
                     'quaternary international': 1, 'quintessence international': 1,
                     'quintessence international (berlin, germany : 1985)': 1,
                     'report of the research laboratory of engineering materials tokyo': 1, 'research disclosure': 1,
                     'review of progress in quantitative nondestructive evaluation': 1,
                     'review of scientific instruments': 1, 'revista escola de minas': 1,
                     'run hua yu mi feng/lubrication engineering': 1, 'russ cast prod': 1,
                     'russian engineering research': 1, 's t l e tribology transactions': 1, 's.a.m.p.e. quarterly': 1,
                     'sadhana': 1, 'sae (society of automotive engineers) transactions': 1, 'sae prepr': 1,
                     'sae preprints': 1, 'schweissen und schneiden/welding and cutting': 1,
                     'science in china, series e: technological sciences': 1,
                     'seimitsu kogaku kaishi/journal of the japan society for precision engineering': 1,
                     'shenyang gongye daxue xuebao/journal of shenyang university of technology': 1,
                     'shenyang jianzhu daxue xuebao (ziran kexue ban)/journal of shenyang jianzhu university (natural science)': 1,
                     'shinku/journal of the vacuum society of japan': 1, 'signature (ramsey, n.j.)': 1,
                     'solar energy': 1, 'southeastern archaeology': 1, 'sov j opt technol': 1,
                     'soviet applied mechanics': 1, 'soviet castings technology': 1,
                     'soviet castings technology (english translation of liteinoe proizvodstvo)': 1,
                     'soviet engineering research': 1, 'sprechsaal': 1, 'sprechsaal 1976': 1, 'stahl und eisen': 1,
                     "stal'": 1, 'sumitomo search': 1, 'surface and coatings technology': 1, 'surface engineering': 1,
                     'surface mount technology': 1, 'svarochnoe proizvodstvo': 1, 'talanta': 1,
                     'technical paper - society of manufacturing engineers. ad': 1,
                     'technical paper - society of manufacturing engineers. em': 1,
                     'technical paper - society of manufacturing engineers. mr': 1,
                     'theoretical and applied fracture mechanics': 1,
                     'toraibarojisuto/journal of japanese society of tribologists': 1, 'transactions of j w r i': 1,
                     'transactions of powder mettalurgy association of india': 1,
                     'transactions of the korean institute of electrical engineers': 1,
                     'transactions of the korean society of mechanical engineers, a': 1,
                     'transactions of the korean society of mechanical engineers, b': 1, 'trenie i iznos': 1,
                     'tribologie und schmierungstechnik': 1, 'tribology and interface engineering series': 1,
                     'tribology international': 1, 'tribology letters': 1, 'tribology series': 1,
                     'tribology transactions': 1, 'tyazheloe mashinostroenie': 1, 'u.s. woman engineer': 1,
                     'ukrainskii khimicheskii zhurnal': 1, 'ultramicroscopy': 1, 'vdi berichte': 1, 'vdi-z': 1,
                     'vuoto bologna': 1, 'waste management': 1, 'water research': 1, 'water science and technology': 1,
                     'wear': 1, 'werkstoffe und korrosion': 1,
                     'wuhan ligong daxue xuebao/journal of wuhan university of technology': 1,
                     'xitong gongcheng lilun yu shijian/system engineering theory and practice': 1,
                     'yi qi yi biao xue bao/chinese journal of scientific instrument': 1,
                     'yosetsu gakkai ronbunshu/quarterly journal of the japan welding society': 1, 'you qi chuyun': 1,
                     'zahn-, mund-, und kieferheilkunde mit zentralblatt': 1,
                     'zahntechnik; zeitschrift fur theorie und praxis der wissenschaftlichen zahntechnik': 1,
                     'zhejiang daxue xuebao (gongxue ban)/journal of zhejiang university (engineering science)': 1,
                     'zhendong yu chongji/journal of vibration and shock': 1,
                     'zhongguo dianji gongcheng xuebao/proceedings of the chinese society of electrical engineering': 1,
                     'zhongguo jixie gongcheng/china mechanical engineering': 1,
                     'zhongguo xitu xuebao/journal of the chinese rare earth society': 1,
                     'zhongnan daxue xuebao (ziran kexue ban)/journal of central south university (science and technology)': 1,
                     'zhurnal fizicheskoi khimii': 1, 'zhuzao/foundry': 1,
                     'zi, ziegelindustrie international/brick and tile industry international': 1, 'zwr': 1,
                     'advanced powder technology': 1, 'advanced science letters': 1, 'aiaa journal': 1, 'aiaa paper': 1,
                     'american society of mechanical engineers (paper)': 1,
                     'annals of the new york academy of sciences': 1, 'applied energy': 1,
                     'archive of applied mechanics': 1, 'asme pap': 1, 'asthetische zahnmedizin': 1,
                     'atomnaya energiya': 1, 'australian journal of basic and applied sciences': 1,
                     'aviation week and space technology (new york)': 1, 'azania': 1,
                     'beijing gongye daxue xuebao / journal of beijing university of technology': 1,
                     'beijing keji daxue xuebao/journal of university of science and technology beijing': 1,
                     'beijing ligong daxue xuebao/transaction of beijing institute of technology': 1,
                     'binggong xuebao/acta armamentarii': 1,
                     'bulletin of the academy of sciences of the u.s.s.r. physical series': 1,
                     'denshi gijutsu sogo kenkyusho iho/bulletin of the electrotechnical laboratory': 1,
                     'deutsche zahnarztliche zeitschrift': 1, 'die quintessenz': 1,
                     'funtai oyobi fummatsu yakin/journal of the japan society of powder and powder metallurgy': 1,
                     'hangkong dongli xuebao/journal of aerospace power': 1,
                     'hanjie xuebao/transactions of the china welding institution': 1,
                     'harbin gongye daxue xuebao/journal of harbin institute of technology': 1,
                     "hsi-an chiao tung ta hsueh/journal of xi'an jiaotong university": 1,
                     'huazhong keji daxue xuebao (ziran kexue ban)/journal of huazhong university of science and technology (natural science edition)': 1,
                     'progress in natural science': 1, 'przeglad elektrotechniczny': 1,
                     'qinghua daxue xuebao/journal of tsinghua university': 1, 'science': 1,
                     'science china technological sciences': 1, 'science of sintering': 1, 'scientia sinica': 1,
                     'separation and purification technology': 1, 'separation science and technology': 1,
                     'shanghai jiaotong daxue xuebao/journal of shanghai jiaotong university': 1}
phys_journal_dic = {'acs applied materials and interfaces': 1, 'acs nano': 1, 'acs symposium series': 1,
                    'applied physics a solids and surfaces': 1,
                    'applied physics a: materials science and processing': 1, 'applied physics b: lasers and optics': 1,
                    'applied physics communications': 1, 'applied physics express': 1, 'applied physics letters': 1,
                    'acta physica polonica a': 1, 'applied superconductivity': 1, 'applied thermal engineering': 1,
                    'bulletin of the russian academy of sciences: physics': 1, 'chinese physics letters': 1,
                    'current applied physics': 1, 'epj applied physics': 1, 'european physical journal b': 1,
                    'european physical journal: special topics': 1, 'europhysics letters': 1, 'ferroelectrics': 1,
                    'ferroelectrics, letters section': 1, 'high temperature science': 1,
                    'high temperatures - high pressures': 1, 'ieee antennas and wireless propagation letters': 1,
                    'ieee journal of quantum electronics': 1, 'ieee microwave and wireless components letters': 1,
                    'ieee mtt-s international microwave symposium digest': 1, 'ieee sensors journal': 1,
                    'ieee trans components hybrids manuf technol': 1, 'ieee trans parts hybrids packag': 1,
                    'ieee transactions on advanced packaging': 1, 'ieee transactions on antennas and propagation': 1,
                    'ieee transactions on applied superconductivity': 1,
                    'ieee transactions on components and packaging technologies': 1,
                    'ieee transactions on components packaging and manufacturing technology part a': 1,
                    'ieee transactions on components packaging and manufacturing technology part b': 1,
                    'ieee transactions on components, hybrids, and manufacturing technology': 1,
                    'ieee transactions on components, packaging and manufacturing technology': 1,
                    'ieee transactions on components, packaging, and manufacturing technology. part a': 1,
                    'ieee transactions on components, packaging, and manufacturing technology. part b, advanced packaging': 1,
                    'ieee transactions on dielectrics and electrical insulation': 1,
                    'ieee transactions on electrical insulation': 1, 'ieee transactions on electron devices': 1,
                    'ieee transactions on instrumentation and measurement': 1, 'ieee transactions on magnetics': 1,
                    'ieee transactions on microwave theory and techniques': 1,
                    'ieee transactions on nuclear science': 1, 'ieee transactions on plasma science': 1,
                    'ieee transactions on ultrasonics, ferroelectrics, and frequency control': 1,
                    'ieee wescon tech pap': 1, 'ieice transactions on electronics': 1,
                    'iet microwaves, antennas and propagation': 1, 'indian journal of physics': 1,
                    'indian journal of pure and applied physics': 1, 'integrated ferroelectrics': 1,
                    'international journal of heat and mass transfer': 1,
                    'international journal of microcircuits and electronic packaging': 1,
                    'international sampe electronics conference': 1, 'japanese journal of applied physics': 1,
                    'japanese journal of applied physics, part 1: regular papers & short notes': 1,
                    'japanese journal of applied physics, part 1: regular papers & short notes & review papers': 1,
                    'japanese journal of applied physics, part 1: regular papers and short notes and review papers': 1,
                    'japanese journal of applied physics, part 2: letters': 1,
                    'jee. journal of electronic engineering': 1, 'journal de physique iii': 1,
                    'journal de physique. colloque': 1, 'journal de physique. iii': 1, 'journal of applied physics': 1,
                    'journal of electronic materials': 1,
                    'journal of electronic packaging, transactions of the asme': 1, 'journal of engineering physics': 1,
                    'journal of low temperature physics': 1,
                    'journal of materials science: materials in electronics': 1, 'journal of physical chemistry b': 1,
                    'journal of physical chemistry c': 1, 'journal of physics and chemistry of solids': 1,
                    'journal of physics condensed matter': 1, 'journal of physics d: applied physics': 1,
                    'journal of physics: condensed matter': 1, 'journal of physics: conference series': 1,
                    'journal of physics. c. solid state physics': 1, 'journal of superconductivity': 1,
                    'journal of superconductivity and novel magnetism': 1, 'journal of the korean physical society': 1,
                    'laser physics': 1, 'laser physics letters': 1, 'low temperature physics': 1,
                    'microelectronic engineering': 1, 'microelectronics and reliability': 1,
                    'microelectronics reliability': 1, 'nano letters': 1, 'optics and laser technology': 1,
                    'optics and lasers in engineering': 1, 'optics communications': 1, 'optics express': 1,
                    'optics letters': 1, 'optoelectronics and advanced materials, rapid communications': 1,
                    'philosophical magazine a: physics of condensed matter, structure, defects and mechanical properties': 1,
                    'physica b: condensed matter': 1, 'physica b: physics of condensed matter': 1,
                    'physica b: physics of condensed matter & c: atomic, molecular and plasma physics, optics': 1,
                    'physica b+c': 1, 'physica c: superconductivity and its applications': 1, 'physica scripta': 1,
                    'physica status solidi - rapid research letters': 1,
                    'physica status solidi (a) applications and materials science': 1,
                    'physica status solidi (a) applied research': 1, 'physica status solidi (b) basic research': 1,
                    'physica status solidi (c) current topics in solid state physics': 1,
                    'physical chemistry chemical physics': 1, 'physical review b': 1,
                    'physical review b - condensed matter and materials physics': 1, 'physical review letters': 1,
                    'physics and chemistry of glasses': 1,
                    'physics and chemistry of glasses: european journal of glass science and technology part b': 1,
                    'physics and chemistry of materials treatment': 1, 'physics letters a': 1,
                    'physics of metals and metallography': 1, 'physics of the solid state': 1,
                    'russian journal of physical chemistry a': 1, 'sensors and actuators': 1,
                    'sensors and actuators, a: physical': 1, 'sensors and actuators: a. physical': 1,
                    'superconductor science and technology': 1, 'central european journal of physics': 1,
                    'chinese physics b': 1, 'czechoslovak journal of physics': 1, 'electronic materials letters': 1,
                    'electronic packaging and production': 1,
                    'electronics and communications in japan, part ii: electronics (english translation of denshi tsushin gakkai ronbunshi)': 1,
                    'electronics letters': 1, 'international journal of modern physics b': 1,
                    'international journal of thermophysics': 1, 'journal of applied crystallography': 1,
                    'journal of crystal growth': 1, 'journal of raman spectroscopy': 1,
                    'journal of thermal analysis': 1, 'journal of thermal analysis and calorimetry': 1, 'langmuir': 1,
                    'solid state communications': 1, 'solid state ionics': 1, 'solid state sciences': 1,
                    'solid state technology': 1, 'advancing microelectronics': 1,
                    'chinese journal of sensors and actuators': 1, 'chinese optics letters': 1,
                    'crystal research and technology': 1, 'crystallography reports': 1, 'crystengcomm': 1,
                    'defect and diffusion forum': 1, 'defektoskopiya': 1,
                    'diffusion and defect data pt.b: solid state phenomena': 1, 'electri-onics': 1, 'elektronika': 1,
                    'elektronnaya obrabotka materialov': 1,
                    'gaoya wuli xuebao/chinese journal of high pressure physics': 1,
                    'guang pu xue yu guang pu fen xi/spectroscopy and spectral analysis': 1,
                    'guangdianzi jiguang/journal of optoelectronics laser': 1,
                    'guangxue jingmi gongcheng/optics and precision engineering': 1,
                    'guangxue xuebao/acta optica sinica': 1, 'guangzi xuebao/acta photonica sinica': 1,
                    'high pressure research': 1, 'hongwai yu jiguang gongcheng/infrared and laser engineering': 1,
                    'hybrid circuit technology': 1, 'international journal of nanoscience': 1, 'j vac sci technol': 1,
                    'japanese journal of tribology': 1, 'journal of aerosol science': 1,
                    'journal of colloid and interface science': 1, 'journal of laser applications': 1,
                    'journal of luminescence': 1, 'journal of microelectronics and electronic packaging': 1,
                    'journal of microwave power and electromagnetic energy': 1, 'journal of nano research': 1,
                    'journal of nanoscience and nanotechnology': 1,
                    'journal of optical technology (a translation of opticheskii zhurnal)': 1,
                    'journal of vacuum science and technology a: vacuum, surfaces and films': 1,
                    'journal of vacuum science and technology b: microelectronics and nanometer structures': 1,
                    'microscopy and microanalysis': 1, 'microsystem technologies': 1,
                    'microwave and optical technology letters': 1, 'microwave journal': 1,
                    'modern physics letters b': 1, 'nanoscale research letters': 1, 'nanotechnology': 1,
                    'new electronics': 1, 'nuclear inst. and methods in physics research, a': 1,
                    'nuclear inst. and methods in physics research, b': 1,
                    'nuclear instruments and methods in physics research, section a: accelerators, spectrometers, detectors and associated equipment': 1,
                    'nuclear instruments and methods in physics research, section b: beam interactions with materials and atoms': 1,
                    'nuclear technology': 1, 'phase transitions': 1, 'philosophical magazine': 1,
                    'philosophical magazine letters': 1, 'photonics spectra': 1, 'proceedings of the ieee': 1,
                    'proceedings of the international microelectronics symposium': 1,
                    'progress in crystal growth and characterization of materials': 1, 'quantum electronics': 1,
                    'radiation effects and defects in solids': 1, 'radiation measurements': 1,
                    'radiation protection dosimetry': 1, 'sensors and actuators, b: chemical': 1,
                    'soviet physics - lebedev institute reports (english translation of sbornik \xe2\x80\xb3kratkie soobshcheniya po fizike\xe2\x80\xb3. an sssr. fizicheskii institut im. p.n. lebedeva)': 1,
                    'surface and interface analysis': 1, 'surface review and letters': 1, 'surface science': 1,
                    'technical physics': 1, 'technical physics letters': 1, 'teplofizika vysokikh temperatur': 1,
                    'the soviet journal of glass physics and chemistry': 1, 'thin solid films': 1,
                    'transactions on electrical and electronic materials': 1, 'ultrasonics': 1,
                    'ultrasonics symposium proceedings': 1, 'vacuum': 1, 'vibrational spectroscopy': 1,
                    'vide: science, technique et applications': 1, 'wuli xuebao/acta physica sinica': 1,
                    'x-ray spectrometry': 1, 'yadian yu shengguang/piezoelectrics and acoustooptics': 1,
                    'zeitschrift f\xc3\xbcr physik b condensed matter': 1,
                    'zeitschrift fur kristallographie, supplement': 1, 'zhongguo jiguang/chinese journal of lasers': 1,
                    'active and passive electronic components': 1, 'applied optics': 1,
                    'applied solar energy (english translation of geliotekhnika)': 1, 'applied surface science': 1,
                    'progress in nuclear energy': 1, 'qiangjiguang yu lizishu/high power laser and particle beams': 1,
                    'silicon': 1}


# Data Input
# coonvert list of keywords in txt into a list 'analyse'
analyse = []
fh = open('code/keywordList.txt', 'r')
for line in fh:
    # analyse.append(line.strip().split(',')) -- original code line
    analyse.append(line.strip())  # replaced


# reading common words list, convert the txt into a list
listOfWords = []
with open('code/CommonkeywordList.txt', 'r') as fh:
    listOfWords = fh.read()

# Do the analysis for each year
for root, dirs, files in os.walk(rootPath):  # for all files in rootpath directory
    counter = 0
    for filename in fnmatch.filter(files, pattern):
        filenameOut = filename
        filename = rootPath + filename
        year = (filenameOut[0:4])  # gets year from file name
        file_size = os.path.getsize(filename)  # get the current file size for the counter
        indata = (open(filename)).read()  # inputs the current file text into indata

    # initialize the counters for papers (stats measured for each year)
    numberOfPages = []
    numberOfPapers = 0

    # removing the DUPLICATES in the original data
    everything_list = re.findall(r'\n\@((.|\n)*?)\},\n\}\n', indata)  # divide the indata string in separate
    # recors
    print everything_list[0]
    everything_list = list(set(everything_list))  # removes duplicates from list
    total_records += len(everything_list)  # count the total number of records
    # (for all folders, not just the current year)
    everything_list = ' '.join(str(e) for e in everything_list)  # convert back to a string
    everything_list = everything_list.lower()  # convert everything lower case

    # count the NUMBER OF ABSTRACTS
    abstract_list = re.findall(r"abstract=\{(.*?)\},", everything_list)  # warning: does not capture abstracts with a
    # new line within
    count_abstract = len(abstract_list)
    length_abstract = [len(char) - 11 for char in
                       abstract_list]  # -11 because need to remove "abstract={" and "}" from the string obtained with the regex
    average_abstract_length = sum(length_abstract) / len(length_abstract)
    del abstract_list

    # count the number of RECORDS for the current year
    article_list = re.findall(r'url=\{(.*?)\},', everything_list)
    count = len(article_list)
    del article_list

    # stats on ABSTRACT LENGTH vs TITLE LENGTH
    everything_list2 = re.findall(r'\n\@((.|\n)*?)\},\n\}\n', indata)  # divide the indata string in separate records
    everything_list2 = list(set(everything_list2))  # remove the duplicate
    for item in everything_list2:
        # test if there is an abstract in the record
        item = str(item)
        if "abstract=" in item:
            # compute abstract length
            abstract = str(re.findall(r'abstract=\{(.*?)\},', item))
            length_abstract = len(abstract)
            # compute title length
            title = str(re.findall(r'\\ntitle=\{(.*?)\},', item))
            length_title_isolated = len(title)
            # compute page length
            page = re.findall(r'pages=\{(.*?)\},', item)
            page_length = 0
            for item_reduced in page:
                item_short = re.findall(r'([0-9]{1,4}){1}-([0-9]{1,4}){1}', item_reduced)
                if item_short is not '[]':
                    for pairs in item_short:
                        page_length = int(pairs[1]) - int(pairs[0])

            # sanity check for incomplete records. papers over 40 pages (by mistake or legit) are not considered
            if 40 > page_length > 0:
                page_length_array.append(page_length)
                abstract_length_array.append(length_abstract)
                title_length_array.append(length_title_isolated)

    # compute the average number of pages of papers with 'membrane' somewhere in results file
    for item in everything_list2:
        # test if there is an abstract in the record
        item = str(item)
        if "membrane" in item:
            page = re.findall(r'pages=\{(.*?)\},', item)
            for item_reduced in page:
                item_short = re.findall(r'([0-9]{1,4}){1}-([0-9]{1,4}){1}', item_reduced)
                if item_short is not '[]':
                    for pairs in item_short:
                        page_length = int(pairs[1]) - int(pairs[0])
                        # sanity check for incomplete records
                if 40 < page_length < 0:
                    numberOfPages.append(page_length)
                    numberOfPapers += 1
    del everything_list2

    # stats on the adoption of EMAIL
    email_count = 0
    correspondence_list = re.findall(r'correspondence_address=\{(.*?)\},',
                                     everything_list)  # select the correspondence adress field of the record
    for item in correspondence_list:
        email_count += item.count('email:')
    email_adoption = email_count / float(count)
    del correspondence_list

    # stats on the TITLES
    title_list = re.findall(r'title=\{(.*?)\},', everything_list)  # select the title field of the record
    title_list = list(set(title_list))  # remove duplicates in the list
    title_list = [char.replace("title={", "") for char in title_list]
    title_list = [char.replace("}", "") for char in title_list]
    count_title = len(title_list)
    length_title = [len(char) for char in title_list]
    average_title_length = sum(length_title) / len(length_title)
    del title_list

    # count the number of SOURCE TITLE
    article_only = re.findall(r'\n\@ARTICLE((.|\n)*?)\},\n\}\n', indata)  # restrict to journals, exclude proceedings
    article_only = list(set(article_only))  # remove duplicates
    article_only = ' '.join(str(e) for e in article_only)  # convert back to a string
    article_only = article_only.lower()  # lower case
    journal_list = re.findall(r'journal=\{(.*?)\},', article_only)  # select only the field with journal title

    # print "number of titles before:" + str(len(journal_list))
    myList = dict((key, len(list(group))) for key, group in groupby(sorted(journal_list)))
    short_list_journal = myList.keys()
    count_journal = len(short_list_journal)

    myList_reduced_2 = {key: value for key, value in myList.items() if value > 2}
    short_list_journal = myList_reduced_2.keys()
    count_journal_2 = len(short_list_journal)

    myList_reduced_5 = {key: value for key, value in myList.items() if value > 5}
    short_list_journal = myList_reduced_5.keys()
    count_journal_5 = len(short_list_journal)

    myList_reduced_10 = {key: value for key, value in myList.items() if value > 10}
    short_list_journal = myList_reduced_10.keys()
    count_journal_10 = len(short_list_journal)

    myList_reduced_50 = {key: value for key, value in myList.items() if value > 50}
    short_list_journal = myList_reduced_50.keys()
    count_journal_50 = len(short_list_journal)

    del myList_reduced_2, myList_reduced_5, myList_reduced_10, myList_reduced_50

    # # classification by fields
    chem_count = 0  # initialize the counters
    ceram_count = 0
    phys_count = 0
    mater_count = 0
    bio_count = 0
    other_count = 0

    for item in journal_list:
        if item in chem_journal_dic:
            chem_count += 1
        elif item in phys_journal_dic:
            phys_count += 1
        elif item in bio_journal_dic:
            bio_count += 1
        elif item in ceram_journal_dic:
            ceram_count += 1
        elif item in mater_journal_dic:
            mater_count += 1
        else:
            other_count += 1
    del journal_list

    total_count = float(chem_count + ceram_count + phys_count + mater_count + bio_count + other_count)
    bio_count = bio_count / total_count
    ceram_count = ceram_count / total_count
    chem_count = chem_count / total_count
    mater_count = mater_count / total_count
    other_count = other_count / total_count
    phys_count = phys_count / total_count

    # stats on the NUMBER of AUTHORS

    authors_list = re.findall(r'author=\{(.*?)\},', everything_list)  # select the author field
    authors_list = ' '.join(authors_list)
    # authors are enumerated using "and". If N is the number of occurences of "and", and
    # n the number of records, hen we have N + n authors for the records.
    # the average number of authors per paper is thus (N + n) / n
    author_count = authors_list.count('and')
    average_author_count = (author_count + count) / float(count)
    del authors_list

    # stats on the LENGTH OF ARTICLES
    page_list = re.findall(r'pages=\{(.*?)\},', everything_list)  # select the pages field
    total_length = 0
    # print page_list
    for item in page_list:
        item_short = re.findall(r'([0-9]{1,4}){1}-([0-9]{1,4}){1}', item)
        if item_short is not '[]':
            for pairs in item_short:
                length = int(pairs[1]) - int(pairs[0])
            if 40 < length < 0:  # sanity check
                total_length += length
    average_page_count = total_length / float(len(page_list))
    del page_list

    # stats on the NUMBER of AFFILIATIONS
    aff_list = re.findall(r'affiliation=\{(.*?)\},', everything_list)  # select the affiliation list
    aff_list = ' '.join(aff_list)
    # affiliation are separated by ";". same approach than for counting the number of authors
    aff_count = aff_list.count(';')
    average_aff_count = (aff_count + count) / float(count)
    del aff_list

    # stats on the CITATIONS
    citations_list = re.findall(r'note=\{(.*?)[\};]', everything_list)  # citation count appear in the 'note' field
    citations_list_values = [char.replace("cited by (since 1996)", "") for char in citations_list]
    citations_list_values = [char.replace(";", "") for char in citations_list_values]
    # citations_list_values = [a.replace(" ","") for a in citations_list_values]
    citations_list_values = [item.replace("cited by", "") for item in citations_list_values]
    citations_list_values = [int(char) for char in citations_list_values]

    average_citations = sum(citations_list_values) / len(citations_list_values)
    stdev_citations = sp.std(citations_list_values)
    # calculate the cumulative probability for various range
    y_50 = stats.scoreatpercentile(citations_list_values, 50)
    y_60 = stats.scoreatpercentile(citations_list_values, 60)
    y_70 = stats.scoreatpercentile(citations_list_values, 70)
    y_80 = stats.scoreatpercentile(citations_list_values, 80)
    y_90 = stats.scoreatpercentile(citations_list_values, 90)
    y_95 = stats.scoreatpercentile(citations_list_values, 95)

    average_page_count_otm = np.average(numberOfPages)
    if average_page_count_otm:
        print "Average length of OTM papers number: %s" % str(average_page_count_otm)

    # ----------------------------------------------------------- #
    # Network analysis on keywords  ###############################
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
    listOfKeywords = filter(None, listOfKeywords)  # remove empty keywords which were showing up for some reasons

    keyword_graph_string = ''
    elements = [re.findall(r'[a-z0-9]{3,}', item) for item in listOfKeywords]
    elements = [item for item in elements if len(item) > 1]
    for elem in elements:
        for x in itertools.combinations(elem, 2):
            x = str(x).replace('(', '')
            x = x.replace(')', '')
            x = x.replace("'", '')
            keyword_graph_string += x + '\n'

    keyword_graph_string = strip_accents(keyword_graph_string)
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

    # count the occurrences of each word in the list
    result = dict((key, len(list(group))) for key, group in groupby(sorted(words)))
    l = result.items()
    l.sort(key=lambda item: item[1], reverse=True)  # sort results by decreasing order

    # preparing the raw text file for the wordle, using only the most frequent words
    # remove all entries with count less than 3, so that rarely used words are not considered
    keyword_sorted = [item for item in l if item[1] > 2]
    keyword_sorted_curated = filter(lambda name: name[0] not in listOfWords,
                                    keyword_sorted)  # remove all keywords from the common words list
    wordle_list = keyword_sorted_curated[:150]  # select only the 150 most frequent words of the year
    wordle_string = ' '.join(((e[0] + ' ') * int(e[1]) ) for e in wordle_list)  # prepare the data for the wordle file

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
        keyword_results = keyword_results + year + ', ' + keywordCount + ', ' + str(
            count) + ', ' + rough_length + ', ' + str(average_abstract_length) + ', ' + str(average_title_length) + '\n'
        outFileKeywordName = dirResults + batch_keyword + '-results.csv'
        out_fileKeyword = open(outFileKeywordName, 'a+')
        out_fileKeyword.write(keyword_results)
        out_fileKeyword.close()
        keyword_results = ''

    # ----------------------------------------------------------- #
    # WRITE all the results in the various files
    # ----------------------------------------------------------- #

    outFileName = dirResults + filenameOut + '-results.txt'
    with open(outFileName, 'w') as of:
        for t in keyword_sorted_curated:
            of.write(','.join(str(s) for s in t) + '\n')  # write the count for all words found in data file

    outFileName = dirResults + 'stats-citations.txt'
    with open(outFileName, 'a+') as of:
        of.write(year
                 + ',' + str(average_citations)
                 + ',' + str(stdev_citations)
                 + ',' + str(y_50)
                 + ',' + str(y_60)
                 + ',' + str(y_70)
                 + ',' + str(y_80)
                 + ',' + str(y_90)
                 + ',' + str(y_95)
                 + '\n')

    outFileName = dirResults + 'journal-citations.txt'
    with open(outFileName, 'a+') as of:
        of.write(year + ',' + str(count_journal)
                 + ',' + str(count_journal_2)
                 + ',' + str(count_journal_5)
                 + ',' + str(count_journal_10)
                 + ',' + str(count_journal_50)
                 + '\n')

    outFileName = dirResults + 'email-adoption.txt'
    with open(outFileName, 'a+') as of:
        of.write(year + ',' + str(email_adoption) + '\n')

    outFileName = dirResults + 'page_count.txt'
    with open(outFileName, 'a+') as of:
        of.write(year + ',' + str(average_page_count) + '\n')

    outFileName = dirResults + 'authors-statistics.txt'
    with open(outFileName, 'a+') as of:
        of.write(year
                 + ',' + str(average_author_count)
                 + ',' + str(average_aff_count)
                 + '\n')

    outFileName = dirResults + 'field-statistics.txt'
    with open(outFileName, 'a+') as of:
        of.write(year
                 + ',' + str(chem_count)
                 + ',' + str(ceram_count)
                 + ',' + str(phys_count)
                 + ',' + str(mater_count)
                 + ',' + str(bio_count)
                 + ',' + str(other_count)
                 + '\n')

    outFileName = dirResults + 'journal-list.txt'
    with open(outFileName, 'a+') as of:
        for item in short_list_journal:
            of.write(item + '\n')

    outFileName = dirResults + 'citations-list.txt'
    with open(outFileName, 'a+') as of:
        for item in citations_list_values:
            of.write(year + ',' + str(item) + '\n')

    outFileName = dirResults + 'records.txt'
    with open(outFileName, 'a+') as of:
        of.write(year + ',' + str(count) + '\n')

    outFileName = dirResults + 'superconpaper-length.txt'
    with open(outFileName, 'a+') as of:
        if math.isnan(average_page_count_otm):
            average_page_count_otm = 0          # check if is NaN
        of.write(year + ',' + str(average_page_count_otm) + ',' + str(numberOfPapers) + '\n')

    outFileName = dirResults + 'keywords_graphe.csv'
    with open(outFileName, 'a+') as of:
        of.write(keyword_graph_string)


    # progress bar
    counter += file_size
    time_used = time.time() - start_time
    time_increment = time_used / float(counter)
    time_left = (directory_size - counter) * time_increment
    os.system('clear')
    # print pb(int(counter/float(directory_size)*100), year, time_left)

print "Total number of records: %s" % str(total_records)
average_page_count_otm = np.average(numberOfPages)
print "Average length of OTM papers number: %s" % str(average_page_count_otm)

# Save the length of titles, abstract and page length arrays to files
outFileName = dirResults + 'array_title.txt'
with open(outFileName, 'a+') as of:
    for item in title_length_array:
        of.write(str(item) + '\n')

outFileName = dirResults + 'array_abstract.txt'
with open(outFileName, 'a+') as of:
    for item in abstract_length_array:
        of.write("%s\n" % str(item))

outFileName = dirResults + 'array_page.txt'
with open(outFileName, 'a+') as of:
    for item in page_length_array:
        of.write("%s\n" % str(item))

# Master plot AUTHORS, CITATIONS, etc.. with multiple panels
# Abstract and title length

plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(3, 3))

sub1 = plt.subplot(111)

sub1.set_ylabel('Length [norm.]')
sub1.axes.set_ylim(top=1.8, bottom=0.8)
sub1.axes.set_xlim(right=2013, left=1970)
sub1.set_yticks([1, 1.2, 1.4, 1.6, 1.8])
sub1.xaxis.set_major_locator(MaxNLocator(5))
sub1.yaxis.grid(True, linestyle='-', linewidth=axes_lw, color=axes_color)

for loc, spine in sub1.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)
plt.text(1996, 1, 'Title', color='k')  # , bbox=bbox_props)
plt.text(1980, 1.6, 'Abstract', color='k', bbox=bbox_props)

for t in analyse:
    t = t[0]
    outFileCSV = dirResults + t + '-results.csv'
    result = genfromtxt(outFileCSV, delimiter=',')
    valeurYear = [x[0] for x in result]
    valeur_abstract_length = [x[4] for x in result]
    ref_valeur_abstract = valeur_abstract_length[0]
    valeur_title_length = [x[5] for x in result]
    ref_valeur_title = valeur_title_length[0]

plt.plot(valeurYear, valeur_abstract_length / ref_valeur_abstract, color='k')
plt.plot(valeurYear, valeur_title_length / ref_valeur_title, color='k')
plt.fill_between(valeurYear, valeur_abstract_length / ref_valeur_abstract, color='b', alpha='0.2')
plt.fill_between(valeurYear, valeur_title_length / ref_valeur_title, color='g', alpha='0.2')

fig_name = 'figure 1a.png'
plt.savefig(fig_name, dpi=dpi_fig)

# Number of journals
plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(3, 3))
sub2 = plt.subplot(111)
plt.ylabel('Number of journals')
minorLocator = MultipleLocator(100)
sub2.yaxis.set_minor_locator(minorLocator)
sub2.xaxis.set_major_locator(MaxNLocator(5))
sub2.set_yticks([500, 1000, 1500])
sub2.axes.set_xlim(right=2013, left=1970)
sub2.axes.set_ylim(top=1850, bottom=0)
sub2.yaxis.grid(True, linestyle='-', linewidth=axes_lw, color=axes_color)

for loc, spine in sub2.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)

plt.text(2012, 1750, '1', color='k')
plt.text(2012, 600, '2', color='k')
plt.text(2012, 260, '5', color='k')
plt.text(2012, 100, '10', color='k')
# plt.text(1975, 1500, 'Journals', color='k', bbox=bbox_props)

outFileCSV = dirResults + 'journal-citations.txt'
result = genfromtxt(outFileCSV, delimiter=',')
valeurYear = [x[0] for x in result]
journal_count = [x[1] for x in result]
journal_count_2 = [x[2] for x in result]
journal_count_5 = [x[3] for x in result]
journal_count_10 = [x[4] for x in result]
journal_count_50 = [x[5] for x in result]

plt.plot(valeurYear, journal_count, color='k')
plt.fill_between(valeurYear, journal_count, color='b', alpha='0.2')
plt.plot(valeurYear, journal_count_2, color='k')
plt.fill_between(valeurYear, journal_count_2, color='b', alpha='0.2')
plt.plot(valeurYear, journal_count_5, color='k')
plt.fill_between(valeurYear, journal_count_5, color='b', alpha='0.2')
plt.plot(valeurYear, journal_count_10, color='k')
plt.fill_between(valeurYear, journal_count_10, color='b', alpha='0.2')

fig_name = 'figure 1b.png'
plt.savefig(fig_name, dpi=dpi_fig)

# Authors and affiliations
plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(3, 3))

sub3 = plt.subplot(111)
plt.ylabel('Number of authors or affiliations')
minorLocator = MultipleLocator(0.2)
sub3.yaxis.set_minor_locator(minorLocator)
sub3.axes.set_ylim(top=4.5, bottom=0.9)
sub3.set_yticks([1, 2, 3, 4])
sub3.axes.set_xlim(right=2013, left=1970)
sub3.xaxis.set_major_locator(MaxNLocator(5))
sub3.yaxis.grid(True, linestyle='-', linewidth=axes_lw, color=axes_color)

for loc, spine in sub3.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)

plt.text(1983.3, 3.7, 'Authors', color='k', bbox=bbox_props)
plt.text(1975, 1.5, 'Affiliations', color='k')  #, bbox=bbox_props)

outFileCSV = dirResults + 'authors-statistics.txt'
result = genfromtxt(outFileCSV, delimiter=',')
valeurYear = [x[0] for x in result]
avg_authors_count = [x[1] for x in result]
avg_aff_count = [x[2] for x in result]

plt.plot(valeurYear, avg_authors_count, color='k')
plt.fill_between(valeurYear, avg_authors_count, color='b', alpha='0.2')
plt.plot(valeurYear, avg_aff_count, color='k')
plt.fill_between(valeurYear, avg_aff_count, color='g', alpha='0.2')

fig_name = 'figure 1c.png'
plt.savefig(fig_name, dpi=dpi_fig)

# Records
# plot the statistics of RECORDS ---------------------------------
plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(3, 3))

sub7 = plt.subplot(111)
plt.ylabel('Number of records', multialignment='center')
minorLocator = MultipleLocator(1000)
sub7.yaxis.set_minor_locator(minorLocator)
sub7.axes.set_xlim(left=1970, right=2013)
sub7.axes.set_ylim(bottom=0, top=100)
sub7.xaxis.set_major_locator(MaxNLocator(5))
sub7.set_yticks([5000, 10000, 15000])
sub7.yaxis.grid(True, linestyle='-', linewidth=axes_lw, color=axes_color)

plt.tight_layout()

for loc, spine in sub7.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)

# plt.text(1975, 12000, 'Records', color='k', bbox=bbox_props, multialignment='center')

outFileCSV = dirResults + 'records.txt'
result = genfromtxt(outFileCSV, delimiter=',')
valeurYear = [x[0] for x in result]
count = [x[1] for x in result]

plt.plot(valeurYear, count, color='k')
plt.fill_between(valeurYear, count, color='b', alpha='0.2')
fig_name = 'figure 1d.png'
plt.savefig(fig_name, dpi=dpi_fig)

# Length of articles
# plot the statistics of LENGTH OF ARTICLES -------------------------
plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(3, 3))

sub8 = plt.subplot(111)
plt.ylabel('Number of pages', multialignment='center')
minorLocator = MultipleLocator(0.2)
sub8.yaxis.set_minor_locator(minorLocator)
sub8.axes.set_xlim(left=1970, right=2013)
sub8.axes.set_ylim(bottom=3, top=6.5)
sub8.set_yticks([4, 5, 6])
sub8.xaxis.set_major_locator(MaxNLocator(5))
sub8.yaxis.grid(True, linestyle='-', linewidth=axes_lw, color=axes_color)

plt.tight_layout()

for loc, spine in sub8.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)

# plt.text(1985, 3.5, 'Pages count', color='k', bbox=bbox_props, multialignment='center')

outFileCSV = dirResults + 'page_count.txt'
result = genfromtxt(outFileCSV, delimiter=',')
valeurYear = [x[0] for x in result]
count = [x[1] for x in result]

plt.plot(valeurYear, count, color='k')
plt.fill_between(valeurYear, count, color='b', alpha='0.2')
fig_name = 'figure 1e.png'
plt.savefig(fig_name, dpi=dpi_fig)

# Email adoption

plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(3, 3))

sub4 = plt.subplot(111)
plt.ylabel('Fraction [%]', multialignment='center')
sub4.axes.set_xlim(left=1990, right=2013)
sub4.axes.set_ylim(bottom=0, top=100)
sub4.xaxis.set_major_locator(MaxNLocator(3))
sub4.set_yticks([25, 50, 75, 100])
minorLocator = MultipleLocator(1)
sub4.xaxis.set_minor_locator(minorLocator)
sub4.yaxis.grid(True, linestyle='-', linewidth=axes_lw, color=axes_color)
plt.subplots_adjust(right=0.95)

for loc, spine in sub4.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)

outFileCSV = dirResults + 'email-adoption.txt'
result = genfromtxt(outFileCSV, delimiter=',')
valeurYear = [x[0] for x in result]
email_count = [x[1] * 100 for x in result]

plt.plot(valeurYear, email_count, color='k')
plt.fill_between(valeurYear, email_count, color='b', alpha='0.2')
fig_name = 'figure 1f.png'
plt.savefig(fig_name, dpi=dpi_fig)

# Citations

# plot the statistics of CITATIONS ------------------------
plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(3, 3))

sub6 = plt.subplot(111)
sub6.set_ylabel('Number of citations since 1996')
sub6.yaxis.tick_right()
sub6.yaxis.set_label_position("right")
sub6.axes.set_ylim(bottom=0, top=60)
sub6.axes.set_xlim(left=1996, right=2013)
sub6.xaxis.set_major_locator(MaxNLocator(4))
minorLocator = MultipleLocator(1)
sub6.xaxis.set_minor_locator(minorLocator)
sub6.yaxis.grid(True, linestyle='-', linewidth=axes_lw, color=axes_color)

for loc, spine in sub6.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)
#plt.subplots_adjust(bottom=0.03, right=0.9)

plt.text(1993, 0, '50%', color='k')
plt.text(1993, 5, '60%', color='k')
plt.text(1993, 10, '70%', color='k')
plt.text(1993, 15, '80%', color='k')
plt.text(1993, 28, '90%', color='k')
plt.text(1993, 48, '95%', color='k')

# plt.text(2003.5, 45, 'Citations\nsince 1996', color='k', bbox=bbox_props, multialignment='center')

outFileCSV = dirResults + 'stats-citations.txt'
result = genfromtxt(outFileCSV, delimiter=',')
valeurYear = [x[0] for x in result]
valeur_citations = [x[1] for x in result]
std_dev = [x[2] for x in result]
lim_50 = [x[3] for x in result]
lim_60 = [x[4] for x in result]
lim_70 = [x[5] for x in result]
lim_80 = [x[6] for x in result]
lim_90 = [x[7] for x in result]
lim_95 = [x[8] for x in result]

sub6.plot(valeurYear, lim_50, label='50%', color='k')
sub6.fill_between(valeurYear, 0, lim_50, alpha=0.2)
sub6.plot(valeurYear, lim_60, label='60%', color='k')
sub6.fill_between(valeurYear, 0, lim_60, alpha=0.2)
sub6.plot(valeurYear, lim_70, label='70%', color='k')
sub6.fill_between(valeurYear, 0, lim_70, alpha=0.2)
sub6.plot(valeurYear, lim_80, label='80%', color='k')
sub6.fill_between(valeurYear, 0, lim_80, alpha=0.2)
sub6.plot(valeurYear, lim_90, label='90%', color='k')
sub6.fill_between(valeurYear, 0, lim_90, alpha=0.2)
sub6.plot(valeurYear, lim_95, label='95%', color='k')
sub6.fill_between(valeurYear, 0, lim_95, alpha=0.2)
fig_name = 'figure 1g.png'
plt.savefig(fig_name, dpi=dpi_fig)

# Repartition between fields
# plot the statistics of REPARTITION BETWEEN FIELDS ----------
plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(3, 3))

sub5 = plt.subplot(111)
plt.ylabel('Fraction [%]')
sub5.axes.set_xlim(left=1970, right=2013)
sub5.axes.set_ylim(top=100, bottom=0)
sub5.xaxis.set_major_locator(MaxNLocator(5))

for loc, spine in sub5.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)

plt.text(2014, 1, 'L&H', color='k', bbox=bbox_props)
plt.text(2014, 34, 'Chemistry', color='k', bbox=bbox_props)
plt.text(2014, 66, 'Physics', color='k', bbox=bbox_props)
plt.text(2014, 18, 'Ceramic', color='k', bbox=bbox_props)
plt.text(2014, 49, 'Materials', color='k', bbox=bbox_props)
plt.text(2014, 85, 'Other', color='k', bbox=bbox_props)

set_fontsize(plt, plot_font_size)

outFileCSV = dirResults + 'field-statistics.txt'
result = genfromtxt(outFileCSV, delimiter=',')
valeurYear = [x[0] for x in result]
bio_count = [x[5] * 100 for x in result]  #bio = 5
ceram_count = [(x[2] + x[5]) * 100 for x in result]  #ceram = 2
chem_count = [(x[1] + x[5] + x[2]) * 100 for x in result]  # chem = 1
mater_count = [(x[4] + x[2] + x[1] + x[5]) * 100 for x in result]  # mater  = 4
phys_count = [(x[3] + x[1] + x[5] + x[2] + x[4]) * 100 for x in result]  # phys = 3
other_count = [(x[6] + x[4] + x[2] + x[3] + x[1] + x[5]) * 100 for x in result]  # other = 6

plt.plot(valeurYear, bio_count, label='Life and health science', color='k')
plt.plot(valeurYear, chem_count, label='Chemistry', color='k')
plt.plot(valeurYear, phys_count, label='Physics', color='k')
plt.plot(valeurYear, ceram_count, label='Ceramic science', color='k')
plt.plot(valeurYear, mater_count, label='Materials science', color='k')
plt.plot(valeurYear, other_count, label='Other', color='k')

plt.fill_between(valeurYear, 0, bio_count, color='k', alpha='0.2')
plt.fill_between(valeurYear, bio_count, ceram_count, color='y', alpha='0.2')
plt.fill_between(valeurYear, ceram_count, chem_count, color='g', alpha='0.2')
plt.fill_between(valeurYear, chem_count, mater_count, color='b', alpha='0.2')
plt.fill_between(valeurYear, mater_count, phys_count, color='r', alpha='0.2')
plt.fill_between(valeurYear, phys_count, other_count, color='w', alpha='0.2')
plt.subplots_adjust(bottom=0.03, right=0.9)

sub1.tick_params(which='minor', color=axes_color, width=axes_lw)
sub2.tick_params(which='minor', color=axes_color, width=axes_lw)
sub3.tick_params(which='minor', color=axes_color, width=axes_lw)
sub4.tick_params(which='minor', color=axes_color, width=axes_lw)
sub5.tick_params(which='minor', color=axes_color, width=axes_lw)
sub6.tick_params(which='minor', color=axes_color, width=axes_lw)
sub7.tick_params(which='minor', color=axes_color, width=axes_lw)
sub8.tick_params(which='minor', color=axes_color, width=axes_lw)

sub1.tick_params(which='major', color=axes_color, width=axes_lw)
sub2.tick_params(which='major', color=axes_color, width=axes_lw)
sub3.tick_params(which='major', color=axes_color, width=axes_lw)
sub4.tick_params(which='major', color=axes_color, width=axes_lw)
sub5.tick_params(which='major', color=axes_color, width=axes_lw)
sub6.tick_params(which='major', color=axes_color, width=axes_lw)
sub7.tick_params(which='major', color=axes_color, width=axes_lw)
sub8.tick_params(which='major', color=axes_color, width=axes_lw)

fig_name = 'figure 1h.png'
plt.savefig(fig_name, dpi=dpi_fig)

# Second master plot, with the KEYWORDS results

number_of_keywords = len(analyse)
gs = gridspec.GridSpec(number_of_keywords / 4 + 2, 4)

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
    valeurY = [(x[1] / x[3] * valeur_ref) for x in result]
    max_valeurYear = max(valeurY)
    acolor = next(color)
    sub1.plot(valeurYear, valeurY, next(linecycler), lw=next(lwcycler), color=acolor, label=t, alpha=1)
    sub3 = plt.subplot(gs[(i / 4) + 2, i % 4])
    sub3.set_title(t, fontsize=9)
    sub3.xaxis.set_major_locator(majorLocator)
    sub3.axes.set_xlim(right=2013, left=1970)
    [label.set_visible(False) for label in sub3.get_xticklabels()]
    sub3.set_yticks([])
    sub3.xaxis.set_minor_locator(minorLocator)
    sub3.axhline(linewidth=axes_lw, color=axes_color)
    sub3.axvline(linewidth=axes_lw, color=axes_color)
    sub3.spines['top'].set_visible(False)
    sub3.spines['right'].set_visible(False)
    sub3.spines['left'].set_visible(False)
    sub3.spines['bottom'].set_visible(False)
    sub3.plot(valeurYear, valeurY / max_valeurYear, label=t, alpha=1, lw=1)
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
leg = sub1.legend(handles2, labels2, bbox_to_anchor=(0.96, 0.5), loc='center left', prop={'size': 9}, handlelength=1.3,
                  handletextpad=0.5)
leg.get_frame().set_alpha(0)  # this will make the box totally transparent
leg.get_frame().set_edgecolor('white')  # this will make the edges of the border white

set_fontsize(plt, plot_font_size)

plt.tight_layout()

fig_name = 'figure keyword.png'
plt.savefig(fig_name, dpi=dpi_fig)

# Plot with abstract and title length, page count
plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(7, 2))

cmap = get_cmap('jet', 10)

# plot ABSTRACT vs TITLE LENGTH
sub1 = plt.subplot(131)
sub1.set_title('A')
sub1.set_ylabel('Abstract [char.]')
sub1.set_xlabel('Title [char.]')
sub1.axes.set_ylim(bottom=0, top=2500)
sub1.axes.set_xlim(right=250)
sub1.xaxis.set_major_locator(MaxNLocator(5))
set_fontsize(plt, 10)

dirResults = './' + 'resultsCeramicomics/'
outFileCSV = dirResults + 'array_title.txt'
title_length = genfromtxt(outFileCSV)
outFileCSV = dirResults + 'array_abstract.txt'
abstract_length = genfromtxt(outFileCSV)

H, xedges, yedges = histogram2d(abstract_length, title_length, range=[[0., 2500.0], [0., 250.0]], bins=(25, 25))
extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
sub1.imshow(H, extent=extent, origin='lower', aspect='auto', interpolation='bicubic')
levels = ( 3.0e3, 1.0e3, 500, 1.0e2, 2.0e1)
cset1 = plt.contour(H, levels, origin='lower', colors=['0.18', '0.72', '0.84', '0.97', '1'], linewidths=(0.4),
                    extent=extent)
for c in cset1.collections:
    c.set_linestyle('solid')
cmap = get_cmap('jet', 10)

# plot ABSTRACT vs PAGES
sub2 = plt.subplot(132)
sub2.set_title('B')
sub2.set_ylabel('Abstract [char.]')
sub2.set_xlabel('Pages')
sub2.axes.set_ylim(bottom=0, top=2500)
sub2.axes.set_xlim(right=25)
sub2.xaxis.set_major_locator(MaxNLocator(5))

outFileCSV = dirResults + 'array_page.txt'
page_length = genfromtxt(outFileCSV)
H, xedges, yedges = histogram2d(abstract_length, page_length, range=[[0., 2500.0], [0., 25.0]], bins=(25, 25))
extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]

sub2.imshow(H, extent=extent, origin='lower', aspect='auto', interpolation='bicubic')
levels = (3.0e3, 1.0e3, 500, 1.0e2, 2.0e1)
cset2 = plt.contour(H, levels, origin='lower', colors=['0.18', '0.82', '0.91', '0.98', '1'], linewidths=(0.4),
                    extent=extent)
set_fontsize(plt, plot_font_size)
for c in cset2.collections:
    c.set_linestyle('solid')

# plot TITLE LENGTH vs PAGES
sub3 = plt.subplot(133)
sub3.set_title('C')
sub3.set_ylabel('Title [char.]')
sub3.set_xlabel('Pages')
sub3.axes.set_ylim(bottom=0, top=250)
sub3.axes.set_xlim(right=25)
sub3.xaxis.set_major_locator(MaxNLocator(5))

H, xedges, yedges = histogram2d(title_length, page_length, range=[[0., 250.0], [0., 25.0]], bins=(25, 25))
extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
sub3.imshow(H, extent=extent, origin='lower', aspect='auto', interpolation='bicubic')
levels = (3.0e3, 1.0e3, 500, 1.0e2, 2.0e1)
cset3 = plt.contour(H, levels, origin='lower', colors=['0.18', '0.82', '0.91', '0.98', '1'], linewidths=(0.4),
                    extent=extent)
set_fontsize(plt, plot_font_size)
for c in cset3.collections:
    c.set_linestyle('solid')

# adjust the font size of the labels of the contour plot
sub1.clabel(cset1, inline=1, fontsize=8, fmt='%1.0i', zorder=2)
sub2.clabel(cset2, inline=1, fontsize=8, fmt='%1.0i', zorder=2)
sub3.clabel(cset3, inline=1, fontsize=8, fmt='%1.0i', zorder=2)

for loc, spine in sub1.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)

for loc, spine in sub2.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)

for loc, spine in sub3.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)

sub1.tick_params(which='minor', color=axes_color, width=axes_lw)
sub2.tick_params(which='minor', color=axes_color, width=axes_lw)
sub3.tick_params(which='minor', color=axes_color, width=axes_lw)

sub1.tick_params(which='major', color=axes_color, width=axes_lw)
sub2.tick_params(which='major', color=axes_color, width=axes_lw)
sub3.tick_params(which='major', color=axes_color, width=axes_lw)

plt.tight_layout()

fig_name = 'figure abstract page length.png'
plt.savefig(fig_name, dpi=dpi_fig)

# Plot of length of superconductivity papers
plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(5, 5))

sub1 = plt.subplot(111)
# plt.title('A')
sub1.set_ylabel('Paper Length [norm.]')
# sub1.axes.set_ylim(bottom=0)
sub1.axes.set_xlim(right=1999, left=1982)
sub1.set_ylim(top=7, bottom=0)
sub1.xaxis.set_major_locator(MaxNLocator(5))
sub1.yaxis.grid(True, linestyle='-', linewidth=axes_lw, color=axes_color)
ax2 = sub1.twinx()
ax2.axes.set_xlim(right=1999, left=1982)
ax2.set_ylim(top=500, bottom=0)

for loc, spine in sub1.spines.iteritems():
    spine.set_lw(axes_lw)
    spine.set_color(axes_color)
# plt.text(1996, 1, 'Title', color='k', bbox=bbox_props)

for t in analyse:
    t = t[0]
    outFileCSV = dirResults + 'superconpaper-length.txt'
    result = genfromtxt(outFileCSV, delimiter=',')
    valeurYear = [x[0] for x in result]
    length_superconpaper = [x[1] for x in result]
    number = [x[2] for x in result]

sub1.plot(valeurYear, length_superconpaper, color='k')
sub1.fill_between(valeurYear, length_superconpaper, color='b', alpha='0.2')
ax2.plot(valeurYear, number, color='k')
ax2.fill_between(valeurYear, number, color='g', alpha='0.2')

set_fontsize(plt, plot_font_size)

fig_name = 'figure supercon page length.png'
plt.savefig(fig_name, dpi=dpi_fig)
