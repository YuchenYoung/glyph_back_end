import os
from .google_images_download import google_images_download


def save_cached_result(words, url_list):
    with open('cached_urls.txt', 'w') as f:
        for i in range(len(url_list)):
            s = str(url_list[i]).replace('[', '').replace(']', '')
            s = s.replace("'", '').replace(',', '') + '\n'
            f.write(s)


def get_cached_result(words, img_num):
    url_list = []
    print('1.get cached!!')
    cached_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cached_urls', f'{words}.txt')
    print(cached_dir)
    with open(cached_dir, 'r') as f:
        line_cnt = 0
        for line in f.readlines():
            url_list.append(line.strip())
            line_cnt += 1
            if line_cnt >= int(img_num):
                break
    return url_list


def get_google_result(words, img_num):
    response = google_images_download.googleimagesdownload()  
    arguments = {"keywords": f"{words} icon", "limit": img_num, "print_urls": True, "no_download": True} 
    paths = response.download(arguments) 
    url_list = paths[0][words]
    # print(paths) 
    print(len(url_list))
    print(url_list)
    # save_cached_result(words, url_list)
    return url_list


def get_search_result(words, img_num):
    # return get_google_result(words, img_num)
    return get_cached_result(words, img_num)
