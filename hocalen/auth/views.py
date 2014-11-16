import json
from django.contrib.auth import authenticate
from django.http.response import HttpResponse
from tastypie.http import HttpUnauthorized, HttpBadRequest
from hocalen.models import HoocalApiKey


__author__ = 'eric'

def login(request):
    if request.method == 'OPTIONS':
        resp = HttpResponse()
        resp['Allow'] = 'POST'
        return resp
    data = json.loads(request.body)
    email = data.get('email', None)
    password = data.get('password', None)  # md5 by front-end
    user = authenticate(email=email, password=password)
    if user is not None:
        api_key = HoocalApiKey.objects.create(user=user)
        response = HttpResponse(json.dumps({'ret': 0, 'msg': 'ok'}))
        response['X-Hoocal-Token'] = api_key.key
        return response
    else:
        return HttpUnauthorized()


def logout(request):
    x_hoocal_token = request.META.get('HTTP_X_HOOCAL_TOKEN', None)
    if x_hoocal_token is None:
        return HttpBadRequest()
    else:
        try:
            api_key = HoocalApiKey.objects.get(key=x_hoocal_token, expired=False)
            api_key.expired = True
            api_key.save()
            # logout successfully, return nothing
            return HttpResponse()
        except HoocalApiKey.DoesNotExist:
            return HttpBadRequest()
