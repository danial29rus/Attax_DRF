from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Participant


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Participant
        fields = ['id', 'user', 'avatar', 'gender', 'first_name', 'last_name', 'latitude', 'longitude']
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        password = user_data.pop('password', None)
        user = User.objects.create(**user_data)
        if password is not None:
            user.set_password(password)
            user.save()
        participant = Participant.objects.create(user=user, **validated_data)
        return participant


class ParticipantLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
