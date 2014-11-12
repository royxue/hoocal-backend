from django.contrib.auth.hashers import make_password
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest
from tastypie.resources import ModelResource
from hocalen.api.utils import HoocalApiKeyAuthentication
from hocalen.models import Event, User, Org
from django.utils.translation import ugettext as _
from tastypie.models import create_api_key
from django.db import models


# Every time a new user is created, a related api key is generated
models.signals.post_save.connect(create_api_key, sender=User)


class HoocalBaseResource(ModelResource):
    """
    Base ModelResource for hoocal REST
    rewrite some of the methods to fit Hoocal's API
    """

    def alter_list_data_to_serialize(self, request, data):
        """
        Remove 'meta' key which exist in the origin method of ModelResource
        """
        return data['objects']


class EventResource(HoocalBaseResource):
    user = fields.ForeignKey('hocalen.api.resources.UserResource', 'user')

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        allowed_methods = ['get']
        authentication = HoocalApiKeyAuthentication()
        authorization = Authorization()
        filtering = {
            'title': ('icontains',),
        }


class OrgResource(HoocalBaseResource):

    owner = fields.ForeignKey('hocalen.api.resources.UserResource', 'owner')
    class Meta:
        queryset = Org.objects.all()
        resource_name = 'org'
        allowed_methods = ['get', 'post', 'put']
        authentication = HoocalApiKeyAuthentication()
        authorization = Authorization()
        filtering = {
            'name': ('icontains',),
        }

class UserResource(HoocalBaseResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['email', 'username']
        allowed_methods = ['get', 'post', 'patch']
        authentication = Authentication()
        authorization = Authorization()

    def validate_password(self, password):
        if not password:
            raise BadRequest(_("Password must be set"))
        elif len(password) < 6:
            raise BadRequest(_("The length of password must be longer than 6"))

    def obj_create(self, bundle, **kwargs):
        data = bundle.data
        password = data.get('password', None)
        username = data.get('username', None)
        self.validate_password(password)
        if not username:
            raise ValueError(_("Username must be set"))
        return super(UserResource, self).obj_create(bundle, **kwargs)

    def save(self, bundle, skip_errors=False):
        password = bundle.data.get('password', None)
        if password is not None:
            self.validate_password(password)
        bundle.obj.password = make_password(password)
        return super(UserResource, self).save(bundle, skip_errors)
