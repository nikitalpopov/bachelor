import urllib.request
import urllib.error
import mechanicalsoup
import ftfy
from bs4 import Comment
from pprint import pprint

import text


def validate_url(url):
    """Check if url is valid
        :param url: string with URL
        :return bool:
    """
    try:
        url.encode('ascii')
        urllib.request.urlopen(url)

    except ValueError:
        print(url, 'is invalid url')
        return False

    except UnicodeEncodeError:
        print(url, 'has bad characters')
        return False

    except urllib.error.HTTPError as err:
        print(url, 'has an HTTPError:', err.reason)
        return False

    except urllib.error.URLError as err:
        print(url, 'has an URLError:', err.reason)
        return False

    else:
        return True


def get_root_domain(url):
    """Get parents name to fetch with children
        :param url: string with URL
        :return string:
    """
    if text.find_between(url, 'http://', '/') != '':
        return text.find_between(url, 'http://', '/')
    else:
        return text.find_between(url, 'https://', '/')


def parse_url(url):
    actual_url = None
    page_type = 1
    text = None

    if not validate_url(url):
        page_type = None
        print()
        return {'actual_url': actual_url, 'type': page_type, 'text': text}

    browser = mechanicalsoup.StatefulBrowser(
        soup_config={'features': 'lxml'},
        raise_on_404=True
    )
    response = browser.open(url)
    actual_url = browser.get_url()

    print(response.status_code, actual_url)

    if response.status_code >= 400:
        page_type = 0
        browser.close()
        print()
        return {'actual_url': actual_url, 'type': page_type, 'text': text}

    webpage = browser.get_current_page()
    links = browser.links()

    browser.close()

    if ("text/html" in response.headers["content-type"]) and webpage:
        # if url != actual_url:
        #     print(url, '->', actual_url)
        # print(get_root_domain(actual_url))

        # Remove all comments
        for comments in webpage.findAll(text=lambda text: isinstance(text, Comment)):
            comments.extract()  # rip it out

        # Remove all script and style elements
        for script in webpage(['script', 'style']):
            script.extract()  # rip it out

        meta = webpage.find('meta')
        title = webpage.find('title')
        body = webpage.find('body')
        text = webpage.get_text()

        # Get all children links at webpage
        children = []
        if body:
            for link in links:
                children.append(link.get('href'))
            children = list(set(children))
            # pprint(children)
            # print(children)
        else:
            page_type = 0

        # If needed to fix encoding
        # text = ftfy.fix_text(text)
        # print(text.strip())

        if text:
            # Break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split(' '))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            text = text.splitlines()
            text = list(dict.fromkeys(text))
        else:
            text = []
            page_type = 0
        text = ' '.join(text)

        # pprint(text)
        print()

    result = {'url': actual_url, 'type': page_type, 'text': text}

    return result
