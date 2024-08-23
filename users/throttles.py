from rest_framework.throttling import UserRateThrottle


class FriendRequestThrottle(UserRateThrottle):
    scope = 'friend_request'

    def allow_request(self, request, view):
        # Call the parent method to check the rate limit
        return super().allow_request(request, view)

    def wait(self):
        # Return the wait time if the rate limit has been exceeded
        return super().wait()
