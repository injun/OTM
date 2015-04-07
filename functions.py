class ProgressBar():
    def __init__(self, width=50):
        self.pointer = 0
        self.width = width

    def __call__(self,x, year, time_left):
         # x in percent
         self.pointer = int(self.width*(x/100.0))
         minutes = int(time_left/60)
         seconds = int(time_left % 60)
         if minutes == 0:
            return "|" + "#"*self.pointer + "-"*(self.width-self.pointer)+\
                "|\n %d percent done, doing year %s, estimated time left:  %ss" % (int(x), year, seconds)
         else:
            return "|" + "#"*self.pointer + "-"*(self.width-self.pointer)+\
                "|\n %d percent done, doing year %s, estimated time left: %smin %ss" % (int(x), year, minutes, seconds)

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def remove_punctuation (dataString):
    symbols = ["'", "(", ")", ",", ".", ":", ";", "abstract={", "title={", "{", "}"]
    for item in symbols:
        dataString = dataString.replace(item, " ")
    return dataString

def keywords_cleanup(indata_keywords):
    indata_keywords = indata_keywords.replace(",",";")
    symbols = ["[", "]", "(", ")", "'", "+", ":", "-", "null"]
    for item in symbols:
        indata_keywords = indata_keywords.replace(item, "")
    return indata_keywords

def remove_similars (dataString):
    data = pd.read_table('code/similars.csv', sep=',')
    for i in range(len(data)):
        dataString = dataString.replace(data.at[i, 'ORIGINAL'],data.at[i, 'REPLACEMENT'])
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
