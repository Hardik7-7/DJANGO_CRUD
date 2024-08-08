from rest_framework.permissions import BasePermission
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from .models import AccessToken  

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff
    

class IsValidAccessToken(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split()[1]
            try:
                access_token = AccessToken.objects.get(token=token)
                if not access_token.is_valid:
                    raise AuthenticationFailed('Token is invalid')
            except AccessToken.DoesNotExist:
                raise AuthenticationFailed('Token does not exist')
        else:
            raise AuthenticationFailed('Authorization header is missing')

        return True
