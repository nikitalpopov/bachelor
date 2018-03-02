import init
import scraper
import text
import numpy
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
        if url.startswith('mailto:'):
            raise ValueError
        urllib.request.urlopen(url)

    except ValueError:
        # print(fg(1) + 'ERR' + attr(0), url, fg(1) + 'is invalid url' + attr(0))
        return False

    except UnicodeEncodeError:
        # print(fg(1) + 'ERR' + attr(0), url, fg(1) + 'has bad characters' + attr(0))
        return False

    except TimeoutError:
        # print(fg(1) + 'ERR' + attr(0), url, fg(1) + ':: Operation timed out' + attr(0))
        return False

    except ConnectionResetError:
        # print(fg(1) + 'ERR' + attr(0), url, fg(1) + ':: Connection reset by peer' + attr(0))
        return False

    except urllib.error.HTTPError as err:
        # print(fg(1) + 'ERR' + attr(0), url, fg(1) + str(err.reason) + attr(0))
        return False

    except urllib.error.URLError as err:
        # print(fg(1) + 'ERR' + attr(0), url, fg(1) + str(err.reason) + attr(0))
        return False

    except:
        # print(fg(1) + 'ERR' + attr(0), url)
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
    # print(fg(6) + url + attr(0))

    # todo try to check whether link is cyrillic
    if root in url:
        if validate_url(url):
            # print(fg(2) + url + attr(0))
            return url
        else:
            if not url.endswith('/'):
                if validate_url(url + '/'):
                    # print(fg(2) + url + '/' + attr(0))
                    return url + '/'
            if url.startswith('https://'):
                if validate_url(url[:4] + url[5:]):
                    # print(fg(2) + url[:4] + url[5:] + attr(0))
                    return url[:4] + url[5:]
                else:
                    # print(fg(1) + 'invalid' + attr(0))
                    return None
            else:
                # print(fg(1) + 'invalid' + attr(0))
                return None
    else:
        parsed = get_root_domain(url)
        if parsed == '':
            if url.startswith('/'):  # '/link'
                if validate_url(root[:-1] + url):
                    # print(fg(2) + root[:-1] + url + attr(0))
                    return root[:-1] + url
                else:
                    # print(fg(1) + 'invalid' + attr(0))
                    return None
            else:  # 'link'
                if validate_url(root + url):
                    # print(fg(2) + root + url + attr(0))
                    return root + url
                else:
                    # print(fg(1) + 'invalid' + attr(0))
                    return None
        else:
            # print(fg(1) + 'invalid' + attr(0))
            return None


def flatten(nested_list):
    """Flatten nested list
        :param nested_list:
        :return nested_list:
    """
    if not nested_list:
        return nested_list
    if isinstance(nested_list[0], list):
        return flatten(nested_list[0]) + flatten(nested_list[1:])
    return nested_list[:1] + flatten(nested_list[1:])


def scrape(url, queue, roots):
    """Scrape data for given url
        :param url:
        :param queue:
        :param roots:
        :return result:
    """
    queue.loc[queue['url'] == url, 'status'] = '+'
    root = roots['root'].str.lower().apply(lambda x: x in url).to_frame()
    root = root[root.root]
    condition = (roots.loc[roots.index.isin(root[root.root].index), 'children'] > 0).values
    # print((roots.loc[roots.index.isin(root[root.root].index), 'children'] > 0).values)
    # print(condition[0])
    if len(condition) == 1 and condition[0]:
        parsed = scraper.parse_url(url)
        if parsed['type'] is not None:
            print(fg('green') + url + attr(0))
            roots.loc[root.index, 'children'] -= 1
            result = parsed

    try:
        result
    except NameError:
        return
    else:
        return result


def fix(child, roots):
    """Try to fix children url (relative or any other) to full-path-url with info about root and category
        :param child:
        :param roots:
        :return result:
    """
    link, root = child
    index = roots['root'].str.lower().apply(lambda x: x in root).to_frame()
    index = index[index.root]
    condition = (roots.loc[roots.index.isin(index[index.root].index), 'children'] > 0).values
    # print(condition[0])
    if len(condition) == 1 and condition[0]:
        check = fix_url(link, root)
        if check != '' and check is not None:
            # print(fg('yellow') + check + attr(0))
            # pprint(roots.loc[roots.index.isin(index.index), 'root'])
            result = (check,
                      roots.loc[roots.index.isin(index.index), 'root'].values[0],
                      roots.loc[roots.index.isin(index.index), 'category'].values[0])
            # pprint(result)

    try:
        result
    except NameError:
        return
    else:
        return result


def manage(queue, roots, dataframe):
    """Manage data for given websites
        :param queue:
        :param roots:
        :param dataframe:
        :return queue:
        :return dataframe:
    """
    # next((x for x in a if x in str), False)  # find first substring from list
    scraped = [x for x in
               init.parallel(scrape, [(url, queue, roots) for url in queue.loc[queue['status'] != '+', 'url']],
                             mode='starmap') if x is not None]
    # pprint(scraped)

    appendix = pandas.DataFrame.from_records(scraped).dropna(how='all')
    appendix['root'] = ''

    for _, root in roots.iterrows():
        appendix.loc[appendix['url'].str.contains(root.root), 'root'] = root.root
    dataframe = dataframe.append(appendix, ignore_index=True)

    children = []
    for root in appendix['url']:
        for links in appendix.loc[appendix.url == root, 'children']:
            for link in links:
                children.append((link, root))
    # pprint(children)
    # input('Press Enter to continue...')

    fixed = [x for x in init.parallel(fix, [(child, roots) for child in children], mode='starmap') if x is not None]
    # pprint(fixed)
    # input('Press Enter to continue...')
    # todo add changed children for parent link in appendix
    children = pandas.DataFrame\
        .from_records(fixed, columns=['url', 'root', 'category'])\
        .dropna(how='any')\
        .drop_duplicates(subset='url')
    children['status'] = '-'
    # pprint(children)
    # input('Press Enter to continue...')

    queue = queue.append(children, ignore_index=True)
    queue = queue[~queue.duplicated(subset=['url'], keep=False)]
    queue = queue.loc[~queue['root'].isin(roots.loc[roots['children'] <= 0, 'root'].values)]
    # pprint(queue)
    # pprint(queue.loc[queue['status'] == '-', 'root'].unique())
    # pprint(roots.loc[roots['children'] <= 0, 'root'].unique())
    # input('Press Enter to continue...')

    if (roots.equals(roots.loc[roots['children'] <= 0]) or queue.equals(queue.loc[queue['status'] == '+'])) or \
            numpy.array_equal(queue.loc[queue['status'] == '-', 'root'].unique(),
                              roots.loc[roots['children'] <= 0, 'root'].unique()):
        dataframe['purpose'] = ''
        dataframe['category'] = ''
        for i in roots.index:
            dataframe.loc[dataframe['root'] == roots['root'][i], 'category'] = roots['category'][i]
            dataframe.loc[dataframe['root'] == roots['root'][i], 'purpose'] = roots['purpose'][i]

        return queue, dataframe
    else:
        return manage(queue, roots, dataframe)
