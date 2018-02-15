import init
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
        if url.startswith('mailto:'):
            raise ValueError
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
    print(fg(6) + url + attr(0))

    # todo try to check whether link is cyrillic
    if url[-1] != '/':
        url += '/'

    if root in url:
        if validate_url(url):
            print(fg(2) + url + attr(0))
            return url
        else:
            if url.startswith('https://'):
                if validate_url(url[:4] + url[5:]):
                    print(fg(2) + url[:4] + url[5:] + attr(0))
                    return url[:4] + url[5:]
                else:
                    print(fg(1) + 'invalid' + attr(0))
                    return None
            else:
                print(fg(1) + 'invalid' + attr(0))
                return None
    else:
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
    queue.loc[queue['url'] == url, 'status'] = '+'
    if roots.loc[roots['root'].str.match('.*[url].*'), 'children'][0] > 0:
        result = scraper.parse_url(url)
        for i, row in roots.iterrows():
            if row['root'] in url:
                roots.loc[i, 'children'] -= 1

    try:
        result
    except NameError:
        return
    else:
        return result


def fix(child, roots):
    link, root = child
    check = fix_url(link, root)
    if check != '' and check is not None:
        for i, line in roots.iterrows():
            if line['root'] in check:
                if roots.loc[i, 'children'] > 0:
                    result = (check,
                              roots.loc[i, 'root'],
                              roots.loc[i, 'category'])

    try:
        result
    except NameError:
        return
    else:
        return result


def manage(queue, roots, dataframe):
    pprint(queue)
    exit()
    # next((x for x in a if x in str), False)  # find first substring from list
    scraped = [x for x in
               init.parallel_starmap(scrape, [(url, queue, roots) for url in queue.loc[queue['status'] != '+', 'url']])
               if x is not None]

    appendix = pandas.DataFrame.from_records(scraped).dropna(how='all')
    appendix['root'] = ''

    for _, root in roots.iterrows():
        appendix.loc[appendix['url'].str.contains(root.root), 'root'] = root.root
    dataframe = dataframe.append(appendix)

    children = []
    for root in appendix['url']:
        for links in appendix.loc[appendix.url == root, 'children']:
            for link in links:
                children.append((link, root))

    fixed = [x for x in init.parallel_starmap(fix, [(child, roots) for child in children]) if x is not None]
    # todo if root.children == 0, clear queue for this root and never add new links
    # todo add changed children for parent link in appendix

    children = pandas.DataFrame\
        .from_records(fixed, columns=['url', 'root', 'category'])\
        .dropna(how='any')\
        .drop_duplicates(subset='url')
    children['status'] = '-'
    queue = queue.append(children, ignore_index=True).drop_duplicates()

    if roots.equals(roots.loc[roots['children'] <= 0]) or queue.equals(queue.loc[queue['status'] == '+']):
        return queue, dataframe
    else:
        return manage(queue, roots, dataframe)
