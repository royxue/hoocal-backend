from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
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