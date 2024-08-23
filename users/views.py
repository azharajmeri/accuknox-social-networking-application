from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignupSerializer, LoginSerializer, UserSerializer, FriendRequestSerializer, \
    PendingFriendRequestSerializer
from .utils import custom_response
from .models import FriendRequest

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


class SendFriendRequestView(generics.CreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = {
            'sender': request.user.id,
            'receiver': request.data.get('receiver')
        }
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return custom_response(
                data=serializer.data,
                message="Friend request sent successfully.",
                status=status.HTTP_201_CREATED
            )
        return custom_response(
            data=None,
            message="Friend request failed.",
            status=status.HTTP_400_BAD_REQUEST,
            errors={"message": serializer.errors}
        )


class RespondFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        friend_request = self.get_object()
        if friend_request.receiver != request.user:
            return custom_response(
                data=None,
                message="Unauthorized action.",
                status=status.HTTP_403_FORBIDDEN,
                errors={"message": "You are not allowed to respond to this friend request."}
            )

        action = request.data.get('action')
        if action == 'accept':
            friend_request.status = 'accepted'
        elif action == 'reject':
            friend_request.status = 'rejected'
        else:
            return custom_response(
                data=None,
                message="Invalid action.",
                status=status.HTTP_400_BAD_REQUEST,
                errors={"message": "Action must be 'accept' or 'reject'."}
            )
        friend_request.save()

        return custom_response(
            data={"status": friend_request.status},
            message=f"Friend request {friend_request.status} successfully.",
            status=status.HTTP_200_OK
        )


class FriendsListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Find users who sent a friend request to the current user and it was accepted
        received_friend_request = FriendRequest.objects.filter(receiver=user, status='accepted').values_list('sender',
                                                                                                             flat=True)

        # Find users who received a friend request from the current user and it was accepted
        sent_friend_request = FriendRequest.objects.filter(sender=user, status='accepted').values_list('receiver',
                                                                                                       flat=True)

        # Combine both sets of friends
        friends_ids = list(received_friend_request) + list(sent_friend_request)

        return User.objects.filter(id__in=friends_ids)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            data=serializer.data,
            message="List of friends retrieved successfully.",
            status=status.HTTP_200_OK
        )


class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = PendingFriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(receiver=user, status='sent')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            data=serializer.data,
            message="List of pending friend requests retrieved successfully.",
            status=status.HTTP_200_OK
        )
