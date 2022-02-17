# -- coding:utf-8 --
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import sys
import platform


@csrf_exempt
def testServer(request):
    py_version = platform.python_version()
    res_str = 'server response: python version is ' + py_version + '; python.exe: ' + sys.executable
    response = HttpResponse(res_str)
    response["Access-Control-Allow-Origin"] = "*"
    return response
