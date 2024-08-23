from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination

from .serializers import SignupSerializer, LoginSerializer, UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .utils import custom_response
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


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


class UserSearchPagination(PageNumberPagination):
    page_size = 10


class UserSearchView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserSearchPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        if query is None:
            return User.objects.none()

        # Search by exact email match
        if User.objects.filter(email__iexact=query).exists():
            return User.objects.filter(email__iexact=query)

        # Search by name (case-insensitive)
        return User.objects.filter(name__icontains=query)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            data=serializer.data,
            message="User search results.",
            status=status.HTTP_200_OK
        )
