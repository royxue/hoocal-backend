from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from hocalen.api.resources import *


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

# auth API for login
urlpatterns += patterns('hocalen.auth.views',
    url(r'^auth/$', 'login'),
)

# api
v1_api = Api(api_name='hoocal')
v1_api.register(EventResource())
v1_api.register(UserResource())
v1_api.register(OrgResource())
v1_api.register(SelfResource())
urlpatterns += patterns('',
    url(r'', include(v1_api.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^test/',include('test.urls'))
    )