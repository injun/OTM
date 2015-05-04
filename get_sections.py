import unicodedata
import pandas as pd
import re


def get_articles(text):
    """extracts and merges all text in all query files"""
    regex_article = r'\n@((.|\n)*?)\},\n\}\n'               # TODO test regex: separates last letter
    articles = list(set(re.findall(regex_article, text)))   # split articles and remove duplicates (will use later)
    articles = ' '.join(str(article) for article in articles)   # join all text in a string
    articles = articles.lower()                             # convert to lower case
    return articles


def count_articles(text):
    """counts number of articles in all years, from the number of url's found in query files"""
    regex_url = r'url=\{(.*?)\},'
    url_list = re.findall(regex_url, text)
    number_of_articles = len(url_list)
    del url_list
    return number_of_articles


def get_title_abstract(text):
    """
    :param regex: regular expression to find given section (abstract, title, ...) in text
    :param text: text from combined query result
    :return: all combined titles from the query results
    """
    regex_title = r'title=\{((.|\n)*?)},'
    regex_abstract = r'abstract=\{(.*?)\},'
    for regex in [regex_title, regex_abstract]:
        section = list(set(re.findall(regex, text)))
        section = str(section).strip('[]')
        section = section.lower()
        section = section.replace("title={", " ")
        section = section.replace("abstract={", " ")
        section = section.replace("}", " ")
        section = remove_punctuation(section)
        section = rmv_similar_words(section)
        section += section
        title_abstract = section
    return title_abstract


def remove_punctuation(text):
    symbols = ["'", "(", ")", ",", ".", ":", ";", "abstract={", "title={", "{", "}"]
    for symbol in symbols:
        text = text.replace(symbol, " ")
    return text


def keywords_cleanup(indata_keywords):
    indata_keywords = indata_keywords.replace(",", ";")
    symbols = ["[", "]", "(", ")", "'", "+", ":", "-", "null"]
    for symbol in symbols:
        indata_keywords = indata_keywords.replace(symbol, " ")
    return indata_keywords


# TODO replace htlm code for symbols and chemical formulae in results by proper characters


def rmv_similar_words(text):
    list_of_similar_words = pd.read_table('code/similars.csv', sep=',')
    for word in range(len(list_of_similar_words)):
        replaced_text = text.replace(list_of_similar_words.at[word, 'ORIGINAL'],
                                     list_of_similar_words.at[word, 'REPLACEMENT'])
    return replaced_text


def strip_accents(s):
    nkfd_form = unicodedata.normalize('NFKD', unicode(s))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


