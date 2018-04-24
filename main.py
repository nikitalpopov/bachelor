import classification
import init
import manager
import scraper
import text
import errno
import numpy
import os
import pandas
from colored import fg, attr
from datetime import datetime
from pprint import pprint

title = '🛠 bachelor [' + str(os.getpid()) + ']'
message = 'initializing data...'
begin = datetime.now()
init.notify(title, message)
try:
    os.makedirs(init.DATA_PREFIX)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
init.adblock()

# Get all urls from .txt to array of strings
children_count, categories = init.from_file(init.TEST)  # init.URLS for all urls, init.TEST for test set

# Results of scraping: 'url', 'type', 'text'
categories['url'] = init.parallel(scraper.get_actual_url, categories['url'], mode='map')
categories.to_csv('data/init.csv', sep=',', encoding='utf-8', index=False)

roots = categories.copy()
roots = roots.dropna(subset=['url']).reset_index(drop=True)
roots['root'] = init.parallel(manager.get_root, roots['url'], mode='map')
roots['children'] = children_count
roots = roots.drop(columns=['url'])

queue = categories.copy()
queue = queue.dropna(subset=['url']).reset_index(drop=True)
queue['root'] = init.parallel(manager.get_root, queue['url'], mode='map')
queue['status'] = '-'

message = 'parsing websites...'
init.notify(title, message)
data = pandas.DataFrame()
while not (roots.equals(roots.loc[roots['children'] <= 0]) or queue.equals(queue.loc[queue['status'] == '+'])) or\
    numpy.array_equal(queue.loc[queue['status'] == '-', 'root'].unique(),
                      roots.loc[roots['children'] <= 0, 'root'].unique()):
    queue, roots, data = manager.manage(queue, roots, data)
# queue, data = manager.manage(queue, roots, data)

message = 'parsing data...'
init.notify(title, message)
data = text.parse_text(data, init.TRAIN_DATA, init.TRAIN_TOKENS, 'pymorphy')

message = 'classification...'
init.notify(title, message)
classification.classify(data, roots)

# Exit
message = 'script has finished'
end = str((datetime.now() - begin).total_seconds() / 60.0)
end = end.split('.')[0] + '.' + end.split('.')[1][:1]
init.notify(title, message, end + ' minutes spent')
