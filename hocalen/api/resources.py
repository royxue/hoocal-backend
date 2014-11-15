import json
from django import http
from django.conf.urls import url
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse
from tastypie import fields, serializers
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest, Unauthorized, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpAccepted, HttpCreated
from tastypie.resources import ModelResource, convert_post_to_put
from tastypie.utils.urls import trailing_slash
from hocalen.models import Event, User, Org, Comment
from hocalen.api.utils import HoocalApiKeyAuthentication, SelfAuthorization, SelfSetResourceAuthorization, \
    event_authorization
from django.utils.translation import ugettext as _
from tastypie.constants import ALL_WITH_RELATIONS, ALL
import calendar
import datetime

class HoocalBaseResource(ModelResource):
    """
    Base ModelResource for hoocal REST
    rewrite some of the methods to fit Hoocal's API
    """

    pass


class UserResource(HoocalBaseResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['email', 'nickname', 'id']
        allowed_methods = ['get', 'post', 'patch', 'options']
        authentication = Authentication()
        authorization = Authorization()
        serializers = serializers.Serializer(formats=['json', 'xml'])
        filtering = {
                'email': ALL,
                'id': ALL,
                }
        always_return_data = True

    def validate_password(self, password):
        if not password:
            raise BadRequest(_("Password must be set"))
        elif len(password) < 6:
            raise BadRequest(_("The length of password must be longer than 6"))

    def obj_create(self, bundle, **kwargs):
        data = bundle.data
        email = data.get('email', None)
        password = data.get('password', None)
        nickname = data.get('nickname', None)
        self.validate_password(password)
        if not nickname and not email:
            raise BadRequest(json.dumps({'ret': -1, 'msg': _("Nickname and Email must be set")}))
        elif User.objects.filter(email=email).exists():
            raise BadRequest(json.dumps({'ret': -2, 'msg': _("Email must duplicated")}))
        return super(UserResource, self).obj_create(bundle, **kwargs)

    def save(self, bundle, skip_errors=False):
        password = bundle.data.get('password', None)
        if password is not None:
            self.validate_password(password)
        bundle.obj.password = make_password(password)
        return super(UserResource, self).save(bundle, skip_errors)


class EventResource(HoocalBaseResource):
    created_by = fields.ForeignKey('hocalen.api.resources.UserResource', 'created_by')
    org = fields.ForeignKey('hocalen.api.resources.OrgResource', 'org')
    like_users = fields.ManyToManyField('hocalen.api.resources.UserResource', 'like_users')

    def dehydrate(self, bundle):
        bundle.data['start_time'] = timestamp_of(bundle.data['start_time'])
        bundle.data['end_time'] = timestamp_of(bundle.data['end_time'])
        bundle.data['created_at'] = timestamp_of(bundle.data['created_at'])
        bundle.data['last_modified'] = timestamp_of(bundle.data['last_modified'])
        return bundle

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        allowed_methods = ['get', 'post', 'put', 'options']
        authentication = HoocalApiKeyAuthentication()
        authorization = Authorization()
        serializers = serializers.Serializer(formats=['json', 'xml']) 
        filtering = {
            'title': ('icontains',),
            'created_by': ALL_WITH_RELATIONS,
            'org': ALL_WITH_RELATIONS,
            'id': ALL,
        }
        always_return_data = True

    def object_create(self, bundle, **kwargs):
        user = bundle.request.user
        start_time = datetime.datetime.fromtimestamp(bundle.data['start_time'])
        end_time = datetime.datetime.fromtimestamp(bundle.data['end_time'])
        if bundle['org']:
            org = Org.objects().filter(name=bundle['org'])
        return super(EventResource, self).obj_create(bundle, created_by=user, org=org, start_time=start_time, end_time=end_time, **kwargs)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<%s>\w[\w/-]*)/like%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('dispatch_like')),
        ]

    def dispatch_like(self, request, **kwargs):
        request_method = self.method_check(request, allowed=['post', 'delete'])
        method = getattr(self, request_method+'_like')
        if method is None:
            raise ImmediateHttpResponse(response=http.HttpNotImplemented())

        self.is_authenticated(request)
        self.throttle_check(request)

        # All clear. Process the request.
        request = convert_post_to_put(request)
        response = method(request, **kwargs)

        # Add the throttled request.
        self.log_throttled_access(request)

        if not isinstance(response, HttpResponse):
            return http.HttpNoContent()

        return response

    def post_like(self, request, **kwargs):
        event_id = kwargs[self._meta.detail_uri_name]
        try:
            event = Event.objects.get(pk=event_id)
        except ObjectDoesNotExist:
            raise BadRequest("Event does not exist")
        event.like_users.add(request.user)
        return HttpCreated(json.dumps({'ret': 0, 'msg': 'ok'}))

    def delete_like(self, request ,**kwargs):
        event_id = kwargs[self._meta.detail_uri_name]
        try:
            event = Event.objects.get(pk=event_id)
        except ObjectDoesNotExist:
            raise BadRequest("Event does not exist")
        event.like_users.remove(request.user)
        return HttpCreated(json.dumps({'ret': 0, 'msg': 'ok'}))

        
