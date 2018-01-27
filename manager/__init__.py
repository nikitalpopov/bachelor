import text
import scraper
import pandas
import urllib.request
import urllib.error
from colored import fg, attr
from pprint import pprint


def validate_url(url):
    """Check if url is valid
        :param url: string with URL
        :return bool:
    """
    try:
        url.encode('ascii')
        urllib.request.urlopen(url)

    except ValueError:
        print(fg(1) + 'ERR' + attr(0), url, fg(1) + 'is invalid url' + attr(0))
        return False

    except UnicodeEncodeError:
        print(fg(1) + 'ERR' + attr(0), url, fg(1) + 'has bad characters' + attr(0))
        return False

    except urllib.error.HTTPError as err:
        print(fg(1) + 'ERR' + attr(0), url, fg(1) + str(err.reason) + attr(0))
        return False

    except urllib.error.URLError as err:
        print(fg(1) + 'ERR' + attr(0), url, fg(1) + str(err.reason) + attr(0))
        return False

    else:
        return True


def get_root_domain(url):
    """Get parents name to fetch with children
        :param url: string with URL
        :return string:
    """
    if url is None:
        return ''

    if text.find_between(url, 'http://', '/') != '':
        return text.find_between(url, 'http://', '/')
    else:
        if text.find_between(url, 'https://', '/') != '':
            return text.find_between(url, 'https://', '/')
        else:
            return ''


def fix_url(url, root):
    """Try to fix children URL
        :param url: string with URL
        :param root: string with root URL
        :return url:
    """
    if ~validate_url(url):
        parsed = get_root_domain(url)
        if parsed == '':
            if url.startswith('/'):  # '/link'
                url = root[:-1] + url
                if validate_url(url):
                    return url
                else:
                    return ''
            else:  # 'link'
                url = root + url
                if validate_url(url):
                    return url
                else:
                    return ''
        else:
            return ''
    else:
        if root in url:
            return url
        else:
            return ''


def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


def run(queue, roots, dataframe):
    # print(queue)
    # print(roots)
    # print(dataframe)
    scraped = [scraper.parse_url(url) for url in queue['url'].values]
    appendix = pandas.DataFrame.from_records(scraped)
    appendix = appendix.dropna(how='all')

    children = []
    for root in appendix['url']:
        print(root)
        for links in appendix.loc[appendix.url == root, 'children']:
            for link in links:
                print(link)
                children.append((link, root))
    pprint(children)

    children = [fix_url(link, root) for link, root in children]
    pprint(children)
    # @todo add 'category' and 'root'
    # train['category'] = pandas.Series([categories['category'][i] for i in roots.categories.values]).values
    # train['root'] = roots.values
    dataframe = dataframe.append(appendix)
    # print(dataframe)

    # run(queue, roots, dataframe)
