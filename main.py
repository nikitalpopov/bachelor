import init
import manager
import scraper
import text
import classification
import pandas
from pprint import pprint

title = '🛠 bachelor'
message = 'initializing data...'
init.notify(title, message)
# Get all urls from .txt to array of strings
children_count, categories = init.from_file(init.URLS)

# Results of scraping: 'url', 'type', 'text'
# scraped = init.parallel(scraper.parse_url, [categories.iloc[0]['url']])  # get first url
scraped = init.parallel(scraper.parse_url, categories['url'])  # all urls
# pprint(scraped)

# List of available websites
roots = pandas.Series([url for url in [x['url'] for x in scraped if x['url'] is not None]])
roots.name = 'url'
clean_roots = pandas.Series(
    [manager.get_root_domain(url) for url in [x['url'] for x in scraped if x['url'] is not None]]
)
clean_roots.name = 'root'
# pprint(roots)

queue = pandas.concat([roots, clean_roots], axis=1)
data = pandas.DataFrame()
manager.run(queue, clean_roots, data)

exit()

message = 'parsing data...'
init.notify(title, message)
# Dataframe with scraped data
train = pandas.DataFrame.from_records(scraped)
train = train.dropna(how='all')
# pprint(train)
train['category'] = pandas.Series([categories['category'][i] for i in train.index.values]).values
train['root'] = roots.values
train.to_csv(init.TRAIN_DATA, sep=',', encoding='utf-8', index=False)

train = text.parse_text(init.TRAIN_DATA, init.TRAIN_TOKENS, 'pymorphy')
# pprint(train)

message = 'classification...'
init.notify(title, message)
predicted = classification.classify(train)
pprint(predicted)

# Exit
message = 'script has finished'
init.notify(title, message)
