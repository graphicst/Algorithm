from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_graph', views.new_graph, name='new_graph'),
]
