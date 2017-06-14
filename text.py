import csv
import pymorphy2


def clean_text(train):
    # Remove all short words
    train.text = train.text.str.replace(r'\W*\b\w{1,2}\b', ' ')

    # All text to lower case
    train.text = train.text.str.lower()

    # Cleaning text from useless characters
    train.text = train.text.str.replace(r'[^\u0400-\u04FF]', u' ')
    train.text = train.text.str.replace(' - ', ' ')
    train.text = train.text.str.replace('[0-9]', ' ')
    train.text = train.text.str.replace('- ', ' ')
    train.text = train.text.str.replace(' -', ' ')
    train.text = train.text.str.replace(u' . ', ' ')
    train.text = train.text.str.replace(u'.', ' ')
    train.text = train.text.str.replace(u'[', ' ')
    train.text = train.text.str.replace(u']', ' ')
    train.text = train.text.str.replace(u'=', ' ')
    train.text = train.text.str.replace(u'+', ' ')
    train.text = train.text.str.replace(r',!?&*#№@|/():"«»+=§±`~', ' ')
    train.text = train.text.str.replace(u' +', ' ')
    train.text = train.text.str.strip()
    # print(train.text)


def tokenization(dataframe, csv_file):
    out_csv = csv.writer(open(csv_file, "w", encoding='utf-8'))
    out_csv.writerow(['url', 'category', 'tokens'])

    morph = pymorphy2.MorphAnalyzer()
    for i in range(dataframe.shape[0]):
        url = dataframe.iloc[i]['url']
        cat = dataframe.iloc[i]['category']
        z = dataframe.iloc[i]['text']

        if type(z) == str:
            out_csv.writerow((url, cat, my_tokenizer(z, morph)))
        else:
            out_csv.writerow((url, cat, []))


def tokenization_test(dataframe, csv_file):
    out_csv = csv.writer(open(csv_file, "w", encoding = 'utf-8'))
    out_csv.writerow(['url', 'predicted', 'tokens'])

    morph = pymorphy2.MorphAnalyzer()
    for i in range(dataframe.shape[0]):
        url = dataframe.iloc[i]['url']
        z = dataframe.iloc[i]['text']

        if type(z) == str:
            out_csv.writerow((url, [], my_tokenizer(z, morph)))
        else:
            out_csv.writerow((url, [], []))


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

