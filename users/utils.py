from rest_framework.response import Response


def custom_response(data=None, message="", status=200, errors=None):
    return Response({
        "message": message,
        "results": {"data": data},
        "status": status,
        "errors": errors or {"message": {}}
    }, status=status)
