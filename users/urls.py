from django.urls import path
from .views import SignupView, LoginView, UserSearchView, SendFriendRequestView, RespondFriendRequestView, \
    FriendsListView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/<int:pk>/', RespondFriendRequestView.as_view(), name='respond-friend-request'),
    path('friends/', FriendsListView.as_view(), name='friends-list'),
]
