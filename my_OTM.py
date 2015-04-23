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


def set_fontsize(fig,fontsize):
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
    plt.rcParams['figure.figsize'] = (3,3)
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
    plt.rcParams['grid.color']='white'
    plt.rcParams['grid.linestyle'] = '-'
    plt.rcParams['grid.linewidth'] = '0.1'
    plt.rcParams['axes.axisbelow'] = True
    plt.rcParams['lines.markersize']= 2.3
    plt.rcParams['lines.markeredgewidth']= '0.1'
    plt.rcParams['lines.color']= 'r'
    # plt.rcParams['lines.marker']= 'o'
    plt.rcParams['lines.linestyle']= ''
    plt.rcParams['xtick.color']= '0'
    plt.rcParams['ytick.color']= '0'
    plt.rcParams['axes.color_cycle']= ['#3778bf', '#feb308', '#a8a495', '#7bb274', '#825f87']
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['right'].set_visible('False')
    plt.gca().spines['top'].set_visible('False')
    plt.gca().spines['top'].set_color('none')
    plt.gca().xaxis.set_ticks_position('bottom')
    plt.gca().yaxis.set_ticks_position('left')
    plt.rcParams['ytick.minor.size']= 1.5
    plt.rcParams['ytick.major.width']= perso_linewidth
    plt.rcParams['ytick.minor.width']= perso_linewidth
    plt.rcParams['xtick.major.width']= perso_linewidth
    plt.rcParams['xtick.minor.width']= perso_linewidth
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

