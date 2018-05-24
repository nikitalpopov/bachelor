import init
import pandas
import pymorphy2


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


def clear_text(text):
    # Remove all short words
    text = text.str.replace(r'\W*\b\w{1,2}\b', ' ')

    # All text to lower case
    text = text.str.lower()

    # Cleaning text from useless characters
    text = text.str.replace(r'[^\u0400-\u04FF]', u' ')
    text = text.str.replace(' - ', ' ')
    text = text.str.replace('[0-9]', ' ')
    text = text.str.replace('- ', ' ')
    text = text.str.replace(' -', ' ')
    text = text.str.replace(u' . ', ' ')
    text = text.str.replace(u'.', ' ')
    text = text.str.replace(u'[', ' ')
    text = text.str.replace(u']', ' ')
    text = text.str.replace(u'=', ' ')
    text = text.str.replace(u'+', ' ')
    text = text.str.replace(r',!?&*#№@|/():"«»§±`~', ' ')
    text = text.str.replace(u' +', ' ')
    text = text.str.strip()

    return text


def my_tokenizer(s, morph):
    parts_of_speech = ('NUMR', 'PREP', 'CONJ', 'PRCL', 'INTJ', 'NPRO', 'COMP', 'PRED')
    t = s.split(' ')
    f = ''
    for j in t:
        m = morph.parse(j.replace('.', ''))
        if len(m) != 0:
            wrd = m[0]
            if wrd.tag.POS not in parts_of_speech:
                f = f + ' ' + str(wrd.normal_form)

    return f


def parse_text(dataframe, input, output):
    writer = pandas.ExcelWriter(init.DATA_PREFIX + 'data.xlsx')
    dataframe.to_excel(writer, 'train')
    dataframe.to_csv(input, sep=',', encoding='utf-8', index=False)

    morph = pymorphy2.MorphAnalyzer()
    for column in ['text', 'title', 'meta']:
        dataframe[column] = clear_text(dataframe[column]).apply(lambda x: my_tokenizer(x, morph))
    dataframe.to_excel(writer, 'tokens')
    dataframe.to_csv(output, sep=',', encoding='utf-8')

    return dataframe
