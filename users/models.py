from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models
from django.utils import timezone

from users.managers import CustomUserManager


class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10,
                              choices=[('sent', 'Sent'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
                              default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"

    @classmethod
    def can_send_request(cls, user):
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests = cls.objects.filter(sender=user, created_at__gte=one_minute_ago)
        return recent_requests.count() < 3
