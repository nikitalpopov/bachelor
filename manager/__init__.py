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
        # if 'mailto://' in url:
        #     print(fg(1) + 'ERR' + attr(0), url, fg(1) + 'is "mailto://" url' + attr(0))
        #     return False

        url.encode('ascii')
        urllib.request.urlopen(url)

    except ValueError:
        print(fg(1) + 'ERR' + attr(0), url, fg(1) + 'is invalid url' + attr(0))
        return False

    except UnicodeEncodeError:
        print(fg(1) + 'ERR' + attr(0), url, fg(1) + 'has bad characters' + attr(0))
        return False

    except TimeoutError:
        print(fg(1) + 'ERR' + attr(0), url, fg(1) + ':: Operation timed out' + attr(0))
        return False

    except ConnectionResetError:
        print(fg(1) + 'ERR' + attr(0), url, fg(1) + ':: Connection reset by peer' + attr(0))
        return False

    except urllib.error.HTTPError as err:
        print(fg(1) + 'ERR' + attr(0), url, fg(1) + str(err.reason) + attr(0))
        return False

    except urllib.error.URLError as err:
        print(fg(1) + 'ERR' + attr(0), url, fg(1) + str(err.reason) + attr(0))
        return False

    except:
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
    print(fg(6) + url + attr(0))
    if ~validate_url(url):
        parsed = get_root_domain(url)
        if parsed == '':
            if url.startswith('/'):  # '/link'
                if validate_url(root[:-1] + url):
                    print(fg(2) + root[:-1] + url + attr(0))
                    return root[:-1] + url
                else:
                    print(fg(1) + 'invalid' + attr(0))
                    return None
            else:  # 'link'
                if validate_url(root + url):
                    print(fg(2) + root + url + attr(0))
                    return root + url
                else:
                    print(fg(1) + 'invalid' + attr(0))
                    return None
        else:
            print(fg(1) + 'invalid' + attr(0))
            return None
    else:
        if root in url:
            print(fg(2) + url + attr(0))
            return url
        else:
            print(fg(1) + 'invalid' + attr(0))
            return None


def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


def manage(queue, roots, dataframe):
    print(queue)
    # print(roots)
    # print(dataframe)
    scraped = [run(url) for url in queue.loc[queue['status'] != '+', 'url']]
    queue.loc[queue['status'] != '+', 'status'] = '+'
    # pprint(scraped)
    appendix = pandas.DataFrame.from_records(scraped).dropna(how='all')
    # pprint(appendix)

    children = []
    for root in appendix['url']:
        # print(root)
        for links in appendix.loc[appendix.url == root, 'children']:
            for link in links:
                # print(link)
                children.append((link, root))
    # pprint(children)

    fixed = []
    for link, root in children:
        check = fix_url(link, root)
        if check != '':
            fixed.append((check, root))

    children = pandas.DataFrame\
        .from_records(fixed, columns=['url', 'root'])\
        .dropna(how='any')\
        .drop_duplicates(subset='url')
    children['status'] = '-'
    pprint(children)
    queue = queue.append(children).drop_duplicates()
    print(queue)
    # @todo add 'category' and 'root'
    # appendix['category'] = pandas.Series([categories['category'][i] for i in roots.categories.values]).values
    # appendix['root'] = roots.values
    dataframe = dataframe.append(appendix)

    # run(queue, roots, dataframe)
    return queue, dataframe


def run(url):
    scraped = scraper.parse_url(url)

    return scraped
