import init
import scraper
import text
import numpy
import pandas
import requests
import urllib.request
import urllib.error
from colored import fg, attr
from datetime import datetime
from pprint import pprint
from urllib import parse


def validate_url(url):
    """Check if url is valid
        :param url: string with URL
        :return bool:
    """
    try:
        # url.encode('ascii')
        if url.startswith('mailto:'):
            raise ValueError
        # urllib.request.urlopen(url)
        # r = requests.get(url, timeout=10)
        # r.raise_for_status()
        result = scraper.get_actual_url(url)

    except ValueError:
        # print(fg('blue') + '[' + datetime.now().time() + ']' + attr(0),
        #       fg(1) + 'ERR' + attr(0), url, fg(1) + 'is invalid url' + attr(0))
        return False

    except UnicodeEncodeError:
        # print(fg('blue') + '[' + datetime.now().time() + ']' + attr(0),
        #       fg(1) + 'ERR' + attr(0), url, fg(1) + 'has bad characters' + attr(0))
        return False

    except TimeoutError:
        # print(fg('blue') + '[' + datetime.now().time() + ']' + attr(0),
        #       fg(1) + 'ERR' + attr(0), url, fg(1) + ':: Operation timed out' + attr(0))
        return False

    except ConnectionResetError:
        # print(fg('blue') + '[' + datetime.now().time() + ']' + attr(0),
        #       fg(1) + 'ERR' + attr(0), url, fg(1) + ':: Connection reset by peer' + attr(0))
        return False

    except requests.exceptions.HTTPError as err:
        # print(fg('blue') + '[' + datetime.now().time() + ']' + attr(0),
        #       fg(1) + 'ERR' + attr(0), url, fg(1) + str(err) + attr(0))
        return False

    except requests.exceptions.RequestException as err:
        # print(fg('blue') + '[' + datetime.now().time() + ']' + attr(0),
        #       fg(1) + 'ERR' + attr(0), url, fg(1) + str(err) + attr(0))
        return False

    # except urllib.error.HTTPError as err:
    #     # print(fg('blue') + '[' + datetime.now().time() + ']' + attr(0),
    #     #       fg(1) + 'ERR' + attr(0), url, fg(1) + str(err.reason) + attr(0))
    #     return False
    #
    # except urllib.error.URLError as err:
    #     # print(fg('blue') + '[' + datetime.now().time() + ']' + attr(0),
    #     #       fg(1) + 'ERR' + attr(0), url, fg(1) + str(err.reason) + attr(0))
    #     return False

    except:
        # print(fg('blue') + '[' + datetime.now().time() + ']' + attr(0), fg(1) + 'ERR' + attr(0), url)
        return False

    else:
        if result:
            return True
        else:
            return False


def get_root(url):
    split = parse.urlsplit(url)
    netloc = split.netloc
    path = split.path
    if netloc.startswith('www.'):
        netloc = netloc[4:]
    return (netloc + path.rstrip('/')).split('/')[0]


def get_root_domain(url):
    """Get parents name to fetch with children
        :param url: string with URL
        :return string:
    """
    if url is None:
        return ''

    http = text.find_between(url, 'http://', '/')
    https = text.find_between(url, 'https://', '/')
    if http != '':
        if http.startswith('www.'):
            return http[4:]
        else:
            return http
    else:
        if https != '':
            if https.startswith('www.'):
                return https[4:]
            else:
                return https
        else:
            return ''


def fix_url(url, root):
    """Try to fix children URL
        :param url: string with URL
        :param root: string with root URL
        :return url: fixed accessible url or None
    """
    if root in url:
        if validate_url(url):
            # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg(2) + url + attr(0))
            return url
        else:
            if not url.endswith('/'):
                if validate_url(url + '/'):
                    # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg(2) + url + '/' + attr(0))
                    return url + '/'
            if url.startswith('https://'):
                if validate_url(url[:4] + url[5:]):
                    # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0),
                    #       fg(2) + url[:4] + url[5:] + attr(0))
                    return url[:4] + url[5:]
                else:
                    # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg(1) + 'invalid' + attr(0))
                    return None
            else:
                # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg(1) + 'invalid' + attr(0))
                return None
    else:
        parsed = get_root_domain(url)
        if parsed == '':
            if url.startswith('/'):  # '/link'
                if validate_url(root[:-1] + url):
                    # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0),
                    #       fg(2) + root[:-1] + url + attr(0))
                    return root[:-1] + url
                else:
                    # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg(1) + 'invalid' + attr(0))
                    return None
            else:  # 'link'
                if url.startswith('./'):  # '/link'
                    if validate_url(root + url[2:]):
                        # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0),
                        #       fg(2) + root[:-1] + url + attr(0))
                        return root[:-1] + url
                    else:
                        # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0),
                        #       fg(1) + 'invalid' + attr(0))
                        return None
                elif validate_url(root + url):
                    # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg(2) + root + url + attr(0))
                    return root + url
                else:
                    # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg(1) + 'invalid' + attr(0))
                    return None
        else:
            # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), fg(1) + 'invalid' + attr(0))
            return None


