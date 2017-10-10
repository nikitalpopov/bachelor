import csv
import pymorphy2
import pandas


def clean_text(dataframe):
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


def parse_data(input, output, is_test=False):
    dataframe = pandas.read_csv(input, sep=',', encoding='utf-8')
    clean_text(dataframe)
    dataframe.to_csv(input, sep=',', encoding='utf-8')
    tokenization(dataframe, output, is_test)

    return pandas.read_csv(output, sep=',', encoding='utf-8')
