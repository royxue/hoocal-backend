from django.conf.urls import patterns, include, url

from django.contrib import admin

from tastypie.api import Api
<<<<<<< HEAD:hoocal/hoocal/urls.py
from hocalen.api.resources import *


=======
#from hocalen.api.resources import EventResource
>>>>>>> 71d44f3c31e2fa97c758d64544f555f07d2fb7b2:hoocal/urls.py
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

# auth API for login
urlpatterns += patterns('',
    url(r'auth/', include('hocalen.auth.urls')),
)

# api
<<<<<<< HEAD:hoocal/hoocal/urls.py
v1_api = Api(api_name='v1')
v1_api.register(EventResource())
v1_api.register(UserResource())

urlpatterns += patterns('',
    url(r'', include(v1_api.urls)),
)
=======
#v1_api = Api(api_name='v1')
#v1_api.register(EventResource())

#urlpatterns += patterns('',
#        (r'^api/', include(v1_api.urls)),
#)
>>>>>>> 71d44f3c31e2fa97c758d64544f555f07d2fb7b2:hoocal/urls.py
