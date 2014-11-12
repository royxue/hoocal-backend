from django.contrib.auth.hashers import make_password
import tastypie
from tastypie.authentication import BasicAuthentication, Authentication, ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from hocalen.models import Event, User
from django.utils.translation import ugettext as _


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
    user = tastypie.fields.ForeignKey('UserResource', 'user')

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        allowed_methods = ['get']


class UserResource(HoocalBaseResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['email', 'username']
        allowed_methods = ['get', 'post', 'patch']
        authentication = ApiKeyAuthentication()
        authorization = Authorization()

    def validate_password(self, password):
        if not password:
            raise ValueError(_("Password must be set"))
        elif len(password) < 6:
            raise ValueError(_("The length of password must be longer than 6"))

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



