from copy import deepcopy
import warnings
from django.conf.urls import url, patterns, include
from tastypie.api import Api
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from tastypie.utils.urls import trailing_slash
from hocalen.models import HoocalApiKey


class HoocalApiKeyAuthentication(ApiKeyAuthentication):
    def extract_credentials(self, request):
        if request.META.get('HTTP_X_HOOCAL_TOKEN') and request.META['HTTP_X_HOOCAL_TOKEN'].lower().startswith('apikey '):
            (auth_type, data) = request.META['HTTP_X_HOOCAL_TOKEN'].split()

            if auth_type.lower() != 'apikey':
                raise ValueError("Incorrect authorization header.")

            username, api_key = data.split(':', 1)
        else:
            # NOTICE: Here we take email as username.
            username = request.GET.get('email') or request.POST.get('email')
            api_key = request.GET.get('api_key') or request.POST.get('api_key')

        return username, api_key
    
    def get_key(self, user, api_key):
        try:
            HoocalApiKey.objects.get(user=user, key=api_key, expired=False)
        except HoocalApiKey.DoesNotExist:
            return self._unauthorized()

        return True


class SelfAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        return object_list.filter(pk=bundle.request.user.pk)

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        return bundle.obj.pk == bundle.request.user.pk

    def create_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        return Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
        return Unauthorized("Sorry, no creates.")

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.pk == bundle.request.user.pk:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.pk == bundle.request.user.pk

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


class SelfResourceAuthorization(Authorization):
    """
    Adaptive Authorization for different relationship between Resource and User
    """
    def __init__(self, self_type='user'):
        self.filter_kwargs = {}
        self.self_type = self_type

    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        self.filter_kwargs[self.self_type] = bundle.request.user
        return object_list.filter(**self.filter_kwargs)

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        return getattr(bundle.obj, self.self_type) == bundle.request.user

    def create_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        return getattr(bundle.obj, self.self_type) == bundle.request.user

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if getattr(obj, self.self_type) == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return getattr(bundle.obj, self.self_type) == bundle.request.user

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if getattr(obj, self.self_type) == bundle.request.user:
                allowed.append(obj)

        return allowed

    def delete_detail(self, object_list, bundle):
        return getattr(bundle.obj, self.self_type) == bundle.request.user


class UnsortedApi(Api):
    @property
    def urls(self):
        """
        Provides URLconf details for the ``Api`` and all registered
        ``Resources`` beneath it.
        """
        pattern_list = [
            url(r"^(?P<api_name>%s)%s$" % (self.api_name, trailing_slash()), self.wrap_view('top_level'), name="api_%s_top_level" % self.api_name),
        ]

        for name in self._registry.keys():
            self._registry[name].api_name = self.api_name
            pattern_list.append((r"^(?P<api_name>%s)/" % self.api_name, include(self._registry[name].urls)))

        urlpatterns = self.prepend_urls()

        overridden_urls = self.override_urls()
        if overridden_urls:
            warnings.warn("'override_urls' is a deprecated method & will be removed by v1.0.0. Please rename your method to ``prepend_urls``.")
            urlpatterns += overridden_urls

        urlpatterns += patterns('',
            *pattern_list
        )
        return urlpatterns
