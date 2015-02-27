from django.conf.urls import patterns, url
from mypy_app import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^add_server/', views.adding_server, name='add server'),
        url(r'^edit_server/', views.edit_server, name='edit_server'),
        url(r'^monitors/', views.monitors, name='monitors'),
        url(r'^realtime/', views.realtime, name='realtime'),
        )
