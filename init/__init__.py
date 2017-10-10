import pandas


def init_from_file(file):
    categories, urls = [], []
    with open(file, 'r') as input_file:
        n = int(input_file.readline())  # num of sites' subpages needed to be downloaded (including root)
        for line in input_file:
            row = line.split()
            categories.append(row[0])
            urls.append(row[1])

    return n, categories, urls


def get_output(output, categories, urls):
    results = []
    [results.append((categories[i], urls[i])) for i in range(len(urls))]
    results = pandas.DataFrame(results, columns=['predicted', 'url'])
    results.to_csv(output, sep=',', encoding='utf-8')
    print('Result:')
    print(results)
    print()


# Init variables
counter = []
children = []
queue = []
# MUST BE .csv!
TRAIN_DATA = 'train_data.csv'
TRAIN_TOKENS = 'train_tokens.csv'
TEST_DATA = 'test_data.csv'
TEST_TOKENS = 'test_tokens.csv'
# MUST BE .json!
TREES = 'trees.json'
MODEL = 'model.pkl'
RESULTS = 'results.txt'


# Ending of non-acceptable children link
file = open('init/endings.txt', 'r')
last = file.read().splitlines()
last = tuple(last + [ending.upper() for ending in last])

# Make the Pool of workers
from multiprocessing.dummy import Pool as ThreadPool
pool = ThreadPool(4)

print('Getting array of urls...')
# Get all urls from .txt to array of strings
num, categories, urls = init_from_file('init/urls.txt')
num += 1
print(urls)
print()

[children.append([]) for _ in range(len(urls))]  # children[i] == array of children urls for urls[i]
[counter.append(0) for _ in range(len(urls))]  # counter[i] == num of loaded subpages for urls[i]
print(counter)
print()
