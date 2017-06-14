import urllib.request
import urllib.error
import ftfy
from bs4 import BeautifulSoup


def process_html(url, root):
    try:
        try:
            try:
                url.encode('ascii')
                html = urllib.request.urlopen(url)
                final_url = html.geturl()
                # if not (final_url == url):
                #     print('redirected to %s' % final_url)
                soup = BeautifulSoup(html, 'lxml')
                title = soup.find('title')
                # print(title)

                links = []
                body = soup.find('body')

                # Beginning of acceptable children link
                first = (url, root, '/')
                # Ending of non-acceptable children link
                last = ('.jpg', '.xls', '.xlsx', '.pdf', '.png', '.doc', '.docx',
                        '.ppt', '.mp4', '.pptx', '.ppsx', '.pps', '.zip',
                        '.JPG', '.XLS', '.XLSX', '.PDF', '.PNG', '.DOC', '.DOCX',
                        '.PPT', '.MP4', '.PPTX', '.PPSX', '.PPS', '.ZIP')

                # Kill all script and style elements
                for script in soup(['script', 'style']):
                    script.extract()  # rip it out

                # Get list of children links for visible text
                if body:
                    for link in body.find_all('a'):
                        if link.get('href') \
                                and link.get('href').startswith(first) \
                                and not link.get('href').endswith(last):
                            if link.get('href').startswith('/'):
                                if final_url[-1] == '/':
                                    address = final_url[:-1] + link.get('href')
                                else:
                                    address = final_url + link.get('href')
                            else:
                                address = link.get('href')
                            links.append(address)

                # Get text
                text = soup.get_text()
                text = ftfy.fix_text(text)
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

                return links, text

            except UnicodeEncodeError:
                print('bad characters in url')
                return [], []

        except urllib.error.URLError as err:
            print(url, ' has an URLError ', err.reason)
            return [], []

    except urllib.error.HTTPError as err:
        print(url, ' has an HTTPError ', err.reason)
        return [], []

