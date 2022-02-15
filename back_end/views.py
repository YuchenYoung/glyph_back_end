# -- coding:utf-8 --
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import ssl
import urllib.request
import sys
import platform


def processSearch(words, img_num):
    ssl._create_default_https_context = ssl._create_unverified_context
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    }
    words = "+".join(words.split(' '))
    # url = 'https://www.google.com/search?q={}&source=lnms&tbm=isch'.format(words)
    url = "https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=0%2C0&fp=detail&logid=7869003273675959011&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=0&lpn=0&st=-1&word={}&z=0&ic=&hd=&latest=&copyright=&s=undefined&se=&tab=0&width=&height=&face=undefined&istype=2&qc=&nc=&fr=&simics=&srctype=&bdtype=0&rpstart=0&rpnum=0&cs=1205005635%2C1125725152&catename=&nojc=undefined&album_id=&album_tab=&cardserver=&tabname=&pn=0&rn={}&gsm=6&1643188057337=".format(
        words, img_num)
    res_url_list = []
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    res_json_str = response.read().decode('utf-8')
    res_json_str = res_json_str.replace('\\', '\\\\')
    res_json = json.loads(res_json_str)
    res_data = res_json['data']
    for item in res_data:
        if 'middleURL' in item:
            res_url_list.append(item['middleURL'])
    return res_url_list


@csrf_exempt
def searchImages(request):
    post_content = request.GET
    key_words = post_content.get("keyWords")
    img_num = post_content.get("imgNum")
    print('{} ||| {}'.format(key_words, img_num))
    url_list = processSearch(key_words, img_num)
    # url_list = [
    #     'https://static.vecteezy.com/system/resources/thumbnails/003/694/243/small/car-icon-in-flat-style-simple-traffic-icon-free-vector.jpg',
    #     'https://media.istockphoto.com/vectors/car-flat-icon-vector-id1144092062?k=20&m=1144092062&s=170667a&w=0&h=g0l9zds27VEZA_a0QTPbpU_5QXWv5ytng2n8QJODUmk=',
    #     ]
    response = HttpResponse(json.dumps(url_list))
    response["Access-Control-Allow-Origin"] = "*"
    return response


@csrf_exempt
def testServer(request):
    py_version = platform.python_version()
    res_str = 'server response: python version is ' + py_version + '; python.exe: ' + sys.executable
    response = HttpResponse(res_str)
    response["Access-Control-Allow-Origin"] = "*"
    return response
