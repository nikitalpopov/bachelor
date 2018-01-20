import init
import scraper
import text
from pprint import pprint


print('Getting array of urls...')
# Get all urls from .txt to array of strings
children_count, categories = init.from_file(init.URLS)

# init.parallel(scraper.parse_url, [categories.iloc[0]['url']])  # [categories.iloc[0]['url']] to get first url,
urls = init.parallel(scraper.parse_url, categories['url'])  # categories['url'] for all urls

# pprint([x for x in urls])
roots = [scraper.get_root_domain(url) for url in [x['url'] for x in urls if x['url'] is not None]]
# pprint(roots)
