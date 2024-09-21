from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # If it's a GET request, allow unauthenticated access even with an invalid/expired token
        if request.method == 'GET':
            try:
                # Try to authenticate as normal
                return super().authenticate(request)
            except (AuthenticationFailed, InvalidToken, TokenError):
                # If the token is invalid or expired, just return None (unauthenticated access)
                return None
        else:
            # For non-GET methods, use the default behavior (authentication required)
            return super().authenticate(request)
