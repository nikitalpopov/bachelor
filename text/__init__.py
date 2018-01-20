import csv
import pandas
import pymorphy2
import nltk
import string
from nltk.corpus import stopwords


def find_between(string, first, last):
    """Find substring between first 'first' and last 'last'
        :param first:
        :param last:
        :return string:
    """
    try:
        if string == '':
            return ''
        start = string.index(first) + len(first)
        end = string.rindex(last, start)

        return string[start:end]

    except AttributeError:
        return ''

    except ValueError:
        return ''


# PYMORPHY2
def clear_text(dataframe):
    # Remove all short words
    dataframe.text = dataframe.text.str.replace(r'\W*\b\w{1,2}\b', ' ')

    # All text to lower case
    dataframe.text = dataframe.text.str.lower()

    # Cleaning text from useless characters
    dataframe.text = dataframe.text.str.replace(r'[^\u0400-\u04FF]', u' ')
    dataframe.text = dataframe.text.str.replace(' - ', ' ')
    dataframe.text = dataframe.text.str.replace('[0-9]', ' ')
    dataframe.text = dataframe.text.str.replace('- ', ' ')
    dataframe.text = dataframe.text.str.replace(' -', ' ')
    dataframe.text = dataframe.text.str.replace(u' . ', ' ')
    dataframe.text = dataframe.text.str.replace(u'.', ' ')
    dataframe.text = dataframe.text.str.replace(u'[', ' ')
    dataframe.text = dataframe.text.str.replace(u']', ' ')
    dataframe.text = dataframe.text.str.replace(u'=', ' ')
    dataframe.text = dataframe.text.str.replace(u'+', ' ')
    dataframe.text = dataframe.text.str.replace(r',!?&*#№@|/():"«»§±`~', ' ')
    dataframe.text = dataframe.text.str.replace(u' +', ' ')
    dataframe.text = dataframe.text.str.strip()
    # print(train.text)


def tokenization(dataframe, csv_file, is_test=False):
    out_csv = csv.writer(open(csv_file, "w", encoding='utf-8'))
    out_csv.writerow(['url', 'predicted' if is_test else 'category', 'tokens'])

    morph = pymorphy2.MorphAnalyzer()
    for i in range(dataframe.shape[0]):
        url = dataframe.iloc[i]['url']
        cat = dataframe.iloc[i]['category'] if not is_test else []
        z = dataframe.iloc[i]['text']

        if type(z) == str:
            out_csv.writerow((url, cat, my_tokenizer(z, morph)))
        else:
            out_csv.writerow((url, cat, []))


def my_tokenizer(s, morph):
    t = s.split(' ')
    # print('t: ', t)
    f = ''
    for j in t:
        # print('j: ', j)
        m = morph.parse(j.replace('.', ''))
        if len(m) != 0:
            wrd = m[0]
            # print('wrd: ', wrd)
            if wrd.tag.POS not in ('NUMR', 'PREP', 'CONJ', 'PRCL', 'INTJ', 'NPRO', 'COMP', 'PRED'):
                f = f + ' ' + str(wrd.normal_form)
    # print('f: ', f)

    return f


# NLTK
def tokenization_nltk(dataframe, csv_file, is_test=False):
    # firstly let's apply nltk tokenization
    dataframe.text = nltk.word_tokenize(dataframe.text)
    print(dataframe)

    # let's delete punctuation symbols
    dataframe.text = [i for i in dataframe.text if (i not in string.punctuation)]

    # deleting stop_words
    stop_words = stopwords.words('russian')
    stop_words.extend(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на'])
    dataframe.text = [i for i in dataframe.text if (i not in stop_words)]

    # cleaning words
    dataframe.text = [i.replace("«", "").replace("»", "") for i in dataframe.text]

    # output results
    out_csv = csv.writer(open(csv_file, "w", encoding='utf-8'))
    out_csv.writerow(['url', 'predicted' if is_test else 'category', 'tokens'])
    for i in range(dataframe.shape[0]):
        url = dataframe.iloc[i]['url']
        cat = dataframe.iloc[i]['category'] if not is_test else []
        z = dataframe.iloc[i]['text']

        if type(z) == str:
            out_csv.writerow((url, cat, z))
        else:
            out_csv.writerow((url, cat, []))


def parse_data(input, output, engine='pymorphy', is_test=False):
    dataframe = pandas.read_csv(input, sep=',', encoding='utf-8')
    if engine == 'nltk':
        tokenization_nltk(dataframe, output, is_test)  # @todo test
    else:  # engine == 'pymorphy'
        clear_text(dataframe)
        dataframe.to_csv(input, sep=',', encoding='utf-8')
        tokenization(dataframe, output, is_test)

    return pandas.read_csv(output, sep=',', encoding='utf-8')
