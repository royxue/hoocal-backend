from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from tastypie.api import Api
from hocalen.api.resources import *


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

# auth API for login
# urlpatterns += patterns('hocalen.auth.views',
#     url(r'^auth/$', 'login'),
# )

urlpatterns += patterns('',
    url(r'hoocal/', include(SelfSubscribeResource().urls))
)

# api
v1_api = Api(api_name='hoocal')
v1_api.register(EventResource())
v1_api.register(UserResource())
v1_api.register(OrgResource())
v1_api.register(CommentResource())
v1_api.register(SelfResource())
urlpatterns += patterns('',
    url(r'', include(v1_api.urls)),
)

urlpatterns += patterns('',
    url(r'', include(AuthResource().urls))
)
urlpatterns += staticfiles_urlpatterns()
    
