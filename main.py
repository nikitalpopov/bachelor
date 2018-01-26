import classification
import init
import pandas
import scraper
import text
from pprint import pprint

print('Getting array of urls...')
# Get all urls from .txt to array of strings
children_count, categories = init.from_file(init.URLS)

# Results of scraping: 'url', 'type', 'text'
# scraped = init.parallel(scraper.parse_url, [categories.iloc[0]['url']])  # get first url
scraped = init.parallel(scraper.parse_url, categories['url'])  # all urls
# pprint([x for x in scraped])

# List of available websites
clean_roots = pandas.Series(
    [scraper.get_root_domain(url) for url in [x['url'] for x in scraped if x['url'] is not None]]
)
roots = pandas.Series([url for url in [x['url'] for x in scraped if x['url'] is not None]])
# pprint(roots)
print()

print('Parsing data...')
# Dataframe with scraped data
train = pandas.DataFrame.from_records(scraped)
train = train.dropna(how='all')
# pprint(train)
train['category'] = pandas.Series([categories['category'][i] for i in train.index.values]).values
train['root'] = roots.values
train.to_csv(init.TRAIN_DATA, sep=',', encoding='utf-8', index=False)

train = text.parse_text(init.TRAIN_DATA, init.TRAIN_TOKENS, 'pymorphy')
print(train)
# pprint(text.parse_data(init.TRAIN_DATA, init.TRAIN_TOKENS))
print()

print('Classification...')
parameters = [
    (train.text, train.category, init.UNIVERSITY),
    (train.text, train.category, init.SCIENCE),
    (train.text, train.category, init.OTHER)
]
prediction = init.parallel(classification.predict, parameters)
predicted = {
    'university': prediction[0],
    'science':    prediction[1],
    'other':      prediction[2]
}
print(predicted)
print()

# Exit
print('The end')
init.notify('🛠 bachelor', 'script has finished')
