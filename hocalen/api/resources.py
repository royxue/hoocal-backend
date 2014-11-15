import json
from django.conf.urls import url
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse
from tastypie import fields, serializers
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest, Unauthorized
from tastypie.http import HttpBadRequest
from tastypie.resources import ModelResource
from tastypie.utils.urls import trailing_slash
from hocalen.api.utils import HoocalApiKeyAuthentication, SelfAuthorization, SelfSetResourceAuthorization
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

    def options_list(self, request, **kwargs):
        str_list_allowed_methods = ' '.join(self.list_allowed_methods).upper()
        return HttpResponse("Allow: %s" % str_list_allowed_methods)

    def options_detail(self, request, **kwargs):
        str_detail_allowed_methods = ' '.join(self.detail_allowed_methods).upper()
        return HttpResponse("Allow: %s" % str_detail_allowed_methods)


class EventResource(HoocalBaseResource):

    created_by = fields.ForeignKey('hocalen.api.resources.UserResource', 'created_by')

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        allowed_methods = ['get', 'options']
        authentication = HoocalApiKeyAuthentication()
        authorization = SelfSetResourceAuthorization('subscribe_users')
        serializers = serializers.Serializer(formats=['json', 'xml'])
        filtering = {
            'title': ('icontains',),
        }


class OrgResource(HoocalBaseResource):

    owner = fields.ForeignKey('hocalen.api.resources.UserResource', 'owner')

    class Meta:
        queryset = Org.objects.all()
        resource_name = 'org'
        allowed_methods = ['get', 'post', 'put', 'options']
        authentication = HoocalApiKeyAuthentication()
        authorization = Authorization()
        filtering = {
            'name': ('icontains',),
        }
        always_return_data = True
        serializers = serializers.Serializer(formats=['json', 'xml'])


class UserResource(HoocalBaseResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['email', 'nickname']
        allowed_methods = ['get', 'post', 'patch', 'options']
        authentication = Authentication()
        authorization = Authorization()
        serializers = serializers.Serializer(formats=['json', 'xml'])

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
        allowed_methods = ['get', 'put', 'options']
        authentication = HoocalApiKeyAuthentication()
        authorization = SelfAuthorization()
        fields = ['email', 'nickname']
        always_return_data = True
        serializers = serializers.Serializer(formats=['json', 'xml'])

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
        authorization = SelfSetResourceAuthorization(self_type='subscribe_users', no_delete=False)
        filtering = {
            'name': ('icontains',),
        }
        detail_allowed_methods = ['post', 'delete', 'options']
        list_allowed_methods = ['get', 'options']
        always_return_data = True
        serializers = serializers.Serializer(formats=['json', 'xml'])

    def post_detail(self, request, **kwargs):
        field_name = self._meta.detail_uri_name # seems field_name is fixed, namely "pk"
        event_id = kwargs[field_name]
        try:
            request.user.subscribe_events.add(Event.objects.get(pk=event_id))
        except ObjectDoesNotExist:
            return HttpBadRequest()
        return HttpResponse(json.dumps({'ret': 0, 'msg': 'subscribe ok'}))

    def delete_detail(self, request, **kwargs):
        field_name = self._meta.detail_uri_name # seems field_name is fixed, namely "pk"
        event_id = kwargs[field_name]
        try:
            request.user.subscribe_events.remove(Event.objects.get(pk=event_id))
        except ObjectDoesNotExist:
            return HttpBadRequest()
        return HttpResponse(json.dumps({'ret': 0, 'msg': 'unsubscribe ok'}))


class SelfGroupResource(HoocalBaseResource):

    class Meta:
        queryset = Org.objects.all()
        resource_name = 'self/group'
        authentication = HoocalApiKeyAuthentication()
        authorization = SelfSetResourceAuthorization(self_type='owner', no_delete=False)





