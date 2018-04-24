import errno
import os
import pandas
import platform
import requests
from colored import fg, attr
from datetime import datetime
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from pprint import pprint


def notify(title, text, subtitle='', sound='Glass'):
    """Send os notification
        :param title:
        :param subtitle:
        :param text:
        :param sound:
    """
    print()
    print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg(8) + text + attr(0))
    if subtitle != '':
        print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg(8) + subtitle + attr(0))
    print()

    # macOS notification
    if platform.system() == 'Darwin':
        os.system("""osascript -e 'display notification "{}" with title "{}" subtitle "{}" sound name "{}"'""".
                  format(text, title, subtitle, sound))
        os.system("""say -v Alex {} {}""".format(text, ' and ' + subtitle if subtitle else ''))


def parallel(func, parameters, mode='map', threads=cpu_count() - 1):
    """Run function with multithreading"""
    results = None
    # Make the Pool of workers
    with ThreadPool(threads) as pool:
        if mode == 'map':
            results = pool.map(func, parameters)
        if mode == 'starmap':
            results = pool.starmap(func, parameters)

        pool.close()
        pool.join()

    return results


def from_file(file):
    """Get initial data from file
        :param file: path to .txt file
        :return n: num of children pages of each website
        :return data: category - url pairs
    """
    with open(file, 'r') as input_file:
        n = int(input_file.readline())  # num of sites' subpages needed to be downloaded (including root)
        data = pandas.read_csv(input_file, sep=" ", header=None, names=['purpose', 'category', 'url'])

    return n, data


def adblock():
    try:
        os.makedirs('./data')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    for rule in ADBLOCK_RULES:
        r = requests.get(rule)

        with open('data/' + rule.rsplit('/', 1)[-1], 'wb') as f:
            f.write(r.content)


def get_output(output, results):
    """Write to .csv file and print results"""
    # print(fg('blue') + '[' + datetime.now().time() + ']' + attr(0), fg(2) + 'Predicted' + attr(0))
    # pprint(results)
    try:
        results.to_csv(output, sep=',', encoding='utf-8')
    except:
        print(fg(1) + 'something wrong with init.get_output()' + attr(0))


INIT_TIME = datetime.now()
INIT_PREFIX = 'init/'
DATA_PREFIX = 'data/{date:%Y-%m-%d_%H:%M:%S}/'.format(date=INIT_TIME)

UNIVERSITY_CATEGORY = 'university'  # 'newspaper'
SCIENCE_CATEGORY = 'institute'  # 'dogs'
OTHER_CATEGORY = 'other'  # 'house'

URLS = INIT_PREFIX + 'urls.txt'
TEST = INIT_PREFIX + 'test.txt'

TRAIN_DATA = DATA_PREFIX + 'train_data.csv'
TRAIN_TOKENS = DATA_PREFIX + 'train_tokens.csv'
TEST_DATA = DATA_PREFIX + 'test_data.csv'
TEST_TOKENS = DATA_PREFIX + 'test_tokens.csv'

UNIVERSITY_MODEL = DATA_PREFIX + UNIVERSITY_CATEGORY + '.pkl'
SCIENCE_MODEL = DATA_PREFIX + SCIENCE_CATEGORY + '.pkl'
OTHER_MODEL = DATA_PREFIX + OTHER_CATEGORY + '.pkl'

UNIVERSITY_PREDICTED = DATA_PREFIX + UNIVERSITY_CATEGORY + '.csv'
SCIENCE_PREDICTED = DATA_PREFIX + SCIENCE_CATEGORY + '.csv'
OTHER_PREDICTED = DATA_PREFIX + OTHER_CATEGORY + '.csv'

RESULTS = DATA_PREFIX + 'results.csv'
EXCEL = DATA_PREFIX + 'classification.xlsx'

ADBLOCK_RULES = ['https://easylist-downloads.adblockplus.org/ruadlist+easylist.txt',
                 'https://filters.adtidy.org/extension/chromium/filters/1.txt']

DEPTH = 1
