import classification
import init
import manager
import scraper
import text
import errno
import os
import pandas
from datetime import datetime
from pprint import pprint

title = '🛠 bachelor [' + str(os.getpid()) + ']'
message = 'initializing data...'
begin = datetime.now()
init.notify(title, message)
# Get all urls from .txt to array of strings
children_count, categories = init.from_file(init.URLS)  # init.URLS for all urls, init.TEST for test set
# pprint(categories)

# Results of scraping: 'url', 'type', 'text'
scraped = init.parallel(scraper.parse_url, categories['url'], mode='map')

roots = categories.copy()
roots['root'] = None
roots['children'] = None
queue = categories.copy()
queue['root'] = None
queue['status'] = None
for website in scraped:
    if website['url']:
        roots.loc[roots['url'] == website['url'], 'root'] = manager.get_root_domain(website['url'])
        roots.loc[roots['url'] == website['url'], 'children'] = children_count
        queue.loc[queue['url'] == website['url'], 'root'] = manager.get_root_domain(website['url'])
        queue.loc[queue['url'] == website['url'], 'status'] = '-'
roots = roots.drop(columns=['url']).dropna().reset_index(drop=True)
queue = queue.dropna().reset_index(drop=True)

message = 'parsing websites...'
init.notify(title, message)
data = pandas.DataFrame()
queue, data = manager.manage(queue, roots, data)
# input()

message = 'parsing data...'
init.notify(title, message)
try:
    os.makedirs('./data')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
data = text.parse_text(data, init.TRAIN_DATA, init.TRAIN_TOKENS, 'pymorphy')
# input()

message = 'classification...'
init.notify(title, message)
classification.classify(data)

# Exit
message = 'script has finished'
end = str((datetime.now() - begin).total_seconds() / 60.0)
end = end.split(".")[0] + '.' + end.split(".")[1][:1]
init.notify(title, message, end + ' minutes spent')
