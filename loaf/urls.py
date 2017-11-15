# -*- coding: UTF-8 -*-
''' 匹配 /loaf/5/  name是为了html中使用{% url name%} 匹配用，
                        作用是当 url(r'')变化时，不用改，因为name没有变化  
    {% url 'detail' question_id %}
    {% url 'loaf:detail' question_id %}
            写入namespace：loaf 得在 include()时 添加 namespace='loaf'
            如：include('loaf.urls', namespace='loaf')
    '''

from django.conf.urls import url

from . import views


urlpatterns = [
   # url(r'^$', views.index, name = 'index'),
   # url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
   # url(r'^results/(?P<question_id>[0-9]+)/$', views.results, name='results'),
    
    url(r'^$', views.IndexView.as_view(), name = 'index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^results/(?P<pk>[0-9]+)/$', views.ResultsView.as_view(), name='results'),
    
    url(r'^vote/(?P<question_id>[0-9]+)/$', views.vote, name='vote'),
    
    ]