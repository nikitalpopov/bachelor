import mechanicalsoup
from bs4 import Comment
from pprint import pprint


def parse_url(url):
    url.encode('ascii')
    browser = mechanicalsoup.StatefulBrowser(
        soup_config={'features': 'lxml'},
        raise_on_404=True
    )
    response = browser.open(url)
    actual_url = browser.get_url()

    print(response.status_code, ' ', actual_url)

    if response.status_code >= 400:
        browser.close()
        return

    webpage = browser.get_current_page()
    links = browser.links()

    browser.close()

    if ("text/html" in response.headers["content-type"]) and webpage:
        # print(url, ' -> ', actual_url)

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

        # If needed to fix encoding
        # text = ftfy.fix_text(text)
        # print(text.strip())

        if text:
            # Break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            text = text.splitlines()
            text = list(dict.fromkeys(text))
        else:
            text = []
        text = ' '.join(text)

        pprint(text)

    return
