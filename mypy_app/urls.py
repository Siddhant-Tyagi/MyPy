from django.conf.urls import patterns, url
from mypy_app import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^about/', views.about, name='about'),
        url(r'^add_server/', views.adding_server, name='add server'),
        )
