from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from . import clip_explainability
from . import data_mapping
# Create your views here.


@csrf_exempt
def props_similarity(request):
    print("now get similarity!")
    data_unicode = request.body.decode('utf-8')
    front_data = json.loads(data_unicode)
    props = front_data.get("dataProps")
    data_types = front_data.get("dataTypes")
    theme = front_data.get("theme")
    groups = front_data.get("groups")

    props, similarity, dic_similarity = data_mapping.get_similarity(theme, props[1:], groups, data_types);
    res_dic = {
        'props': props,
        'similarity': similarity,
        'dic': dic_similarity
    }
    response = HttpResponse(json.dumps(res_dic))
    response["Access-Control-Allow-Origin"] = "*"
    return response


@csrf_exempt
def mapping_view(request):
    # print("data mapping request!")
    data_unicode = request.body.decode('utf-8')
    front_data = json.loads(data_unicode)
    # print(front_data)
    data_props = front_data.get("dataProps")
    # data_types = front_data.get("dataTypes")
    svg_list = front_data.get("svgList")
    content = front_data.get("content")
    # mapper = data_mapping.data_mapping_km(content, data_props[1:], [], svg_list)
    mapper = data_mapping.data_mapping_main(content, data_props[1:], [], svg_list)
    # mapper = { "status": 'reveived'}
    response = HttpResponse(json.dumps(mapper))
    response["Access-Control-Allow-Origin"] = "*"
    return response


@csrf_exempt
def mapping_multi(request):
    # print("data mapping request!")
    data_unicode = request.body.decode('utf-8')
    front_data = json.loads(data_unicode)
    data_props = front_data.get("dataProps")
    similarity = front_data.get("similarity")
    data_types = front_data.get("dataTypes")
    svgs_list = front_data.get("svgsList")
    content = front_data.get("content")
    groups = front_data.get("groups")
    mapped = front_data.get("mapped")
    # mapper = data_mapping.data_mapping_km(content, data_props[1:], [], svg_list)
    best_img, score, mapper, scores, mappers, times  = data_mapping.data_mapping_multi(content, data_props, similarity, groups, data_types, svgs_list, mapped)
    # mapper = { "status": 'reveived'}
    res = {
        "best_img": best_img, 
        "score": score,
        "mapper": mapper,
        "scores": scores,
        "mappers": mappers,
        "times": times
    }
    response = HttpResponse(json.dumps(res))
    response["Access-Control-Allow-Origin"] = "*"
    return response