# defining the relevant fields for the different journals
bio_journal_dic = {"acta biomaterialia":1, "acta chirurgiae orthopaedicae et traumatologiae cechoslovaca":1, "acta odontologica scandinavica":1, "acta orthopaedica":1, "actualites odonto-stomatologiques":1, "american journal of dentistry":1, "american journal of orthodontics and dentofacial orthopedics":1, "american journal of orthodontics and dentofacial orthopedics : official publication of the american association of orthodontists, its constituent societies, and the american board of orthodontics":1, "american journal of otology":1, "analytical and bioanalytical chemistry":1, "angle orthodontist":1, "annals of occupational hygiene":1, "australian dental journal":1, "biomaterials":1, "biomaterials medical devices and artificial organs":1, "biomedical materials":1, "biomedical sciences instrumentation":1, "biomedizinische technik":1, "bone":1, "chinese journal of clinical rehabilitation":1, "clinical materials":1, "clinical oral implants research":1, "clinical oral investigations":1, "clinical orthopaedics and related research":1, "current opinion in dentistry":1, "das dental-labor. le laboratoire dentaire. the dental laboratory":1, "dental clinics of north america":1, "dental materials":1, "dental materials journal":1, "dentistry today":1, "deutsche stomatologie (berlin, germany : 1990)":1, "egyptian dental journal":1, "environmental health perspectives":1, "european journal of dentistry":1, "european journal of orthopaedic surgery and traumatology":1, "european spine journal":1, "general dentistry":1, "hiroshima daigaku shigaku zasshi. the journal of hiroshima university dental society":1, "hua xi kou qiang yi xue za zhi \= huaxi kouqiang yixue zazhi \= west china journal of stomatology":1, "indian journal of dental research":1, "international endodontic journal":1, "international journal of oral and maxillofacial implants":1, "international journal of prosthodontics":1, "international orthopaedics":1, "journal of adhesive dentistry":1, "journal of arthroplasty":1, "journal of biomedical materials research":1, "journal of biomedical materials research - part a":1, "journal of biomedical materials research - part b applied biomaterials":1, "journal of bone and joint surgery - series a":1, "journal of bone and joint surgery - series b":1, "journal of clinical rehabilitative tissue engineering research":1, "journal of dental research":1, "journal of dental technology : the peer-reviewed publication of the national association of dental laboratories":1, "journal of dentistry":1, "journal of esthetic and restorative dentistry":1, "journal of esthetic and restorative dentistry : official publication of the american academy of esthetic dentistry . [et al.]":1, "journal of esthetic dentistry":1, "journal of esthetic dentistry (canada)":1, "journal of fermentation and bioengineering":1, "journal of occupational health and safety - australia and new zealand":1, "journal of oral and maxillofacial surgery":1, "journal of oral rehabilitation":1, "journal of orthopaedic research":1, "journal of prosthetic dentistry":1, "journal of prosthodontic research":1, "journal of prosthodontics":1, "journal of the american dental association":1, "journal of the japanese orthopaedic association":1, "journal of the mechanical behavior of biomedical materials":1, "medicina oral, patologia oral y cirugia bucal":1, "orthopaedics and traumatology: surgery and research":1, "orthopedics":1, "practical periodontics and aesthetic dentistry : ppad":1, "practical procedures & aesthetic dentistry : ppad":1, "practical procedures & aesthetic dentistry : ppad.":1, "proceedings of the institution of mechanical engineers, part h: journal of engineering in medicine":1, "shika zairyo, kikai \= journal of the japanese society for dental materials and devices":1, "shikai tenbo \= dental outlook":1, "spine":1, "spine journal":1, "stomatologie der ddr":1, "stomatologiia":1, "stomatologiya":1, "the european journal of esthetic dentistry : official journal of the european academy of esthetic dentistry":1, "the international journal of oral & maxillofacial implants":1, "the international journal of prosthodontics":1, "the journal of adhesive dentistry":1, "the journal of prosthetic dentistry":1, "tissue engineering":1, "tissue engineering - part a":1, "zhonghua kou qiang yi xue za zhi \= zhonghua kouqiang yixue zazhi \= chinese journal of stomatology":1, "zhonghua kou qiang yi xue za zhi \= zhonghua kouqiang yixue zazhi \= chinese journal of stomatology.":1, "international journal of computerized dentistry":1, "journal of biomaterials applications":1, "journal of materials science: materials in medicine":1, "lasers in medical science":1, "operative dentistry":1, "seminars in arthroplasty":1, "trends in biomaterials and artificial organs":1, "les cahiers de prothese":1, "journal of contemporary dental practice":1, "archives of orthopaedic and trauma surgery":1, "attualita dentale":1, "compendium of continuing education in dentistry (jamesburg, n.j. : 1995)":1, "hotetsu rinsho. practice in prosthodontics":1, 'l" information dentaire':1, "quintessence of dental technology":1,  "spectrochimica acta - part a: molecular and biomolecular spectroscopy":1, "the medical journal of malaysia":1, "zeitschrift fur orthopadie und ihre grenzgebiete":1}
ceram_journal_dic = {"advances in applied ceramics": 1, "am ceram soc bull": 1, "ber deut keram gesell": 1, "ber dtsch keram ges": 1, "boletin de la sociedad espanola de ceramica y vidrio": 1, "british ceramic transactions": 1, "british ceramic. transactions and journal": 1, "bull soc fr ceram": 1, "bulletin de la societe francaise de ceramique": 1, "canadian ceramics": 1, "canadian ceramics quarterly": 1, "ceram age": 1, "ceramic transactions": 1, "ceramica": 1, "ceramics - art and perception": 1, "ceramics - silikaty": 1, "ceramics - technical": 1, "ceramics international": 1, "ceramurgia": 1, "ceramurgia international": 1, "cfi ceramic forum international": 1, "fract in ceram mater": 1, "fract mech of ceram": 1, "glass and ceramics": 1, "glass and ceramics (english translation of steklo i keramika)": 1, "in: technology of glass, ceramic, or glass, ceramic to metal sealing, presented at asme winter annual meeting, (boston, u.s.a": 1, "industrial ceramics": 1, "industrie ceramique and verriere": 1, "industrie ceramique et verriere": 1, "interceram: international ceramic review": 1, "international journal of applied ceramic technology": 1, "international journal of high technology ceramics": 1, "j am ceram soc": 1, "j cer soc jap": 1, "j ceram soc jpn": 1, "j. american ceramic society": 1, "journal of ceramic processing research": 1, "journal of the american ceramic society": 1, "journal of the australasian ceramic society": 1, "journal of the australian ceramic society": 1, "journal of the canadian ceramic society": 1, "journal of the ceramic society of japan. international ed.": 1, "journal of the european ceramic society": 1, "journal of the korean ceramic society": 1, "keramische zeitschrift": 1, "kuei suan jen hsueh pao/ journal of the chinese ceramic society": 1, "kuei suan jen hsueh pao/journal of the chinese ceramic society": 1, "proc br ceram soc": 1, "proc brit ceram soc (mechanical properties of ceramics)": 1, "proceedings - australian ceramic conference": 1, "proceedings of the british ceramic society": 1, "refractories": 1, "refractories (english translation of ogneupory)": 1, "refractories and industrial ceramics": 1, "sci of ceram, conf, 7th int, proc, pap, juan-les-pins, fr, sep 24-26 1973": 1, "silicates industriels": 1, "trans j brit cer soc": 1, "trans j brit ceram soc": 1, "transactions and journal of the british ceramic society": 1, "transactions of the indian ceramic society": 1, "american ceramic society bulletin": 1, "ci news (ceramics international)": 1, "applied clay science": 1, "journal of electroceramics": 1, "keram z": 1, "naihuo cailiao/refractories": 1, "nippon seramikkusu kyokai gakujutsu ronbunshi/journal of the ceramic society of japan": 1, "revue internationale des hautes temperatures et des refractaires": 1, "steklo i keramika": 1, "tile & brick international": 1, "trans indian ceram soc": 1, "world cement": 1, "yogyo kyokai shi/journal of the ceramic society of japan": 1}
chem_journal_dic = {"actualite chimique": 1, "aiche journal": 1, "angewandte chemie - international edition in english": 1, "applied catalysis a: general": 1, "applied catalysis b: environmental": 1, "applied organometallic chemistry": 1, "applied spectroscopy": 1, "catalysis today": 1, "central european journal of chemistry": 1, "chemical engineering journal": 1, "chemical engineering research and design": 1, "chemical engineering science": 1, "chemicke listy": 1, "chemie-ingenieur-technik": 1, "chemistry and industry (london)": 1, "chemistry of materials": 1, "chemosphere": 1, "chemtech": 1, "chinese journal of catalysis": 1, "chinese journal of chemical engineering": 1, "electrochemical and solid-state letters": 1, "electrochemistry communications": 1, "electrochimica acta": 1, "energy and fuels": 1, "eurasian chemico-technological journal": 1, "european journal of inorganic chemistry": 1, "fuel cells": 1, "fuel cells bulletin": 1, "glass physics and chemistry": 1, "industrial and engineering chemistry research": 1, "inorganic chemistry": 1, "international journal of chemical reactor engineering": 1, "journal of analytical atomic spectrometry": 1, "journal of applied chemistry of the ussr": 1, "journal of applied electrochemistry": 1, "journal of chemical engineering of japan": 1, "journal of chemical physics": 1, "journal of industrial and engineering chemistry": 1, "journal of solid state chemistry": 1, "journal of solid state electrochemistry": 1, "journal of the american chemical society": 1, "journal of the electrochemical society": 1, "korean journal of chemical engineering": 1, "mechanical and corrosion properties. series a, key engineering materials": 1, "quimica nova": 1, "radiation physics and chemistry": 1, "radiochemistry": 1, "russian journal of applied chemistry": 1, "russian journal of electrochemistry": 1, "russian journal of inorganic chemistry": 1, "studies in surface science and catalysis": 1, "topics in catalysis": 1, "analytica chimica acta": 1, "asian journal of chemistry": 1, "berichte der bunsengesellschaft/physical chemistry chemical physics": 1, "chinese journal of inorganic chemistry": 1, "corrosion science": 1, "fresenius' journal of analytical chemistry": 1, "fresenius' zeitschrift f\xc3\xbcr analytische chemie": 1, "huagong xuebao/journal of chemical industry and engineering (china)": 1, "huaxue gongcheng/chemical engineering (china)": 1, "journal of materials chemistry": 1, "journal of radioanalytical and nuclear chemistry": 1, "journal of sol-gel science and technology": 1, "mikrochimica acta": 1, "monatshefte fur chemie": 1, "nace - international corrosion conference series": 1, "progress in solid state chemistry": 1, "sensors and actuators: b. chemical": 1, "thermochimica acta": 1, "world academy of science, engineering and technology": 1, "zairyo to kankyo/ corrosion engineering": 1}
mater_journal_dic = {"acta materialia": 1,"acta metallurgica et materialia": 1,"advanced composite materials: the official journal of the japan society of composite materials": 1,"advanced composites bulletin": 1,"advanced engineering materials": 1,"advanced functional materials": 1,"advanced materials": 1,"advanced materials and processes": 1,"advanced materials research": 1,"advanced performance materials": 1,"annales de chimie: science des materiaux": 1,"applied mechanics and materials": 1,"bulletin of materials science": 1,"cailiao gongcheng/journal of materials engineering": 1,"cailiao kexue yu gongyi/material science and technology": 1,"cailiao yanjiu xuebao/chinese journal of materials research": 1,"composite structures": 1,"composites": 1,"composites - part a: applied science and manufacturing": 1,"composites engineering": 1,"composites part a: applied science and manufacturing": 1,"composites part b: engineering": 1,"composites science and technology": 1,"computational materials science": 1,"fatigue and fracture of engineering materials and structures": 1,"frontiers of materials science in china": 1,"high performance structures and materials": 1,"high temperature materials and processes": 1,"inorganic materials": 1,"international journal of inorganic materials": 1,"international journal of materials and product technology": 1,"international journal of materials research": 1,"international journal of minerals, metallurgy and materials": 1,"international journal of refractory metals and hard materials": 1,"journal of advanced materials": 1,"journal of alloys and compounds": 1,"journal of composite materials": 1,"journal of engineering materials and technology, transactions of the asme": 1,"journal of hazardous materials": 1,"journal of intelligent material systems and structures": 1,"journal of magnetism and magnetic materials": 1,"journal of materials engineering and performance": 1,"journal of materials processing tech.": 1,"journal of materials processing technology": 1,"journal of materials research": 1,"journal of materials science": 1,"journal of materials science and technology": 1,"journal of materials science letters": 1,"journal of materials synthesis and processing": 1,"journal of non-crystalline solids": 1,"journal of nuclear materials": 1,"journal of porous materials": 1,"jsme international journal, series 1: solid mechanics, strength of materials": 1,"jsme international journal, series a: mechanics and material engineering": 1,"jsme international journal, series a: solid mechanics and material engineering": 1,"key engineering materials": 1,"korean journal of materials research": 1,"manufacturing engineering": 1,"mater sci res": 1,"materiali in tehnologije": 1,"materials and design": 1,"materials and manufacturing processes": 1,"materials at high temperatures": 1,"materials characterization": 1,"materials chemistry & physics": 1,"materials chemistry and physics": 1,"materials engineering": 1,"materials evaluation": 1,"materials forum": 1,"materials letters": 1,"materials research": 1,"materials research bulletin": 1,"materials research innovations": 1,"materials science and engineering": 1,"materials science and engineering a": 1,"materials science and engineering b": 1,"materials science and engineering b: solid-state materials for advanced technology": 1,"materials science and engineering c": 1,"materials science and technology": 1,"materials science forum": 1,"materials science monographs": 1,"materials science research": 1,"materials science research international": 1,"materials science- poland": 1,"materials technology": 1,"materials transactions": 1,"materials transactions, jim": 1,"materials world": 1,"materialwissenschaft und werkstofftechnik": 1,"metallurgical and materials transactions a": 1,"metallurgical and materials transactions a: physical metallurgy and materials science": 1,"metallurgical and materials transactions b: process metallurgy and materials processing science": 1,"metallurgical transactions a": 1,"metals and materials bury st edmunds": 1,"metals and materials international": 1,"mrl bulletin of research and development": 1,"mrs bulletin": 1,"nanostructured materials": 1,"nature materials": 1,"optical materials": 1,"polymer composites": 1,"revista romana de materiale/ romanian journal of materials": 1,"science and technology of advanced materials": 1,"scripta materialia": 1,"scripta metallurgica": 1,"scripta metallurgica et materiala": 1,"soft materials": 1,"solar energy materials": 1,"soviet journal of superhard materials": 1,"synthetic metals": 1,"current opinion in solid state and materials science": 1,"journal of metastable and nanocrystalline materials": 1,"journal of reinforced plastics and composites": 1,"reviews on advanced materials science": 1,"revista materia": 1,"strength of materials": 1,"stroitel'nye materialy": 1,"archives of metallurgy and materials": 1,"construction and building materials": 1,"diamond and related materials": 1,"fenmo yejin cailiao kexue yu gongcheng/materials science and engineering of powder metallurgy": 1,"fuhe cailiao xuebao/acta materiae compositae sinica": 1,"functional materials letters": 1,"gaofenzi cailiao kexue yu gongcheng/polymeric materials science and engineering": 1,"glass": 1,"glass international": 1,"glass science and technology": 1,"glass science and technology frankfurt": 1,"glass science and technology: glastechnische berichte": 1,"glass technology": 1,"glass technology: european journal of glass science and technology part a": 1,"glastechnische berichte": 1,"gongneng cailiao yu qijian xuebao/journal of functional materials and devices": 1,"gongneng cailiao/journal of functional materials": 1,"hangkong cailiao xuebao/journal of aeronautical materials": 1,"indian journal of engineering and materials sciences": 1,"inorganic materials: applied research": 1,"jingangshi yu moliao moju gongcheng/diamond & abrasives engineering": 1,"jingangshi yu moliao moju gongcheng/diamond and abrasives engineering": 1,"jinshu rechuli/heat treatment of metals": 1,"jinshu xuebao/ acta metallurgica sinica": 1,"jinshu xuebao/acta metallurgica sinica": 1,"jom": 1,"journal of applied polymer science": 1,"journal of inorganic and organometallic polymers": 1,"journal of iron and steel research international": 1,"journal of korean institute of metals and materials": 1,"journal of metals": 1,"journal of optoelectronics and advanced materials": 1,"journal of polymer science, part b: polymer physics": 1,"journal of the less-common metals": 1,"journal of thermoplastic composite materials": 1,"journal of university of science and technology beijing: mineral metallurgy materials (eng ed)": 1,"journal wuhan university of technology, materials science edition": 1,"macromolecules": 1,"mecanique, materiaux, electricite": 1,"metall": 1,"metallofizika i noveishie tekhnologii": 1,"metallurg": 1,"metalurgia international": 1,"microporous and mesoporous materials": 1,"new materials & new processes": 1,"nippon kinzoku gakkaishi/journal of the japan institute of metals": 1,"polymer engineering and science": 1,"polymers for advanced technologies": 1,"powder metallurgy": 1,"powder metallurgy and metal ceramics": 1,"powder metallurgy international": 1,"powder technology": 1,"rapid prototyping journal": 1,"rare metals": 1,"rengong jingti xuebao/journal of synthetic crystals": 1,"revista de metalurgia (madrid)": 1,"smart materials and structures": 1,"soviet powder metallurgy and metal ceramics": 1,"steel research international": 1,"sumitomo metals": 1,"sverkhtverdye materialy": 1,"tetsu-to-hagane/journal of the iron and steel institute of japan": 1,"tezhong zhuzao ji youse hejin/special casting and nonferrous alloys": 1,"the carbide and tool journal": 1,"transactions of nonferrous metals society of china (english edition)": 1,"transactions of the indian institute of metals": 1,"transactions of the iron and steel institute of japan": 1,"upb scientific bulletin, series b: chemistry and materials science": 1,"welding international": 1,"wuji cailiao xuebao/journal of inorganic materials": 1,"xiyou jinshu / chinese journal of rare metals": 1,"xiyou jinshu cailiao yu gongcheng/rare metal materials and engineering": 1,"zairyo/journal of the society of materials science, japan": 1,"zeitschrift fuer metallkunde/materials research and advanced techniques": 1,"zeitschrift fuer werkstofftechnik/materials technology and testing": 1,"zhongguo youse jinshu xuebao/chinese journal of nonferrous metals": 1,"acta metallurgica": 1,"annual conference on materials for coal conversion and utilization (proceedings)": 1,"archives of materials science and engineering": 1,"fenmo yejin jishu/powder metallurgy technology": 1}
other_journal_dic = {'acta mechanica': 1,'advanced packaging': 1,'agard conference proceedings': 1,'american antiquity': 1,'ancient mesoamerica': 1,"annali dell'istituto superiore di sanita": 1,'antiquity': 1,'applications of cryogenic technology': 1,'archaeology, ethnology and anthropology of eurasia': 1,'archaeometry': 1,'archeologicke rozhledy': 1,'archeometriai muhely': 1,'arts of asia': 1,'bulletin de la societe prehistorique francaise': 1,'bulletin of the japan society of precision engineering': 1,'c e ca': 1,'cailiao rechuli xuebao/transactions of materials and heat treatment': 1,'carbon': 1,'china foundry': 1,'chinese journal of aeronautics': 1,'chinese science bulletin': 1,'chungara': 1,'cirp annals - manufacturing technology': 1,'colloids and surfaces a: physicochemical and engineering aspects': 1,'communications in computer and information science': 1,'crafts': 1,'cryogenics': 1,'cutting tool engineering': 1,'dalton transactions': 1,'defence science journal': 1,'desalination': 1,'desalination and water treatment': 1,'die quintessenz der zahntechnik': 1,'doklady akademii nauk': 1,'doktorsavhandlingar vid chalmers tekniska hogskola': 1,'dongbei daxue xuebao/journal of northeastern university': 1,'dyes and pigments': 1,'energy': 1,'energy and environmental science': 1,'engineer': 1,'engineering failure analysis': 1,'engineering fracture mechanics': 1,'engineering. cornell quarterly': 1,'environmental geology': 1,'environmental science and technology': 1,'estudios atacamenos': 1,'european cells and materials': 1,'european journal of oral sciences': 1,'european polymer journal': 1,'filtration and separation': 1,'fiz nizk temp': 1,'fizika i khimiya obrabotki materialov': 1,'fizika nizkikh temperatur (kharkov)': 1,'fizika nizkikh temperatur (kiev)': 1,'fiziko-khimicheskaya mekhanika materialov': 1,'foundry trade journal': 1,'freiberger forschungshefte (reihe) a': 1,'fusion engineering and design': 1,'fusion science and technology': 1,'fusion technology': 1,'gaodianya jishu/high voltage engineering': 1,'gaswaerme international': 1,'geliotekhnika': 1,'geoarchaeology - an international journal': 1,'guti huojian jishu/journal of solid rocket technology': 1,'huanan ligong daxue xuebao/journal of south china university of technology (natural science)': 1,'huanjing kexue/environmental science': 1,'hyperfine interactions': 1,'iarc scientific publications': 1,'ibm journal of research and development': 1,'ibm technical disclosure bulletin': 1,'iee colloquium (digest)': 1,'in: proc. jsle int. tribology conf., (tokyo, japan: jul. 8-10, 1985)': 1,'industrial heating': 1,'industrial laboratory': 1,'informacije midem': 1,'injury': 1,'instrum exp tech': 1,'instruments and experimental techniques new york': 1,'international applied mechanics': 1,'international journal of advanced manufacturing technology': 1,'international journal of fracture': 1,'international journal of hydrogen energy': 1,'international journal of impact engineering': 1,'international journal of machine tools and manufacture': 1,'international journal of manufacturing technology and management': 1,'international journal of solids and structures': 1,'intersecciones en antropologia': 1,'inzhenerno-fizicheskii zhurnal': 1,'inzynieria chemiczna i procesowa': 1,'ionics': 1,'isij international': 1,'israel journal of technology': 1,'izv akad nauk sssr neorg mater': 1,'izvestiya akademii nauk. ser. fizicheskaya': 1,'j eng power trans asme': 1,'j. japan society precision engineering': 1,"jane's defence weekly": 1,'jixie gongcheng xuebao/chinese journal of mechanical engineering': 1,'jixie gongcheng xuebao/journal of mechanical engineering': 1,'journal of adhesion science and technology': 1,'journal of applied mechanics, transactions asme': 1,'journal of applied oral science': 1,'journal of applied sciences': 1,'journal of archaeological method and theory': 1,'journal of archaeological science': 1,'journal of astm international': 1,'journal of central south university of technology (english edition)': 1,'journal of computational and theoretical nanoscience': 1,'journal of engineering for gas turbines and power': 1,'journal of failure analysis and prevention': 1,'journal of field archaeology': 1,'journal of food engineering': 1,'journal of harbin institute of technology (new series)': 1,'journal of japan society of lubrication engineers': 1,'journal of manufacturing science and engineering, transactions of the asme': 1,'journal of mechanical science and technology': 1,'journal of mechanical working technology': 1,'journal of membrane science': 1,'journal of micromechanics and microengineering': 1,'journal of microscopy': 1,'journal of molecular structure': 1,'journal of nanoparticle research': 1,'journal of power sources': 1,'journal of rare earths': 1,'journal of sound and vibration': 1,'journal of testing and evaluation': 1,'journal of the acoustical society of america': 1,'journal of the mechanics and physics of solids': 1,'journal of the royal society interface': 1,'journal of thermal spray technology': 1,'journal of tribology': 1,"kang t'ieh/iron and steel (peking)": 1,'konstruktion': 1,'kunsthandwerk und design': 1,'kunststoffe international': 1,'latin american antiquity': 1,'le vide, les couches minces': 1,'lecture notes in computer science (including subseries lecture notes in artificial intelligence and lecture notes in bioinformatics)': 1,'lecture notes in electrical engineering': 1,'liteinoe proizvodstvo': 1,'litejnoe proizvodstvo': 1,'lubrication engineering': 1,'machine design': 1,'machining science and technology': 1,'malaysian journal of microscopy': 1,'mcic rep 78-36': 1,'measurement science and technology': 1,'mechanics of materials': 1,'medziagotyra': 1,'metal powder report': 1,'micron': 1,'minutes of the meeting - pennsylvania electric association, engineering section': 1,'mocaxue xuebao/tribology': 1,'modern casting': 1,'nasa technical memorandum': 1,'national technical report': 1,'natl tech rep': 1,'natl tech rep matsushita electr ind': 1,'nato science for peace and security series b: physics and biophysics': 1,'nature': 1,'nec research and development': 1,'neorganiceskie materialy': 1,'nihon kikai gakkai ronbunshu, a hen/transactions of the japan society of mechanical engineers, part a': 1,'nippon hotetsu shika gakkai zasshi': 1,'nippon kikai gakkai ronbunshu, a hen/transactions of the japan society of mechanical engineers, part a': 1,'nippon kikai gakkai ronbunshu, b hen/transactions of the japan society of mechanical engineers, part b': 1,'nippon kikai gakkai ronbunshu, c hen/transactions of the japan society of mechanical engineers, part c': 1,'nippon kinzoku gakkai-si': 1,'nippon shishubyo gakkai kaishi': 1,'nist special publication': 1,'nongye jixie xuebao/transactions of the chinese society of agricultural machinery': 1,'ntisearch': 1,'nuclear and chemical waste management': 1,'ogneupory': 1,'ogneupory i tekhnicheskaya keramika': 1,'otolaryngologic clinics of north america': 1,'plasma processes and polymers': 1,'plasma science and technology': 1,'pollution engineering': 1,'poroshkovaya metallurgiya': 1,'power': 1,'prace naukowe instytutu budownictwa politechniki wroclawskiej': 1,'praktische metallographie/practical metallography': 1,'pribory i tekhnika eksperimenta': 1,'problemy prochnosti': 1,'proceedings - computer networking symposium': 1,'proceedings of the institution of mechanical engineers, part b: journal of engineering manufacture': 1,'proceedings of the national academy of sciences of the united states of america': 1,'proceedings of the royal society a: mathematical, physical and engineering sciences': 1,'quaternary international': 1,'quintessence international': 1,'quintessence international (berlin, germany : 1985)': 1,'report of the research laboratory of engineering materials tokyo': 1,'research disclosure': 1,'review of progress in quantitative nondestructive evaluation': 1,'review of scientific instruments': 1,'revista escola de minas': 1,'run hua yu mi feng/lubrication engineering': 1,'russ cast prod': 1,'russian engineering research': 1,'s t l e tribology transactions': 1,'s.a.m.p.e. quarterly': 1,'sadhana': 1,'sae (society of automotive engineers) transactions': 1,'sae prepr': 1,'sae preprints': 1,'schweissen und schneiden/welding and cutting': 1,'science in china, series e: technological sciences': 1,'seimitsu kogaku kaishi/journal of the japan society for precision engineering': 1,'shenyang gongye daxue xuebao/journal of shenyang university of technology': 1,'shenyang jianzhu daxue xuebao (ziran kexue ban)/journal of shenyang jianzhu university (natural science)': 1,'shinku/journal of the vacuum society of japan': 1,'signature (ramsey, n.j.)': 1,'solar energy': 1,'southeastern archaeology': 1,'sov j opt technol': 1,'soviet applied mechanics': 1,'soviet castings technology': 1,'soviet castings technology (english translation of liteinoe proizvodstvo)': 1,'soviet engineering research': 1,'sprechsaal': 1,'sprechsaal 1976': 1,'stahl und eisen': 1,"stal'": 1,'sumitomo search': 1,'surface and coatings technology': 1,'surface engineering': 1,'surface mount technology': 1,'svarochnoe proizvodstvo': 1,'talanta': 1,'technical paper - society of manufacturing engineers. ad': 1,'technical paper - society of manufacturing engineers. em': 1,'technical paper - society of manufacturing engineers. mr': 1,'theoretical and applied fracture mechanics': 1,'toraibarojisuto/journal of japanese society of tribologists': 1,'transactions of j w r i': 1,'transactions of powder mettalurgy association of india': 1,'transactions of the korean institute of electrical engineers': 1,'transactions of the korean society of mechanical engineers, a': 1,'transactions of the korean society of mechanical engineers, b': 1,'trenie i iznos': 1,'tribologie und schmierungstechnik': 1,'tribology and interface engineering series': 1,'tribology international': 1,'tribology letters': 1,'tribology series': 1,'tribology transactions': 1,'tyazheloe mashinostroenie': 1,'u.s. woman engineer': 1,'ukrainskii khimicheskii zhurnal': 1,'ultramicroscopy': 1,'vdi berichte': 1,'vdi-z': 1,'vuoto bologna': 1,'waste management': 1,'water research': 1,'water science and technology': 1,'wear': 1,'werkstoffe und korrosion': 1,'wuhan ligong daxue xuebao/journal of wuhan university of technology': 1,'xitong gongcheng lilun yu shijian/system engineering theory and practice': 1,'yi qi yi biao xue bao/chinese journal of scientific instrument': 1,'yosetsu gakkai ronbunshu/quarterly journal of the japan welding society': 1,'you qi chuyun': 1,'zahn-, mund-, und kieferheilkunde mit zentralblatt': 1,'zahntechnik; zeitschrift fur theorie und praxis der wissenschaftlichen zahntechnik': 1,'zhejiang daxue xuebao (gongxue ban)/journal of zhejiang university (engineering science)': 1,'zhendong yu chongji/journal of vibration and shock': 1,'zhongguo dianji gongcheng xuebao/proceedings of the chinese society of electrical engineering': 1,'zhongguo jixie gongcheng/china mechanical engineering': 1,'zhongguo xitu xuebao/journal of the chinese rare earth society': 1,'zhongnan daxue xuebao (ziran kexue ban)/journal of central south university (science and technology)': 1,'zhurnal fizicheskoi khimii': 1,'zhuzao/foundry': 1,'zi, ziegelindustrie international/brick and tile industry international': 1,'zwr': 1,'advanced powder technology': 1,'advanced science letters': 1,'aiaa journal': 1,'aiaa paper': 1,'american society of mechanical engineers (paper)': 1,'annals of the new york academy of sciences': 1,'applied energy': 1,'archive of applied mechanics': 1,'asme pap': 1,'asthetische zahnmedizin': 1,'atomnaya energiya': 1,'australian journal of basic and applied sciences': 1,'aviation week and space technology (new york)': 1,'azania': 1,'beijing gongye daxue xuebao / journal of beijing university of technology': 1,'beijing keji daxue xuebao/journal of university of science and technology beijing': 1,'beijing ligong daxue xuebao/transaction of beijing institute of technology': 1,'binggong xuebao/acta armamentarii': 1,'bulletin of the academy of sciences of the u.s.s.r. physical series': 1,'denshi gijutsu sogo kenkyusho iho/bulletin of the electrotechnical laboratory': 1,'deutsche zahnarztliche zeitschrift': 1,'die quintessenz': 1,'funtai oyobi fummatsu yakin/journal of the japan society of powder and powder metallurgy': 1,'hangkong dongli xuebao/journal of aerospace power': 1,'hanjie xuebao/transactions of the china welding institution': 1,'harbin gongye daxue xuebao/journal of harbin institute of technology': 1,"hsi-an chiao tung ta hsueh/journal of xi'an jiaotong university": 1,'huazhong keji daxue xuebao (ziran kexue ban)/journal of huazhong university of science and technology (natural science edition)': 1,'progress in natural science': 1,'przeglad elektrotechniczny': 1,'qinghua daxue xuebao/journal of tsinghua university': 1,'science': 1,'science china technological sciences': 1,'science of sintering': 1,'scientia sinica': 1,'separation and purification technology': 1,'separation science and technology': 1,'shanghai jiaotong daxue xuebao/journal of shanghai jiaotong university':1}
phys_journal_dic = {'acs applied materials and interfaces': 1,'acs nano': 1,'acs symposium series': 1,'applied physics a solids and surfaces': 1,'applied physics a: materials science and processing': 1,'applied physics b: lasers and optics': 1,'applied physics communications': 1,'applied physics express': 1,'applied physics letters': 1,'acta physica polonica a': 1,'applied superconductivity': 1,'applied thermal engineering': 1,'bulletin of the russian academy of sciences: physics': 1,'chinese physics letters': 1,'current applied physics': 1,'epj applied physics': 1,'european physical journal b': 1,'european physical journal: special topics': 1,'europhysics letters': 1,'ferroelectrics': 1,'ferroelectrics, letters section': 1,'high temperature science': 1,'high temperatures - high pressures': 1,'ieee antennas and wireless propagation letters': 1,'ieee journal of quantum electronics': 1,'ieee microwave and wireless components letters': 1,'ieee mtt-s international microwave symposium digest': 1,'ieee sensors journal': 1,'ieee trans components hybrids manuf technol': 1,'ieee trans parts hybrids packag': 1,'ieee transactions on advanced packaging': 1,'ieee transactions on antennas and propagation': 1,'ieee transactions on applied superconductivity': 1,'ieee transactions on components and packaging technologies': 1,'ieee transactions on components packaging and manufacturing technology part a': 1,'ieee transactions on components packaging and manufacturing technology part b': 1,'ieee transactions on components, hybrids, and manufacturing technology': 1,'ieee transactions on components, packaging and manufacturing technology': 1,'ieee transactions on components, packaging, and manufacturing technology. part a': 1,'ieee transactions on components, packaging, and manufacturing technology. part b, advanced packaging': 1,'ieee transactions on dielectrics and electrical insulation': 1,'ieee transactions on electrical insulation': 1,'ieee transactions on electron devices': 1,'ieee transactions on instrumentation and measurement': 1,'ieee transactions on magnetics': 1,'ieee transactions on microwave theory and techniques': 1,'ieee transactions on nuclear science': 1,'ieee transactions on plasma science': 1,'ieee transactions on ultrasonics, ferroelectrics, and frequency control': 1,'ieee wescon tech pap': 1,'ieice transactions on electronics': 1,'iet microwaves, antennas and propagation': 1,'indian journal of physics': 1,'indian journal of pure and applied physics': 1,'integrated ferroelectrics': 1,'international journal of heat and mass transfer': 1,'international journal of microcircuits and electronic packaging': 1,'international sampe electronics conference': 1,'japanese journal of applied physics': 1,'japanese journal of applied physics, part 1: regular papers & short notes': 1,'japanese journal of applied physics, part 1: regular papers & short notes & review papers': 1,'japanese journal of applied physics, part 1: regular papers and short notes and review papers': 1,'japanese journal of applied physics, part 2: letters': 1,'jee. journal of electronic engineering': 1,'journal de physique iii': 1,'journal de physique. colloque': 1,'journal de physique. iii': 1,'journal of applied physics': 1,'journal of electronic materials': 1,'journal of electronic packaging, transactions of the asme': 1,'journal of engineering physics': 1,'journal of low temperature physics': 1,'journal of materials science: materials in electronics': 1,'journal of physical chemistry b': 1,'journal of physical chemistry c': 1,'journal of physics and chemistry of solids': 1,'journal of physics condensed matter': 1,'journal of physics d: applied physics': 1,'journal of physics: condensed matter': 1,'journal of physics: conference series': 1,'journal of physics. c. solid state physics': 1,'journal of superconductivity': 1,'journal of superconductivity and novel magnetism': 1,'journal of the korean physical society': 1,'laser physics': 1,'laser physics letters': 1,'low temperature physics': 1,'microelectronic engineering': 1,'microelectronics and reliability': 1,'microelectronics reliability': 1,'nano letters': 1,'optics and laser technology': 1,'optics and lasers in engineering': 1,'optics communications': 1,'optics express': 1,'optics letters': 1,'optoelectronics and advanced materials, rapid communications': 1,'philosophical magazine a: physics of condensed matter, structure, defects and mechanical properties': 1,'physica b: condensed matter': 1,'physica b: physics of condensed matter': 1,'physica b: physics of condensed matter & c: atomic, molecular and plasma physics, optics': 1,'physica b+c': 1,'physica c: superconductivity and its applications': 1,'physica scripta': 1,'physica status solidi - rapid research letters': 1,'physica status solidi (a) applications and materials science': 1,'physica status solidi (a) applied research': 1,'physica status solidi (b) basic research': 1,'physica status solidi (c) current topics in solid state physics': 1,'physical chemistry chemical physics': 1,'physical review b': 1,'physical review b - condensed matter and materials physics': 1,'physical review letters': 1,'physics and chemistry of glasses': 1,'physics and chemistry of glasses: european journal of glass science and technology part b': 1,'physics and chemistry of materials treatment': 1,'physics letters a': 1,'physics of metals and metallography': 1,'physics of the solid state': 1,'russian journal of physical chemistry a': 1,'sensors and actuators': 1,'sensors and actuators, a: physical': 1,'sensors and actuators: a. physical': 1,'superconductor science and technology': 1,'central european journal of physics': 1,'chinese physics b': 1,'czechoslovak journal of physics': 1,'electronic materials letters': 1,'electronic packaging and production': 1,'electronics and communications in japan, part ii: electronics (english translation of denshi tsushin gakkai ronbunshi)': 1,'electronics letters': 1,'international journal of modern physics b': 1,'international journal of thermophysics': 1,'journal of applied crystallography': 1,'journal of crystal growth': 1,'journal of raman spectroscopy': 1,'journal of thermal analysis': 1,'journal of thermal analysis and calorimetry': 1,'langmuir': 1,'solid state communications': 1,'solid state ionics': 1,'solid state sciences': 1,'solid state technology': 1,'advancing microelectronics': 1,'chinese journal of sensors and actuators': 1,'chinese optics letters': 1,'crystal research and technology': 1,'crystallography reports': 1,'crystengcomm': 1,'defect and diffusion forum': 1,'defektoskopiya': 1,'diffusion and defect data pt.b: solid state phenomena': 1,'electri-onics': 1,'elektronika': 1,'elektronnaya obrabotka materialov': 1,'gaoya wuli xuebao/chinese journal of high pressure physics': 1,'guang pu xue yu guang pu fen xi/spectroscopy and spectral analysis': 1,'guangdianzi jiguang/journal of optoelectronics laser': 1,'guangxue jingmi gongcheng/optics and precision engineering': 1,'guangxue xuebao/acta optica sinica': 1,'guangzi xuebao/acta photonica sinica': 1,'high pressure research': 1,'hongwai yu jiguang gongcheng/infrared and laser engineering': 1,'hybrid circuit technology': 1,'international journal of nanoscience': 1,'j vac sci technol': 1,'japanese journal of tribology': 1,'journal of aerosol science': 1,'journal of colloid and interface science': 1,'journal of laser applications': 1,'journal of luminescence': 1,'journal of microelectronics and electronic packaging': 1,'journal of microwave power and electromagnetic energy': 1,'journal of nano research': 1,'journal of nanoscience and nanotechnology': 1,'journal of optical technology (a translation of opticheskii zhurnal)': 1,'journal of vacuum science and technology a: vacuum, surfaces and films': 1,'journal of vacuum science and technology b: microelectronics and nanometer structures': 1,'microscopy and microanalysis': 1,'microsystem technologies': 1,'microwave and optical technology letters': 1,'microwave journal': 1,'modern physics letters b': 1,'nanoscale research letters': 1,'nanotechnology': 1,'new electronics': 1,'nuclear inst. and methods in physics research, a': 1,'nuclear inst. and methods in physics research, b': 1,'nuclear instruments and methods in physics research, section a: accelerators, spectrometers, detectors and associated equipment': 1,'nuclear instruments and methods in physics research, section b: beam interactions with materials and atoms': 1,'nuclear technology': 1,'phase transitions': 1,'philosophical magazine': 1,'philosophical magazine letters': 1,'photonics spectra': 1,'proceedings of the ieee': 1,'proceedings of the international microelectronics symposium': 1,'progress in crystal growth and characterization of materials': 1,'quantum electronics': 1,'radiation effects and defects in solids': 1,'radiation measurements': 1,'radiation protection dosimetry': 1,'sensors and actuators, b: chemical': 1,'soviet physics - lebedev institute reports (english translation of sbornik \xe2\x80\xb3kratkie soobshcheniya po fizike\xe2\x80\xb3. an sssr. fizicheskii institut im. p.n. lebedeva)': 1,'surface and interface analysis': 1,'surface review and letters': 1,'surface science': 1,'technical physics': 1,'technical physics letters': 1,'teplofizika vysokikh temperatur': 1,'the soviet journal of glass physics and chemistry': 1,'thin solid films': 1,'transactions on electrical and electronic materials': 1,'ultrasonics': 1,'ultrasonics symposium proceedings': 1,'vacuum': 1,'vibrational spectroscopy': 1,'vide: science, technique et applications': 1,'wuli xuebao/acta physica sinica': 1,'x-ray spectrometry': 1,'yadian yu shengguang/piezoelectrics and acoustooptics': 1,'zeitschrift f\xc3\xbcr physik b condensed matter': 1,'zeitschrift fur kristallographie, supplement': 1,'zhongguo jiguang/chinese journal of lasers':1,'active and passive electronic components':1,'applied optics':1,'applied solar energy (english translation of geliotekhnika)':1,'applied surface science':1,'progress in nuclear energy':1,'qiangjiguang yu lizishu/high power laser and particle beams':1,'silicon':1}