class OrgResource(HoocalBaseResource):
    owner = fields.ForeignKey('hocalen.api.resources.UserResource', 'owner')
    members = fields.ManyToManyField('hocalen.api.resources.UserResource', 'members')
    followers = fields.ManyToManyField('hocalen.api.resources.UserResource', 'followers')

    class Meta:
        queryset = Org.objects.all()
        resource_name = 'org'
        allowed_methods = ['get', 'post', 'put', 'options']
        authentication = HoocalApiKeyAuthentication()
        authorization = Authorization()
        serializers = serializers.Serializer(formats=['json', 'xml'])
        filtering = {
            'name': ('icontains',),
            'owner': ALL_WITH_RELATIONS,
            'members': ALL_WITH_RELATIONS,
            'id': ALL,
        }
        always_return_data = True

    def object_create(self, bundle, **kwargs):
        user = bundle.request.user
        return super(OrgResource, self).obj_create(bundle, owner=user, **kwargs)

    def __authorized(self, request, **kwargs):
        return Org.objects.filter(pk=kwargs[self._meta.detail_uri_name], owner=request.user).exists()

    def put_detail(self, request, **kwargs):
        if self.__authorized(request):
            super(OrgResource, self).put_detail(request, **kwargs)
        else:
            raise Unauthorized()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<%s>\w[\w/-]*)/member%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('get_member')),
            url(r"^(?P<resource_name>%s)/(?P<%s>\w[\w/-]*)/member/(?P<user_id>\d+)%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('dispatch_member')),
            url(r"^(?P<resource_name>%s)/(?P<%s>\w[\w/-]*)/event%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('get_event')),
        ]

    def get_member(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        if not self.__authorized(request, **kwargs):
            raise Unauthorized()
        org = Org.objects.get(pk=kwargs[self._meta.detail_uri_name])
        applicable_filters = UserResource().build_filters(request.GET.copy() if hasattr(request, 'GET') else None)
        objects = org.members.filter(**applicable_filters)
        sorted_objects = self.apply_sorting(objects, options=request.GET)
        paginator = self._meta.paginator_class(request.GET, sorted_objects)
        to_be_serialized = paginator.page()
        bundles = []

        user_resource = UserResource()
        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = user_resource.build_bundle(obj=obj, request=request)
            bundles.append(user_resource.full_dehydrate(bundle, for_list=True))

        to_be_serialized[self._meta.collection_name] = bundles
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def post_member(self, request, **kwargs):
        if not self.__authorized(request, **kwargs):
            raise Unauthorized()
        org = Org.objects.get(pk=kwargs[self._meta.detail_uri_name])
        try:
            user = User.objects.get(pk=int(kwargs['user_id']))
            org.members.add(user)
            return HttpCreated(json.dumps({'ret': 0, 'msg': 'ok'}))
        except ObjectDoesNotExist:
            raise BadRequest("User does not exist")

    def delete_member(self, request, **kwargs):
        if not self.__authorized(request, **kwargs):
            raise Unauthorized()
        org = Org.objects.get(pk=kwargs[self._meta.detail_uri_name])
        try:
            user = User.objects.get(pk=int(kwargs['user_id']))
            org.members.remove(user)
            return HttpAccepted(json.dumps({'ret': 0, 'msg': 'ok'}))
        except ObjectDoesNotExist:
            raise BadRequest("User does not exist")

    def dispatch_member(self, request, **kwargs):
        request_method = self.method_check(request, allowed=['post', 'delete'])
        method = getattr(self, request_method+'_member')
        if method is None:
            raise ImmediateHttpResponse(response=http.HttpNotImplemented())

        self.is_authenticated(request)
        self.throttle_check(request)

        # All clear. Process the request.
        request = convert_post_to_put(request)
        response = method(request, **kwargs)

        # Add the throttled request.
        self.log_throttled_access(request)

        if not isinstance(response, HttpResponse):
            return http.HttpNoContent()

        return response

    def get_event(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        try:
            org = Org.objects.get(pk=kwargs[self._meta.detail_uri_name])
        except ObjectDoesNotExist:
            raise BadRequest("Org Does not exist")
        objects = org.events.all()
        sorted_objects = self.apply_sorting(objects, options=request.GET)
        paginator = self._meta.paginator_class(request.GET, sorted_objects)
        to_be_serialized = paginator.page()
        bundles = []

        event_resource = EventResource()
        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = event_resource.build_bundle(obj=obj, request=request)
            bundles.append(event_resource.full_dehydrate(bundle, for_list=True))

        to_be_serialized[self._meta.collection_name] = bundles
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)



class CommentResource(HoocalBaseResource):
    event = fields.ForeignKey('hocalen.api.resources.EventResource', 'event')
    user = fields.ForeignKey('hocalen.api.resources.UserResource', 'user')  
    reply_to = fields.ForeignKey('hocalen.api.resources.UserResource', 'reply_to')

    class Meta:
        queryset = Comment.objects.all()
        resource_name = "comment"
        allowed_methods = ['get', 'post']
        authentication = HoocalApiKeyAuthentication()
        authorization = Authorization()
        filtering = {
                'event': ALL_WITH_RELATIONS,
                'user': ALL_WITH_RELATIONS,
                'id': ALL,
                }
        always_return_data = True

    def obj_create(self, bundle, **kwargs):
        user = bundle.request.user
        return super(CommentResource,self).obj_create(bundle, user=user, **kwargs)


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


def timestamp_of(d):
  if hasattr(d, 'isoformat'):
    return calendar.timegm(d.utctimetuple())
  return None
