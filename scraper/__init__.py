import init
import manager
import ftfy
import lxml.html
import mechanicalsoup
import requests
from adblock import AdRemover
from bs4 import BeautifulSoup, Comment
from colored import fg, attr
from datetime import datetime
from lxml.etree import tostring


def get_actual_url(url):
    try:
        r = requests.get(url, timeout=100)
        print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), str(r.status_code), url)
    except:
        return None

    if r.url and r.status_code == requests.codes.ok:
        return r.url
    else:
        return None


def parse_url(url):
    if not manager.validate_url(url):

        return {'url': None, 'type': None, 'text': None, 'children': None, 'meta': None, 'title': None}

    browser = mechanicalsoup.StatefulBrowser(
        soup_config={'features': 'lxml'},
        raise_on_404=True
    )
    try:
        response = browser.open(url)
        actual_url = browser.get_url()
    except:
        return {'url': None, 'type': None, 'text': None, 'children': None, 'meta': None, 'title': None}

    print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0),
          fg(2) + str(response.status_code) + attr(0), actual_url)

    if browser.get_current_page() and response.status_code < 400:
        webpage = browser.get_current_page()
        links = browser.links()

        browser.close()
    else:
        browser.close()

        return {'url': actual_url, 'type': 0, 'text': '', 'children': [], 'meta': '', 'title': ''}

    page_type = 1
    page_text = ''
    children = []
    meta = ''
    title = ''

    if ("text/html" in response.headers["content-type"]) and webpage:
        # Remove ads
        remover = AdRemover(*['data/' + rule.rsplit('/', 1)[-1] for rule in init.ADBLOCK_RULES])
        try:
            html = requests.get(url).text
            if html:
                document = lxml.html.document_fromstring(html)
                remover.remove_ads(document)
            else:
                return {'url': actual_url, 'type': 0, 'text': '', 'children': [], 'meta': '', 'title': ''}
            clean_html = tostring(document).decode("utf-8")
            webpage = BeautifulSoup(clean_html, 'lxml')
        except ValueError:
            print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg('red') + url + attr(0))
            print('ValueError')
        except TypeError:
            print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg('red') + url + attr(0))
            print('TypeError')
        except:
            print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg('red') + url + attr(0))
            print('Some error with removing ads')

        # Remove all comments
        for comments in webpage.findAll(text=lambda text: isinstance(text, Comment)):
            comments.extract()  # rip it out

        # Remove all script and style elements
        for script in webpage(['script', 'style']):
            script.extract()  # rip it out

        # temp = webpage.find('meta')
        for tag in webpage.find_all("meta"):
            if tag is not None:
                try:
                    meta = ' '.join([meta, tag['content'], tag['keywords'], tag['description']])
                except KeyError:
                    pass
        temp = webpage.find('title')
        if temp is not None:
            title = temp.text
        body = webpage.find('body')
        page_text = webpage.get_text(" ")

        # Get all children links at webpage
        if body:
            for link in links:
                children.append(link.get('href'))
            children = [child for child in list(filter(None, list(set(children)))) if not child.startswith('#')]
            # pprint(children)
        else:
            page_type = 0

        # If needed to fix encoding
        # page_text = ftfy.fix_text(page_text)
        # print(page_text.strip())

        if page_text:
            # Break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in page_text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split(' '))
            # Drop blank lines
            page_text = '\n'.join(chunk for chunk in chunks if chunk)
            page_text = page_text.splitlines()
            page_text = list(dict.fromkeys(page_text))
        else:
            page_text = []
            page_type = 0
        page_text = ' '.join(page_text)

    result = {
        'url':      actual_url,
        'children': children,
        'type':     page_type,
        'meta':     meta,
        'title':    title,
        'text':     page_text
    }

    return result
