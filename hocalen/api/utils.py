from tastypie.authentication import ApiKeyAuthentication
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