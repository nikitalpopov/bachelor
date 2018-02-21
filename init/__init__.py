import os
import pandas
import platform
from colored import fg, attr
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from pprint import pprint


def notify(title, text, sound='Glass'):
    """Send os notification
        :param title:
        :param text:
        :param sound:
    """
    print()
    print(fg(8) + text + attr(0))
    print()

    # macOS notification
    if platform.system() == 'Darwin':
        os.system("""osascript -e 'display notification "{}" with title "{}" sound name "{}"'""".
                  format(text, title, sound))
        # os.system("""say -v Alex {}""".format(text))


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


def get_output(output, results):
    """Write to .csv file and print results"""
    # print(fg(2) + 'Predicted' + attr(0))
    # pprint(results)
    try:
        results.to_csv(output, sep=',', encoding='utf-8')
    except:
        print(fg(1) + 'something wrong with init.get_output()' + attr(0))


URLS = 'init/urls.txt'
TEST = 'init/test.txt'
# MUST BE .csv!
TRAIN_DATA = 'data/train_data.csv'
TRAIN_TOKENS = 'data/train_tokens.csv'
TEST_DATA = 'data/test_data.csv'
TEST_TOKENS = 'data/test_tokens.csv'
# MUST BE .json!
# TREES = 'trees.json'
UNIVERSITY_MODEL = 'data/university.pkl'
SCIENCE_MODEL = 'data/science.pkl'
OTHER_MODEL = 'data/other.pkl'
UNIVERSITY_PREDICTED = 'data/university.csv'
SCIENCE_PREDICTED = 'data/science.csv'
OTHER_PREDICTED = 'data/other.csv'
RESULTS = 'data/results.csv'
