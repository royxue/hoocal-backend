import tastypie
from tastypie.resources import ModelResource
from hocalen.models import Event, User


class EventResource(ModelResource):
    user = tastypie.fields.ForeignKey('jiffy.api.')

    def get_list(self, request, **kwargs):
        return super(EventResource, self).get_list(request, kwargs)

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        allow_method = ['get']
        

class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        allowed_method = ['get', 'post']

    def get_list(self, request, **kwargs):
        return super(UserResource, self).get_list(request, kwargs)
