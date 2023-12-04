from re import sub
from rest_framework.authtoken.models import Token

class OrganizationMiddleware(object):
  
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        header_token = request.headers.get('Authorization', None)
        if header_token is not None:
            try:
                token = sub('Token ', '', header_token)
                token_obj = Token.objects.get(key = token)
            except Token.DoesNotExist:
                request.user = None
                return None
        else:
            request.user = None
            return None
