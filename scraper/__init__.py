import manager
import mechanicalsoup
import ftfy
from bs4 import Comment
from pprint import pprint
from colored import fg, attr


def parse_url(url):
    if not manager.validate_url(url):

        return {'url': None, 'type': None, 'text': None, 'children': None, 'meta': None, 'title': None}

    browser = mechanicalsoup.StatefulBrowser(
        soup_config={'features': 'lxml'},
        raise_on_404=True
    )
    response = browser.open(url)
    actual_url = browser.get_url()

    print(fg(2) + str(response.status_code) + attr(0), actual_url)

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
        # if url != actual_url:
        #     print(url, '->', actual_url)
        # print(get_root_domain(actual_url))

        # Remove all comments
        for comments in webpage.findAll(text=lambda text: isinstance(text, Comment)):
            comments.extract()  # rip it out

        # Remove all script and style elements
        for script in webpage(['script', 'style']):
            script.extract()  # rip it out

        if webpage.find('meta') is not None:
            meta = webpage.find('meta')
        if webpage.find('title') is not None:
            title = webpage.find('title').text
        body = webpage.find('body')
        page_text = webpage.get_text()

        # Get all children links at webpage
        if body:
            for link in links:
                children.append(link.get('href'))
            children = [child for child in list(filter(None, list(set(children)))) if not child.startswith('#')]
            # pprint(children)
            # print(children)
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

        # pprint(page_text)

    result = {
        'url':      actual_url,
        'children': children,
        'type':     page_type,
        'meta':     meta,
        'title':    title,
        'text':     page_text
    }

    return result
