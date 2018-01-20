import init
import scraper
import pandas
import text
from pprint import pprint


print('Getting array of urls...')
# Get all urls from .txt to array of strings
children_count, categories = init.from_file(init.URLS)

# Results of scraping: 'url', 'type', 'text'
# scraped = init.parallel(scraper.parse_url, [categories.iloc[0]['url']])  # get first url
scraped = init.parallel(scraper.parse_url, categories['url'])  # all urls
# pprint([x for x in scraped])
# @todo Drop all Nones

# List of available websites
roots = [scraper.get_root_domain(url) for url in [x['url'] for x in scraped if x['url'] is not None]]
# pprint(roots)

print('Parsing data...')
# Dataframe with scraped data
# @todo Modify Dataframe: add 'category', etc.
train = pandas.DataFrame.from_records(scraped)
# pprint(train)
train.to_csv(init.TRAIN_DATA, sep=',', encoding='utf-8')

train.text = text.parse_column(train.text)
print(train)
# pprint(text.parse_data(init.TRAIN_DATA, init.TRAIN_TOKENS))
