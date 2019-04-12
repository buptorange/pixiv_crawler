import requests
import re
import os
import json
import time
from pyquery import PyQuery as pq
real_root = os.path.realpath(__file__).split('pixiv.py')[0]
SAVE_PATH = ''
def get_cookie():
    with open(real_root+'/cookies.txt','r') as f:
        cookies={}
        for line in f.read().split(';'):
            name,value=line.strip().split('=',1)  #1代表只分割一次
            cookies[name]=value
        return cookies

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

def get_list():
    t = open(real_root+'/list.txt','r')
    list = []
    s = t.read().split('\n')
    for item in s:
        list.append(item)
    return list

rtn_cookies = get_cookie() #获取cookies.txt内容
count = 0 #下载图片数计数
list = get_list()#获取list.txt中画师id
proxies = {
    "http": "socks5://127.0.0.1:1080",
    'https': 'socks5://127.0.0.1:1080'
}
for ID in list:
    '''获取画师名，创建文件夹'''
    headers = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding':'gzip, deflate, sdch, br',
        'accept-language':'zh-CN,zh;q=0.8',
        'referer':'https://www.pixiv.net/bookmark.php?type=user',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
    }

    nameres = requests.get(headers = headers,proxies = proxies,cookies = rtn_cookies,url = 'https://www.pixiv.net/member_illust.php?id='+ID).content
    n = pq(nameres.decode())
    name = n('title').text().split('「')[1].split('」')[0]
    artist_folder = real_root+'/results/' + name + '_' + ID + '/'
    if not os.path.exists(artist_folder):
        os.makedirs(artist_folder)
    SAVE_PATH = artist_folder


    '''获取query string parameters列表(all.ajax)'''
    headers = {
        'accept':'application/json',
        'accept-encoding':'gzip, deflate, sdch, br',
        'accept-language':'zh-CN,zh;q=0.8',
        'referer':'https://www.pixiv.net/member_illust.php?id='+ID,
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
        'x-user-id':'17793431'
    }
    res = requests.get(headers = headers,proxies = proxies,cookies = rtn_cookies,url='https://www.pixiv.net/ajax/user/'+ID+'/profile/all')
    doc = res.content.decode()
    a = json.loads(doc)
    b = a['body']['illusts']
    illusts = []
    for key,id in b.items():
        illusts.append(key)
    multi_illu = []
    if len(illusts)>48:
        k = len(illusts)//48
        for i in range(k+1):
            start = i*48
            end = min((i+1)*48,len(illusts))
            multi_illu.append(illusts[start:end])
    else:
        multi_illu.append(illusts)
    print('illust总数',len(illusts))

    for epoch in multi_illu:
        i = 0
        print('epoch = ',epoch)
        '''获取画师作品信息ajax 48个一组'''
        headers = {
            'accept':'application/json',
            'accept-encoding':'gzip, deflate, sdch, br',
            'accept-language':'zh-CN,zh;q=0.8',
            'referer':'https://www.pixiv.net/member_illust.php?id='+ID,
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
            'x-user-id':'17793431'
        }
        param = {'ids[]':epoch,'is_manga_top':0}


        res = requests.get(headers = headers,proxies = proxies,cookies = rtn_cookies,url='https://www.pixiv.net/ajax/user/'+ID+'/profile/illusts',params=param)
        #print(res.url)
        doc = res.content.decode()
        a = json.loads(doc)
        get_dict = {}
        b = a['body']['works']
        redund = 1
        titles = []
        for key,illust in b.items():
            title = validateTitle(illust['title'])
            titles.append(title)
            if len(titles)!=len(set(titles)):
                titles[-1] = titles[-1] +'_'+str(redund)
                redund += 1
            url_small = illust['url']
            url = 'https://i.pximg.net/img-original/img/' + url_small.split('https://i.pximg.net/c/250x250_80_a2/img-master/img/')[1].split('_squ')[0] + '.jpg'
            id = illust['id']
            refer_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + id
            get_dict[refer_url] = (url,title)

        '''根据时间和id获取图片'''
        headers = {
            'accept':'image/webp,image/*,*/*;q=0.8',
            'accept-encoding':'gzip, deflate, sdch, br',
            'accept-language':'zh-CN,zh;q=0.8',
            'referer':'',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
        }

        for refer,(url,title) in get_dict.items():
            headers['referer'] = refer
            response = requests.get(headers = headers,proxies = proxies,url = url).content
            if len(response)<70:
                #print(response)
                url = url.replace('.jpg','.png')
                f = open(SAVE_PATH + title + '.png', 'wb')
                response = requests.get(headers=headers, proxies = proxies,url=url).content
            else:
                f = open(SAVE_PATH+title+'.jpg','wb')
            f.write(response)
            print('total=',count)
            count += 1
            f.close()
            time.sleep(0.1)
            i += 1
