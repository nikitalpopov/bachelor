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
init.notify(title, '', message)
# Get all urls from .txt to array of strings
children_count, categories = init.from_file(init.TEST)  # init.URLS for all urls, init.TEST for test set

# Results of scraping: 'url', 'type', 'text'
scraped = init.parallel(scraper.parse_url, categories['url'], mode='map')

queue = pandas.DataFrame.from_dict({
    'url': [url for url in [x['url'] for x in scraped if x['url'] is not None]],
    'root': [manager.get_root_domain(url) for url in [x['url'] for x in scraped if x['url'] is not None]],
    'status': ['-' for _ in [x['url'] for x in scraped if x['url'] is not None]]
})
roots = pandas.DataFrame.from_dict({
    'root': [manager.get_root_domain(url) for url in [x['url'] for x in scraped if x['url'] is not None]],
    'children': [children_count for _ in [x['url'] for x in scraped if x['url'] is not None]]
})

roots['category'] = categories.loc[categories['url'].str.contains('|'.join(roots.root.values)), 'category']\
    .reset_index(drop=True)
roots['purpose'] = categories.loc[categories['url'].str.contains('|'.join(roots.root.values)), 'purpose']\
    .reset_index(drop=True)
queue['category'] = roots['category']

message = 'parsing websites...'
init.notify(title, '', message)
data = pandas.DataFrame()
queue, data = manager.manage(queue, roots, data)
# pprint(data)

message = 'parsing data...'
init.notify(title, '', message)
try:
    os.makedirs('./data')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
data.to_csv(init.TRAIN_DATA, sep=',', encoding='utf-8', index=False)
data = text.parse_text(init.TRAIN_DATA, init.TRAIN_TOKENS, 'pymorphy')
# pprint(data)

message = 'classification...'
init.notify(title, '', message)
classification.classify(data)

# Exit
message = 'script has finished'
end = str((datetime.now() - begin).total_seconds() / 60.0)
end = end.split(".")[0] + '.' + end.split(".")[1][:2]
init.notify(title, end + ' minutes spent', message)
