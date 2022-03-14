# -- coding:utf-8 --
import os
import urllib.request
import ssl
import json


def get_svgrepo_svgs(words, img_num):

    return get_cached_svgs(words, img_num)
    '''
    ssl._create_default_https_context = ssl._create_unverified_context
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    }
    url_list = []
    svg_list = []
    url = f'http://api.svgrepo.com/search/?term={words}&limit=50&start=0'
    while True:
        print(url)
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        res_json_str = response.read().decode('utf-8')
        res_json_str = res_json_str.replace('\\', '\\\\')
        res_json = json.loads(res_json_str)
        # print(res_json)
        obj_list = res_json['icons']
        next_url = res_json['next']
        for it in obj_list:
            svg_url = f"https://www.svgrepo.com/show/{it['id']}/burger.svg"
            request = urllib.request.Request(svg_url, headers=headers)
            print(len(url_list))
            response = urllib.request.urlopen(request)
            res_str = response.read().decode('utf-8')
            url_list.append(svg_url)
            print(len(url_list))
            svg_list.append(res_str)
            if len(url_list) >= int(img_num):
                break
        if len(url_list) >= int(img_num):
                break
        url = next_url
    return url_list, svg_list
    '''


def get_cached_svgs(words, img_num):
    url_list = []
    svg_list = []
    print('get svg cached!!')
    for i in range(int(img_num)):
        cached_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cached_svgs', words, f'{i}.svg')
        with open(cached_file, 'r') as f:
            svg_list.append(f.read())
    print(len(svg_list))
    return url_list, svg_list
