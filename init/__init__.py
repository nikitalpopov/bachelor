import pandas
import os
import platform
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from colored import fg, attr


def notify(title, text):
    """Send os notification
        :param title:
        :param text:
    """
    print()
    print(fg(8) + text + attr(0))
    print()

    # macOS notification
    if platform.system() == 'Darwin':
        os.system(
            """osascript -e 'display notification "{}" with title "{}"'""".format(text, title))


def parallel_map(func, parameters, threads=cpu_count() - 1):
    """Run function with multithreading"""
    # Make the Pool of workers
    with ThreadPool(threads) as pool:
        results = pool.map(func, parameters)

        pool.close()
        pool.join()

    return results


def parallel_starmap(func, parameters, threads=cpu_count() - 1):
    """Run function with multithreading"""
    # Make the Pool of workers
    with ThreadPool(threads) as pool:
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


def get_output(output, categories, urls):
    """Write to .csv file and print results"""
    try:
        results = pandas.DataFrame([[].append((categories[i], urls[i])) for i in range(len(urls))],
                                   columns=['predicted', 'url'])
        results.to_csv(output, sep=',', encoding='utf-8')
    except:
        print(fg(1) + 'something wrong with init.get_output()' + attr(0))
    else:
        print(fg(2) + 'result:' + attr(0))
        print(results)
        print()


URLS = 'init/urls.txt'
TEST = 'init/test.txt'
# MUST BE .csv!
TRAIN_DATA = 'train_data.csv'
TRAIN_TOKENS = 'train_tokens.csv'
TEST_DATA = 'test_data.csv'
TEST_TOKENS = 'test_tokens.csv'
# MUST BE .json!
# TREES = 'trees.json'
UNIVERSITY_MODEL = 'university.pkl'
SCIENCE_MODEL = 'science.pkl'
OTHER_MODEL = 'other.pkl'
UNIVERSITY_PREDICTED = 'university.csv'
SCIENCE_PREDICTED = 'science.csv'
OTHER_PREDICTED = 'other.csv'
RESULTS = 'results.txt'
