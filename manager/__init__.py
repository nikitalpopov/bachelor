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
        :return url:
    """
    print(fg(6) + url + attr(0))

    # @todo do less requests
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
    print(roots)
    # print(dataframe)

    # next((x for x in a if x in str), False)  # find first substring from list
    scraped = []
    for url in queue.loc[queue['status'] != '+', 'url']:
        if roots.loc[roots['root'].str.match('.*[url].*'), 'children'][0] == 0:
            url = ''
        else:
            queue.loc[queue['url'] == url, 'status'] = '+'
            for i, row in roots.iterrows():
                if row['root'] in url:
                    roots.loc[i, 'children'] -= 1
        scraped.append(scraper.parse_url(url))

    # pprint(scraped)
    appendix = pandas.DataFrame.from_records(scraped).dropna(how='all')
    appendix['root'] = ''

    for _, root in roots.iterrows():
        # print(appendix.loc[appendix['url'].str.contains(root.root), 'root'])
        appendix.loc[appendix['url'].str.contains(root.root), 'root'] = root.root

    children = []
    for root in appendix['url']:
        for links in appendix.loc[appendix.url == root, 'children']:
            for link in links:
                children.append((link, root))
                # pprint(children)

    fixed = []
    for link, root in children:
        check = fix_url(link, root)
        if check != '':
            for i, row in roots.iterrows():
                if row['root'] in link:
                    # @todo skips a lot of children
                    roots.loc[i, 'children'] -= 1
            # @todo if root.children == 0, clear queue for this root and never add new links
            fixed.append((check, roots.loc[roots['root'].str.match('.*[root].*'), 'root'][0], roots.loc[roots['root'].str.match('.*[root].*'), 'category'][0]))
            # @todo add change children for parent link in appendix
    # pprint(fixed)

    children = pandas.DataFrame\
        .from_records(fixed, columns=['url', 'root', 'category'])\
        .dropna(how='any')\
        .drop_duplicates(subset='url')
    children['status'] = '-'
    queue = queue.append(children[['url', 'status']], ignore_index=True).drop_duplicates()
    pprint(appendix)
    print(queue)
    print(roots)
    # @todo add 'category'
    # appendix['category'] = pandas.Series([categories['category'][i] for i in roots.categories.values]).values
    # appendix['root'] = roots.values
    dataframe = dataframe.append(appendix)
    pprint(dataframe)

    exit()
    if queue.loc[queue['status'] == '-', 'status'].shape[0] == 0:
        return queue, dataframe
    else:
        return manage(queue, roots, dataframe)