# initialization of variables
keyword_results = ''
keyword_graph_string = ''
total_records = 0       # total number of records (articles) in all results files
# directory_size = get_size(rootPath)
color = get_color()
start_time = time.time()
# pb = ProgressBar()
abstract_length_array = []
title_length_array = []
page_length_array = []
page_length_supercon = []

# Keyword stats

# read the list of keywords to be analysed
analyse = []
fh = open('code/keywordList.txt', 'r')
for line in fh:
    analyse.append(line.strip().split(','))

# Do the analysis for each query file/year
for root, dirs, files in os.walk(rootPath):
    counter = 0
    for filename in fnmatch.filter(files, pattern):
        filenameOut = filename
        filename += rootPath
        year = (filenameOut[0:4])               # retrieves year from results filename
        # file_size = os.path.getsize(filename)   # get the current file size for the counter
        indata = (open(filename)).read()        # retrieves full text from results file

# removing the DUPLICATES from the imported query file
        everything_list = re.findall(r'\n@((.|\n)*?)\},\n\}\n', indata)     # separates indata per article
        everything_list = list(set(everything_list))                        # removes duplicates
        total_records += len(everything_list)                               # total number of records ( all!)
        everything_list = ' '.join(str(e) for e in everything_list)         # convert back to a string
        everything_list = everything_list.lower()                           # convert everything lower case

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

        outFileName = dirResults + 'keywords_graphe.csv'
        with open(outFileName, 'a+') as of:
            of.write(keyword_graph_string)

# Second master plot, with the KEYWORDS results

number_of_keywords = len(analyse)
gs = gridspec.GridSpec(number_of_keywords/4+2, 4)

plt.figure(num=None, dpi=dpi_fig, facecolor='w', edgecolor='w', frameon=False, figsize=(4,4))
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
    valeurY = [(x[1]/x[3]*valeur_ref) for x in result]
    max_valeurYear = max(valeurY)
    acolor = next(color)
    sub1.plot(valeurYear, valeurY, next(linecycler), lw=next(lwcycler), color=acolor, label = t, alpha = 1)
    sub3 = plt.subplot(gs[(i/4)+2, i%4])
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
    sub3.plot(valeurYear, valeurY/max_valeurYear, label = t, alpha = 1, lw=1)
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
leg = sub1.legend(handles2, labels2,  bbox_to_anchor=(0.96, 0.5), loc='center left', prop={'size': 9},
                  handlelength=1.3, handletextpad=0.5)
leg.get_frame().set_alpha(0)    # this will make the box totally transparent
leg.get_frame().set_edgecolor('white')  # this will make the edges of the border white

set_fontsize(plt, plot_font_size)

plt.tight_layout()

fig_name = 'figure keyword.png'
plt.savefig(fig_name, dpi=dpi_fig)