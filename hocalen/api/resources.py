from django.conf.urls import url
from django.contrib.auth.hashers import make_password
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest
from tastypie.resources import ModelResource
from tastypie.utils.urls import trailing_slash
from hocalen.api.utils import HoocalApiKeyAuthentication, SelfAuthorization, SelfResourceAuthorization
from hocalen.models import Event, User, Org
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
 
    class Meta:
        queryset = Org.objects.all()
        resource_name = 'org'
        allowed_methods = ['get', 'post', 'put']
        authentication = HoocalApiKeyAuthentication()
        authorization = Authorization()
        filtering = {
            'name': ('icontains',),
        }
        always_return_data = True

class UserResource(HoocalBaseResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['email', 'nickname']
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
        username = data.get('nickname', None)
        self.validate_password(password)
        if not username:
            raise BadRequest(_("Nickname must be set"))
        return super(UserResource, self).obj_create(bundle, **kwargs)

    def save(self, bundle, skip_errors=False):
        password = bundle.data.get('password', None)
        if password is not None:
            self.validate_password(password)
        bundle.obj.password = make_password(password)
        return super(UserResource, self).save(bundle, skip_errors)


class SelfResource(HoocalBaseResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = "self"
        allowed_methods = ['get', 'put']
        authentication = HoocalApiKeyAuthentication()
        authorization = SelfAuthorization()
        fields = ['email', 'nickname']
        always_return_data = True

    def alter_list_data_to_serialize(self, request, data):
        result = super(SelfResource, self).alter_list_data_to_serialize(request, data)[0]
        return result

    def put_list(self, request, **kwargs):
        return self.put_detail(request, **kwargs)

    def patch_list(self, request, **kwargs):
        return self.patch_detail(request, **kwargs)

    def get_object_list(self, request):
        return super(SelfResource, self).get_object_list(request).filter(pk=request.user.pk)


class SelfSubscribeResource(HoocalBaseResource):

    class Meta:
        queryset = Event.objects.all()
        resource_name = "self/subscribe"
        authentication = HoocalApiKeyAuthentication()
        authorization = SelfResourceAuthorization(self_type='like_users')
        filtering = {
            'name': ('icontains',),
        }
        detail_allowed_methods = ['post', 'detail']
        list_allowed_methods = ['get']
        always_return_data = True

    #def post_list(self, request, **kwargs):
