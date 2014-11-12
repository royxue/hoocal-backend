__author__ = 'eric'

from django.conf.urls import url, patterns

urlpatterns = patterns('hocalen.auth.views',
    url(r'^/$', 'login'),
)