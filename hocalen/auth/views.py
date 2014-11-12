__author__ = 'eric'
import time
import random
import hashlib
import json
from django.http.response import HttpResponse
from hocalen.models import User, UserToken


def login(request):
    """
    Login status authentication is realized by TOKEN
    :param request: email, password
    :return: ret, TOKEN, expire(0 for permanent)
    """
    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    if email is not None and password is not None:
        if not __auth_login(email, password):
            ret = {'ret': -2, 'msg': 'auth fails'}
            return HttpResponse(json.dumps(ret))
        now_timestamp = int(time.time())
        rand_number = str(random.randint(1, 10000))
        token = hashlib.md5(hashlib.md5(email + str(now_timestamp)) + rand_number)
        request.session['email'] = email
        request.session['token'] = token
        ret = {'ret': 0, 'token': token, 'expire': 0}
        return HttpResponse(json.dumps(ret))
    else:
        ret = {'ret': -1, 'msg': 'email or password missing'}
        return HttpResponse(json.dumps(ret))


def __auth_login(email, password):
    if User.objects.filter(email=email, password=password).exists():
        return True
    else:
        return False


def authenticate(request):
    token = request.POST.get('token', None)
    if token is None:
        return False
    elif UserToken.objects.filter(token=token).exists():
        return True
    else:
        return False