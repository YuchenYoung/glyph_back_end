from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from . import clip_explainability
# Create your views here.


@csrf_exempt
def getFrontData(request):
    # print("data mapping request!")
    data_unicode = request.body.decode('utf-8')
    front_data = json.loads(data_unicode)
    # print(front_data)
    data_props = front_data.get("dataProps")
    svg_list = front_data.get("svgList")
    content = front_data.get("content")
    mapper = clip_explainability.clip_main(content, data_props[1:], svg_list)
    # mapper = { "status": 'reveived'}
    response = HttpResponse(json.dumps(mapper))
    response["Access-Control-Allow-Origin"] = "*"
    return response
