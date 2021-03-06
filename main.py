import classification
import init
import manager
import scraper
import text
import errno
import numpy
import os
import pandas
import plotly.plotly as py
from colored import fg, attr
from datetime import datetime
from pprint import pprint

title = '🛠 bachelor [' + str(os.getpid()) + ']'
message = 'initializing data...'
# init.URLS for default dataset, init.TEST for tests
dataset = init.TEST
begin = datetime.now()
init.notify(title, message)
try:
    os.makedirs(init.DATA_PREFIX)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
init.adblock()
py.sign_in(init.PLOTLY['username'], init.PLOTLY['api_key'])

# Get all urls from .txt to array of strings
children_count, initial_data, init.CATEGORIES = init.from_file(dataset)

# Results of scraping: 'url', 'type', 'text'
initial_data['url'] = init.parallel(scraper.get_actual_url, initial_data['url'], mode='map')
initial_data.to_csv(init.DATA_PREFIX + 'init.csv', sep=',', encoding='utf-8', index=False)

roots = initial_data.copy()
roots = roots.dropna(subset=['url']).reset_index(drop=True)
roots['root'] = init.parallel(manager.get_root, roots['url'], mode='map')
queue = roots.copy()
roots['children'] = children_count
roots = roots.drop(columns=['url'])
queue['status'] = '-'

message = 'parsing websites...'
init.notify(title, message)
data = pandas.DataFrame()
counter = 0
while not (roots.equals(roots.loc[roots['children'] <= 0]) or queue.equals(queue.loc[queue['status'] == '+'])) or\
    numpy.array_equal(queue.loc[queue['status'] == '-', 'root'].unique(),
                      roots.loc[roots['children'] <= 0, 'root'].unique()):
    queue, roots, data = manager.manage(queue, roots, data)
    print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), len(queue))
    pprint(roots)
    roots.to_csv(init.DATA_PREFIX + str(counter) + '_roots.csv', sep=',', encoding='utf-8')
    queue.to_csv(init.DATA_PREFIX + str(counter) + '_queue.csv', sep=',', encoding='utf-8')
    counter += 1

message = 'parsing data...'
init.notify(title, message)
data = text.parse_text(data, init.TRAIN_DATA, init.TRAIN_TOKENS)

message = 'classification...'
init.notify(title, message)
classification.classify(data, roots)

# Exit
message = 'script has finished'
end = str((datetime.now() - begin).total_seconds() / 60.0)
end = end.split('.')[0] + '.' + end.split('.')[1][:1]
init.notify(title, message, end + ' minutes spent')
