from rest_framework import generics, status
from .serializers import SignupSerializer, LoginSerializer
from rest_framework.permissions import AllowAny
from .utils import custom_response
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class SignupView(generics.CreateAPIView):
    queryset = None
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return custom_response(
                data={"user": serializer.data, "tokens": tokens},
                message="User signed up successfully.",
                status=status.HTTP_201_CREATED
            )
        return custom_response(
            data=None,
            message="Signup failed.",
            status=status.HTTP_400_BAD_REQUEST,
            errors={"message": serializer.errors}
        )

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            if user:
                tokens = get_tokens_for_user(user)
                return custom_response(
                    data={"tokens": tokens},
                    message="User logged in successfully.",
                    status=status.HTTP_200_OK
                )
            return custom_response(
                data=None,
                message="Invalid credentials.",
                status=status.HTTP_400_BAD_REQUEST,
                errors={"message": "Authentication failed, please check your email and password."}
            )
        return custom_response(
            data=None,
            message="Login failed.",
            status=status.HTTP_400_BAD_REQUEST,
            errors={"message": serializer.errors}
        )
