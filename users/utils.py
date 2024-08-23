from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


def custom_response(data=None, message="", status=200, errors=None):
    return Response({
        "message": message,
        "results": {"data": data},
        "status": status,
        "errors": errors or {"message": {}}
    }, status=status)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
