from cups import HTTP_OK
import json
from django.contrib.auth import authenticate
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from tastypie.http import HttpUnauthorized, HttpBadRequest
from hocalen.models import HoocalApiKey


__author__ = 'eric'

def login(request):

    email = request.POST.get('email', None)
    password = request.POST.get('password', None)  # md5 by front-end
    user = authenticate(email=email, password=password)
    if user is not None:
        api_key = HoocalApiKey.objects.create(user=user)
        response = HttpResponse(json.dumps({'ret': 0, 'msg': 'ok'}))
        response['X-Hoocal-Token'] = api_key.key
        response["Access-Control-Allow-Origin"] = "*"
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

