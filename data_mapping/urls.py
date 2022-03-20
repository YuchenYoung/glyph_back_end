from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.mapping_view),
    path('mul/', views.mapping_multi),
    path('similarity/', views.props_similarity)
]