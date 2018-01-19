import pandas
from multiprocessing.dummy import Pool as ThreadPool


def parallel(func, parameters, threads=4):
    """Run function with multithreading"""
    # Make the Pool of workers
    pool = ThreadPool(threads)
    # Run func
    results = pool.map(func, parameters)
    # Close pool
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
        data = pandas.read_csv(input_file, sep=" ", header=None, names=['category', 'url'])

    return n, data


def get_output(output, categories, urls):
    """Write to .csv file and print results"""
    results = pandas.DataFrame([[].append((categories[i], urls[i])) for i in range(len(urls))],
                               columns=['predicted', 'url'])
    results.to_csv(output, sep=',', encoding='utf-8')
    print('Result:')
    print(results)
    print()


# Init variables
counter = []
children = []
queue = []
URLS = 'init/urls.txt'
# MUST BE .csv!
TRAIN_DATA = 'train_data.csv'
TRAIN_TOKENS = 'train_tokens.csv'
TEST_DATA = 'test_data.csv'
TEST_TOKENS = 'test_tokens.csv'
# MUST BE .json!
TREES = 'trees.json'
MODEL = 'model.pkl'
RESULTS = 'results.txt'
