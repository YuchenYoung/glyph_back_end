from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from . import image_search
# Create your views here.


@csrf_exempt
def searchImages(request):
    front_data = request.GET
    # print(front_data)
    key_words = front_data.get("keyWords")
    img_num = front_data.get("imgNum")
    print('{} ||| {}'.format(key_words, img_num))
    url_list = image_search.get_search_result(key_words, img_num)
    response = HttpResponse(json.dumps(url_list))
    response["Access-Control-Allow-Origin"] = "*"
    return response
