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
# scraped = init.parallel(scraper.parse_url, [categories.iloc[3]['url']])  # get first url
scraped = init.parallel(scraper.parse_url, categories['url'])  # all urls
# pprint(scraped)

# List of available websites
queue = pandas.DataFrame.from_dict({
    'url': [url for url in [x['url'] for x in scraped if x['url'] is not None]],
    'status': ['-' for _ in [x['url'] for x in scraped if x['url'] is not None]]
})
roots = pandas.DataFrame.from_dict({
    'root': [manager.get_root_domain(url) for url in [x['url'] for x in scraped if x['url'] is not None]],
    'children': [20 for _ in [x['url'] for x in scraped if x['url'] is not None]]
})

data = pandas.DataFrame()
queue, data = manager.manage(queue, roots, data)
pprint(data)

message = 'parsing data...'
init.notify(title, message)
# Dataframe with scraped data
# dataframe = pandas.DataFrame.from_records(scraped)
# dataframe = dataframe.dropna(how='all')
dataframe = data.copy()
# pprint(train)
dataframe['purpose'] = pandas.Series([categories['purpose'][i] for i in dataframe.index.values]).values
dataframe['category'] = pandas.Series([categories['category'][i] for i in dataframe.index.values]).values
dataframe['root'] = queue['url']
dataframe.to_csv(init.TRAIN_DATA, sep=',', encoding='utf-8', index=False)
dataframe = text.parse_text(init.TRAIN_DATA, init.TRAIN_TOKENS, 'pymorphy')
# pprint(train)

message = 'classification...'
init.notify(title, message)
predicted = classification.classify(dataframe)
pprint(predicted)

# Exit
message = 'script has finished'
init.notify(title, message)
