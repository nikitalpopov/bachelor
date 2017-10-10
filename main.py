import time
import json
import pandas
from collections import Counter
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.svm import LinearSVC
from sklearn.externals import joblib

import init
import parser
import downloader
from database import engine

# Init variables
data = []
trees = []

# Start filling tree of web-pages
# and filling table of pairs [this page url] - [urls of its children] - [text of web page]
init.queue = downloader.results
for i in range(len(init.queue)):  # process url[i] data
    if init.counter[i] < init.num:  # fill data for each children till it's possible
        # (or counter[i] == max subpages num for task)
        print(init.counter)
        parsing = list(downloader.results[i])  # get data from processed data
        if parsing[0] == parsing[1] and parsing[0] == []:
            continue  # if there is no data for subpage, skip it
        data.append((init.urls[i], parsing[0], parsing[1]))  # add data to dataframe (table)
        trees.append({'address': init.urls[i], 'children': []})  # fill tree root with url[i]
        init.children[i].append(init.urls[i])
        print(len(parsing[0]))  # print num of children urls
        for j in range(len(parsing[0])):
            # fill tree for url[i]: setting list of children urls with its children set as empty array
            trees[i]['children'].append({'address': parsing[0][j], 'children': []})
        init.counter[i] += 1  # go to next root url
stop = time.clock()
# print('Time of getting data: ', stop - start, ' s')
print(init.children)
# Print trees to 'trees.json'
trees_json = json.dumps(trees, indent=4, sort_keys=True)
with open(init.TREES, 'w') as outfile:
    outfile.write(trees_json)
print()

# print('Setting data to pandas dataframe...')
print('Getting train dataframe...')
list_of_column_names = ['url', 'links', 'text']
train = pandas.DataFrame(data, columns=list_of_column_names)
train.insert(0, 'category', init.categories)  # assert categories for train data
train.to_csv(init.TRAIN_DATA, sep=',', encoding='utf-8')
train.to_sql('train', engine, if_exists='replace')
print()
print(train)
print()
print('Getting data for sublevels')
print('+ Update trees for sublevels...')

data = []

for i in range(len(trees)):
        tree = trees[i]  # work with tree for root url[i]
        for j in range(len(tree['children'])):  # process its children urls
            if init.counter[i] < init.num:  # till it's possible
                # pprint.pprint(tree)
                print(init.counter)
                if init.counter[i] == init.num:
                    break  # if it's not possible
                subtree = tree['children'][j]  # tree of j-th children url
                url = subtree['address']  # current url
                if url not in init.children[i]:
                    print(url)
                    parsing = list(downloader.process_html(url, init.urls[i]))  # get data for url
                    if parsing[0] == parsing[1] and parsing[0] == []:  # if there is no data
                        tree['children'][j] = subtree  # save updated subtree
                        subtree = tree  # and get back to the parent
                        continue
                    else:
                        init.children[i].append(url)
                        data.append((url, parsing[0], parsing[1]))  # or add data to dataframe (table)
                        for k in range(len(parsing[0])):  # and start filling its children
                            subtree['children'].append({'address': parsing[0][k], 'children': []})
                        tree['children'][j] = subtree  # and save updated subtree
                    init.counter[i] += 1
                # else:
                #     print(url, ' is already a children')
        trees[i] = tree  # return updated tree

trees_json = json.dumps(trees, indent=4, sort_keys=True)
with open(init.TREES, 'w') as outfile:
    outfile.write(trees_json)
test = pandas.DataFrame(data, columns=list_of_column_names)
test.to_csv(init.TEST_DATA, sep=',', encoding='utf-8')
print()

print('Parsing text...')
train = parser.parse_data(init.TRAIN_DATA, init.TRAIN_TOKENS)
test = parser.parse_data(init.TEST_DATA, init.TEST_TOKENS, True)
coder = HashingVectorizer()
trn = coder.fit_transform(train.tokens)
clf = LinearSVC().fit(trn, train.category)
joblib.dump(clf, init.MODEL)
tst = coder.transform(test.tokens.values.astype('U'))
clf = joblib.load(init.MODEL)
result = clf.predict(tst)
predicted = pandas.Series(result)
test['predicted'] = predicted.values
print()

print('Getting predicted category for each web-site...')
for i in range(len(init.urls)):
    init.categories[i] = []  # each web-site category
    for url in init.children[i]:
        if not train.loc[train['url'] == url].empty:
            cat = train.loc[train['url'] == url, 'category'].iloc[0]
            init.categories[i].append(cat)
        else:
            cat = test.loc[test['url'] == url, 'predicted'].iloc[0]
            init.categories[i].append(cat)


print('Outputting result...')
with open(init.RESULTS, mode='w', encoding='utf-8') as output:
    output.write('\n'.join(result))

test.to_csv(init.TEST_DATA, sep=',', encoding='utf-8')

for i in range(len(init.urls)):
    init.categories[i] = Counter(init.categories[i]).most_common(1)[0][0]
output = 'result_' + str(init.num - 1) + '.csv'
init.get_output(output, init.categories, init.urls)
print()

print('The end')
