from django.conf.urls import patterns, include, url

from django.contrib import admin

from tastypie.api import Api
from hocalen.api.resources import *


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

# auth API for login
urlpatterns += patterns('',
    url(r'auth/', include('hocalen.auth.urls')),
)

# api
v1_api = Api(api_name='v1')
v1_api.register(EventResource())
v1_api.register(UserResource())

urlpatterns += patterns('',
    url(r'', include(v1_api.urls)),
)
