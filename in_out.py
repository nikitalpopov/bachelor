import pandas


def init_from_file(file):
    categories, urls = [], []
    with open(file, 'r') as input:
        n = int(input.readline()) # num of sites' subpages needed to be downloaded (including root)
        for line in input:
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
