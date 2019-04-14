import re
import os
import sys
import urllib
import requests
import threading
from pyquery import PyQuery as pq

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': '__cfduid=d671f919b7adeda699a235d8713b40fee1554992425',
    'upgrade-insecure-requests': '1',
    'Connection': 'keep-alive',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}

proxies = {
    'http':'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}

def get_pics(detail_url,headers,dst_folder,abstract_url):
    head3 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    }
    head3['referer'] = abstract_url
    #print('request for = ',detail_url,'refer = ',abstract_url)
    res = requests.get(headers=head3, url=detail_url, proxies=proxies, timeout=(3, 10)).content
    detail_html = pq(res.decode())
    pic_real_url = detail_html('#img').attr('src')
    name = pic_real_url.split('/')[-1]
    host = re.compile('\d+\.\d+\.\d+\.\d+:\d+').findall(pic_real_url)
    print('host=', host)
    if host:
        headers['host'] = host[0]
    else:
        headers['host'] = re.compile('\d+\.\d+\.\d+\.\d+').findall(pic_real_url)[0]
    pic = requests.get(headers=headers, url=pic_real_url, proxies=proxies, timeout=(3, 10)).content
    with open(os.path.join(dst_folder,name),'wb') as f:
        f.write(pic)

def get_a_hon(abstract_url):
    head2 = {
    'Cookie': '__cfduid=d42a724d1c73ca4064a332879938f5eb71555041094',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Host': 'e-hentai.org',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15',
    'Accept-Language': 'zh-cn',
    'Accept-Encoding': 'br, gzip, deflate',
    'Connection': 'keep-alive'
    }
    res = requests.get(headers = head2,url = abstract_url,proxies = proxies,timeout = (10,10))
    print(res.url)
    res = res.content
    small_pic_urls = []
    root = os.path.realpath(__file__).split('ehentai.py')[0] + 'hon/'

    abstract_html = pq(res.decode())
    title = abstract_html('#gj')[0].text
    if title == None:
        title = abstract_html('#gn')[0].text
    small_pic_objs = abstract_html("a[href*='https://e-hentai.org/s/']")
    father = pq(abstract_html(".ptb")[0])
    td_2 = pq(father("td")[-2])
    end_page = td_2("a")[0].text

    for i in end_page:
        urls = [i.attrib['href'] for i in small_pic_objs]
        small_pic_urls += urls

    dst_folder = os.path.join(root,title)
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    t_s = []
    for detail_url in small_pic_urls:
        t_s.append(
            threading.Thread(target=get_pics, args=[detail_url, headers, dst_folder, abstract_url], name='LoopThread'))
        t_s[-1].start()
        # print('start')
    for q in t_s:
        q.join()




search_url = 'https://e-hentai.org/?f_search=深崎暮人'
print('one or search? (one/search)')
select = input()
if select == 'one':
    one_url = input()
    get_a_hon(one_url)
elif select == 'search':
    search_url = input()
    f_search = search_url.split('f_search=')[1]
    f_search = urllib.parse.unquote(f_search)
    all_hon_urls = []
    headers['host'] = 'e-hentai.org'
    headers['referer'] = 'https://e-hentai.org/'

    res = requests.get(headers = headers,url = search_url,proxies = proxies,timeout = (10,10)).content
    abstract_html = pq(res.decode())
    fafather = pq(abstract_html('.ido')[0])

    father = pq(fafather(".ptb")[0])
    td_2 = pq(father("td")[-2])
    end_page_num = td_2("a")[0].text

    for k in range(int(end_page_num)):
        res = requests.get(headers = headers,url = 'https://e-hentai.org/',proxies = proxies,timeout = (10,10),params={'page':k,'f_search':f_search})
        #print(res.url)
        res = res.content
        search_html = pq(res.decode())
        table = pq(search_html('.glname'))
        page_hon_objs = table('a')
        page_hon_urls = [(i.attrib['href'],k) for i in page_hon_objs]
        all_hon_urls += page_hon_urls
    print('book_numbers:',len(all_hon_urls))
    for abstract_url,k in all_hon_urls:
        get_a_hon(abstract_url)

