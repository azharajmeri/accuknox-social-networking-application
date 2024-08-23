from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User, FriendRequest


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'name']

    def create(self, validated_data):
        user = User(
            email=validated_data['email'].lower(),
            name=validated_data.get('name', '').lower()
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email').lower()
        password = data.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']

    def validate(self, data):
        if data['sender'] == data['receiver']:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")
        if FriendRequest.objects.filter(sender=data['sender'], receiver=data['receiver']).exists():
            raise serializers.ValidationError("A friend request has already been sent.")
        return data
