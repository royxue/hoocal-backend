import tastypie
from tastypie.resources import ModelResource
from hocalen.models import Event

class EventResource(ModelResource):
    user = tastypie.fields.ForeignKey('jiffy.api.')

    def get_list(self, request, **kwargs):


    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        allow_method = ['get']
        

class UserResource(ModelResource):

    def get
    