def scrape(url, queue, roots):
    """Scrape data for given url
        :param url:
        :param queue:
        :param roots:
        :return result:
    """
    # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0))
    queue.loc[queue['url'] == url, 'status'] = '+'
    root = get_root(url)
    if len(roots.loc[roots[roots.root == root].index, "children"] > 0) == 1 and \
            (roots.loc[roots[roots.root == root].index, "children"] > 0).values[0]:
        parsed = scraper.parse_url(url)
        if parsed['type'] is not None:
            roots.loc[roots[roots.root == root].index, "children"] -= 1
            return parsed
    return


def fix(child, roots):
    """Try to fix children url (relative or any other) to full-path-url with info about root and category
        :param child:
        :param roots:
        :return result:
    """
    # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0))
    link, root_url = child
    root = get_root(root_url)
    if len(roots[roots.root == root].children > 0) == 1 and (roots[roots.root == root].children > 0).values[0]:
        check = fix_url(link, root_url)
        if check != '' and check is not None:
            return (check,
                    roots.loc[roots[roots.root == root].index].root.values[0],
                    roots.loc[roots[roots.root == root].index].category.values[0])
    return


def manage(queue, roots, dataframe):
    """Manage data for given websites
        :param queue:
        :param roots:
        :param dataframe:
        :return queue:
        :return dataframe:
    """
    # next((x for x in a if x in str), False)  # find first substring from list
    scraped = []
    while len(queue.loc[queue['status'] != '+']) > 0:
        # if 200 > len(queue.loc[queue['status'] != '+']):
        #     j = len(queue.loc[queue['status'] != '+'])
        # else:
        #     j = 200
        # scraped = [x for x in init.parallel(scrape, [(url, queue, roots) for url in
        #                                              queue.loc[queue['status'] != '+', 'url'][0:j]], mode='starmap')
        #            if x is not None]
        scraped = [x for x in
                   init.parallel(scrape, [(url, queue, roots) for url in queue.loc[queue['status'] != '+', 'url']],
                                 mode='starmap') if x is not None]
    # pprint(scraped)

    appendix = pandas.DataFrame.from_records(scraped).dropna(how='all')
    appendix['root'] = ''
    appendix['depth'] = 1. / init.DEPTH
    init.DEPTH += 1

    children = []
    if len(appendix):
        for _, root in roots.iterrows():
            appendix.loc[appendix['url'].str.contains(root.root), 'root'] = root.root
        dataframe = dataframe.append(appendix, ignore_index=True)

        for root in appendix['url']:
            for links in appendix.loc[appendix.url == root, 'children']:
                for link in links:
                    children.append((link, root))

    # fixed = []
    # for i in range(int(len(children) / 200)):
    #     if i * 200 + 199 > len(children):
    #         j = len(children)
    #     else:
    #         j = i * 200 + 199
    #     fixed.append([x for x in
    #                   init.parallel(fix, [(child, roots) for child in children[(i * 200):j]], mode='starmap')
    #                   if x is not None])
    fixed = [x for x in init.parallel(fix, [(child, roots) for child in children], mode='starmap') if x is not None]
    # fixed = flatten(fixed)
    # todo add changed children for parent link in appendix
    children = pandas.DataFrame\
        .from_records(fixed, columns=['url', 'root', 'category'])\
        .dropna(how='any')\
        .drop_duplicates(subset='url')
    children['status'] = '-'

    queue = queue.append(children, ignore_index=True)
    queue = queue[~queue.duplicated(subset=['url'], keep=False)]
    queue = queue.loc[~queue['root'].isin(roots.loc[roots['children'] <= 0, 'root'].values)]

    dataframe['purpose'] = ''
    dataframe['category'] = ''
    for i in roots.index:
        dataframe.loc[dataframe['root'] == roots['root'][i], 'category'] = roots['category'][i]
        dataframe.loc[dataframe['root'] == roots['root'][i], 'purpose'] = roots['purpose'][i]

    return queue, roots, dataframe
