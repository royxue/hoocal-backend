import tastypie
from tastypie.resources import ModelResource
from hocalen.models import Event

class EventResource(ModelResource):
    #ser = tastypie.fields.ForeignKey('')

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        allow_method = ['get']
        

#class UserResource(ModelResource):
    
